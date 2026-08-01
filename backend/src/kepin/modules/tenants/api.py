from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import (
    ListParams,
    PeriodParams,
    TenantContext,
    get_session,
    get_tenant_context,
    get_tenant_membership,
)
from kepin.api.errors import NotFoundError
from kepin.core.money import money_str
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.time import resolve_period
from kepin.db.models import (
    Account,
    BankAccount,
    Branch,
    Invoice,
    JournalEntry,
    JournalLine,
    Membership,
    Product,
    StockBalance,
    StockMovement,
    Tenant,
    Transaction,
    User,
)

router = APIRouter(tags=["Tenants"])


class TenantContextResponse(ApiSchema):
    tenant: dict
    branches: list[dict] = []
    active_branch_id: str | None = None
    user: dict | None = None
    role: str | None = None
    permissions: list[str] = []
    authorization_enabled: bool = True


class DashboardResponse(ApiSchema):
    period: dict
    metrics: dict
    cash_flow: list[dict] = []
    expense_composition: list[dict] = []
    alerts: list[dict] = []
    insights: list[dict] = []
    recent_transactions: list[dict] = []


@router.get("/context", response_model=TenantContextResponse)
async def get_context(
    tenant: TenantContext = Depends(get_tenant_context),
    membership: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Tenant).where(Tenant.id == tenant.id))
    t = result.scalar_one_or_none()
    branches_result = await session.execute(
        select(Branch).where(Branch.tenant_id == tenant.id, Branch.status == "active")
    )
    branches = branches_result.scalars().all()

    user = (await session.execute(select(User).where(User.id == membership.user_id))).scalar_one_or_none()

    return TenantContextResponse(
        tenant={
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "planCode": t.plan_code,
            "status": t.status,
            "timezone": t.timezone,
            "currency": t.currency,
            "sector": t.sector,
        },
        branches=[{
            "id": str(b.id),
            "code": b.code,
            "name": b.name,
            "isMain": b.is_main,
        } for b in branches],
        role=membership.role_name,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        } if user else None,
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    tenant: TenantContext = Depends(get_tenant_context),
    membership: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    start, end = resolve_period(params.preset, params.start_date, params.end_date)
    tid = tenant.id

    income_stmt = select(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).where(
        Transaction.tenant_id == tid,
        Transaction.type == "income",
        Transaction.status == "posted",
        Transaction.transaction_date.between(start, end),
    )
    income = (await session.execute(income_stmt)).scalar() or Decimal("0")

    expense_stmt = select(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).where(
        Transaction.tenant_id == tid,
        Transaction.type == "expense",
        Transaction.status == "posted",
        Transaction.transaction_date.between(start, end),
    )
    expense = (await session.execute(expense_stmt)).scalar() or Decimal("0")

    gross_profit = income - expense

    bank_account_ids = (
        await session.execute(
            select(BankAccount.account_id).where(BankAccount.tenant_id == tid)
        )
    ).scalars().all()
    cash_stmt = (
        select(
            func.coalesce(func.sum(JournalLine.debit - JournalLine.credit), 0)
        )
        .select_from(JournalLine)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, Account.id == JournalLine.account_id)
        .where(
            JournalEntry.tenant_id == tid,
            JournalEntry.status.in_(("posted", "reversed")),
            Account.tenant_id == tid,
            Account.type == "asset",
            or_(
                Account.name.ilike("%kas%"),
                Account.code.in_(["1-1002", "1-1003"]),
                Account.id.in_(bank_account_ids),
            ),
        )
    )
    cash_balance = (await session.execute(cash_stmt)).scalar() or Decimal("0")

    metrics = {
        "income": money_str(income),
        "expense": money_str(expense),
        "grossProfit": money_str(gross_profit),
        "cashBalance": money_str(cash_balance),
    }

    cash_flow = []
    cf_stmt = text("""
        SELECT d::date AS dt,
               COALESCE(SUM(CASE WHEN t.type = 'income' AND t.status = 'posted' THEN t.amount ELSE 0 END), 0) AS inc,
               COALESCE(SUM(CASE WHEN t.type = 'expense' AND t.status = 'posted' THEN t.amount ELSE 0 END), 0) AS exp
        FROM generate_series(:start, :end, '1 day'::interval) d
        LEFT JOIN transactions t ON t.transaction_date = d::date AND t.tenant_id = :tid
        GROUP BY d::date
        ORDER BY d::date
    """)
    cf_rows = (await session.execute(cf_stmt, {"start": start, "end": end, "tid": tid})).all()
    for dt, inc, exp in cf_rows:
        cash_flow.append({"date": str(dt), "income": money_str(inc), "expense": money_str(exp)})

    expense_composition = []
    ec_stmt = (
        select(
            Account.id,
            Account.name,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .join(Transaction, Transaction.account_id == Account.id)
        .where(
            Account.tenant_id == tid,
            Account.type == "expense",
            Transaction.tenant_id == tid,
            Transaction.status == "posted",
            Transaction.transaction_date.between(start, end),
        )
        .group_by(Account.id, Account.name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    ec_rows = (await session.execute(ec_stmt)).all()
    total_expense = expense or Decimal("1")
    for acc_id, acc_name, amt in ec_rows:
        expense_composition.append({
            "accountId": str(acc_id),
            "accountName": acc_name,
            "amount": money_str(amt),
            "percentage": round(float(amt) / float(total_expense) * 100, 1),
        })

    alerts = []
    overdue_stmt = select(func.count(Invoice.id)).where(
        Invoice.tenant_id == tid,
        Invoice.status == "overdue",
    )
    overdue_count = (await session.execute(overdue_stmt)).scalar() or 0
    if overdue_count > 0:
        alerts.append({
            "type": "warning",
            "message": f"{overdue_count} faktur telah melewati jatuh tempo",
        })

    low_stock_stmt = select(func.count(StockBalance.tenant_id)).where(
        StockBalance.tenant_id == tid,
        StockBalance.quantity <= 10,
    )
    low_stock_count = (await session.execute(low_stock_stmt)).scalar() or 0
    if low_stock_count > 0:
        alerts.append({
            "type": "warning",
            "message": f"{low_stock_count} produk memiliki stok menipis",
        })

    insights = []
    if income > expense:
        insights.append({
            "title": "Profit Positif",
            "description": "Pendapatan melebihi biaya pada periode ini",
            "impact": "positive",
            "horizon": "short_term",
            "confidence": "high",
            "factors": ["pendapatan tinggi", "biaya terkendali"],
        })
    else:
        insights.append({
            "title": "Perhatian Diperlukan",
            "description": "Biaya melebihi pendapatan pada periode ini",
            "impact": "negative",
            "horizon": "short_term",
            "confidence": "high",
            "factors": ["biaya operasional tinggi"],
        })
    if cash_balance > Decimal("0"):
        insights.append({
            "title": "Likuiditas Sehat",
            "description": "Saldo kas/bank positif, operasional aman",
            "impact": "positive",
            "horizon": "medium_term",
            "confidence": "medium",
            "factors": ["saldo kas positif"],
        })
    else:
        insights.append({
            "title": "Likuiditas Rendah",
            "description": "Saldo kas/bank rendah, perhatikan arus kas",
            "impact": "negative",
            "horizon": "short_term",
            "confidence": "medium",
            "factors": ["saldo kas minim"],
        })

    recent_transactions = []
    rt_stmt = (
        select(Transaction)
        .where(Transaction.tenant_id == tid)
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .limit(5)
    )
    rt_rows = (await session.execute(rt_stmt)).scalars().all()
    for txn in rt_rows:
        recent_transactions.append({
            "id": str(txn.id),
            "date": txn.transaction_date.isoformat() if txn.transaction_date else None,
            "description": txn.description or "",
            "amount": money_str(txn.amount or Decimal("0")),
            "type": txn.type or "",
            "status": txn.status or "",
        })

    return DashboardResponse(
        period={"startDate": start.isoformat(), "endDate": end.isoformat(), "timezone": "UTC"},
        metrics=metrics,
        cash_flow=cash_flow,
        expense_composition=expense_composition,
        alerts=alerts,
        insights=insights,
        recent_transactions=recent_transactions,
    )
