from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from kepin.api.dependencies import get_session, TenantContext, get_tenant_context, ListParams, PeriodParams
from kepin.api.errors import NotFoundError, ConflictError, ValidationError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, money_str
from kepin.core.time import resolve_period
from kepin.db.models import (
    Tenant,
    Branch,
    Account,
    Transaction,
    JournalLine,
    Product,
    StockBalance,
    Invoice,
    Membership,
    User,
    StockMovement,
)


router = APIRouter(tags=["Tenants"])  # no prefix - lives at /tenants/{tenantSlug}/ level


# ── Schemas ──────────────────────────────────────────────────────────


class TenantContextResponse(ApiSchema):
    tenant: dict
    branches: list[dict] = []
    active_branch_id: str | None = None
    user: dict | None = None
    permissions: list[str] = []
    authorization_enabled: bool = False


class DashboardResponse(ApiSchema):
    period: dict
    metrics: dict
    cash_flow: list[dict] = []
    expense_composition: list[dict] = []
    alerts: list[dict] = []
    insights: list[dict] = []
    recent_transactions: list[dict] = []


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/context", response_model=TenantContextResponse)
async def get_context(
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Tenant).where(Tenant.id == tenant.id))
    t = result.scalar_one_or_none()
    if not t:
        raise NotFoundError(message="Tenant tidak ditemukan")

    branches_result = await session.execute(
        select(Branch).where(Branch.tenant_id == tenant.id, Branch.status == "active")
    )
    branches = branches_result.scalars().all()

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
        active_branch_id=None,
        user=None,
        permissions=[],
        authorization_enabled=False,
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    start, end = resolve_period(params.preset, params.start_date, params.end_date)
    tenant_id = tenant.id

    # ── metrics: income & expense ──
    income_acc_subq = (
        select(Account.id)
        .where(Account.tenant_id == tenant_id, Account.type == "income")
        .subquery()
    )
    expense_acc_subq = (
        select(Account.id)
        .where(Account.tenant_id == tenant_id, Account.type == "expense")
        .subquery()
    )

    income_stmt = select(
        func.coalesce(func.sum(TransactionLine.amount), 0)
    ).where(
        TransactionLine.account_id.in_(select(income_acc_subq.c.id)),
        TransactionLine.transaction_id == Transaction.id,
        Transaction.tenant_id == tenant_id,
        Transaction.date.between(start, end),
    )
    income = (await session.execute(income_stmt)).scalar() or Decimal("0")

    expense_stmt = select(
        func.coalesce(func.sum(TransactionLine.amount), 0)
    ).where(
        TransactionLine.account_id.in_(select(expense_acc_subq.c.id)),
        TransactionLine.transaction_id == Transaction.id,
        Transaction.tenant_id == tenant_id,
        Transaction.date.between(start, end),
    )
    expense = (await session.execute(expense_stmt)).scalar() or Decimal("0")

    gross_profit = income - expense

    # ── cashBalance: cash/bank account balances ──
    cash_acc_subq = (
        select(Account.id)
        .where(Account.tenant_id == tenant_id, Account.type.in_(["cash", "bank"]))
        .subquery()
    )
    balance_stmt = select(
        func.coalesce(func.sum(Account.balance), 0)
    ).where(
        Account.id.in_(select(cash_acc_subq.c.id)),
        Account.tenant_id == tenant_id,
    )
    cash_balance = (await session.execute(balance_stmt)).scalar() or Decimal("0")

    metrics = {
        "income": money_str(income),
        "expense": money_str(expense),
        "grossProfit": money_str(gross_profit),
        "cashBalance": money_str(cash_balance),
    }

    # ── cashFlow: daily income/expense ──
    cash_flow = []
    cf_stmt = text(
        """
        SELECT d::date AS dt,
               COALESCE(SUM(CASE WHEN a.type IN ('income') THEN tl.amount ELSE 0 END), 0) AS inc,
               COALESCE(SUM(CASE WHEN a.type IN ('expense') THEN tl.amount ELSE 0 END), 0) AS exp
        FROM generate_series(:start, :end, '1 day'::interval) d
        LEFT JOIN transactions txn ON txn.date = d::date AND txn.tenant_id = :tenant_id
        LEFT JOIN transaction_lines tl ON tl.transaction_id = txn.id
        LEFT JOIN accounts a ON a.id = tl.account_id
        GROUP BY d::date
        ORDER BY d::date
        """
    )
    cf_rows = (await session.execute(cf_stmt, {"start": start, "end": end, "tenant_id": tenant_id})).all()
    for dt, inc, exp in cf_rows:
        cash_flow.append({
            "date": str(dt),
            "income": money_str(inc),
            "expense": money_str(exp),
        })

    # ── expenseComposition: expense by account ──
    expense_composition = []
    ec_stmt = (
        select(
            Account.id,
            Account.name,
            func.coalesce(func.sum(TransactionLine.amount), 0),
        )
        .join(TransactionLine, TransactionLine.account_id == Account.id)
        .join(Transaction, TransactionLine.transaction_id == Transaction.id)
        .where(
            Account.tenant_id == tenant_id,
            Account.type == "expense",
            Transaction.tenant_id == tenant_id,
            Transaction.date.between(start, end),
        )
        .group_by(Account.id, Account.name)
        .order_by(func.sum(TransactionLine.amount).desc())
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

    # ── alerts ──
    alerts = []

    overdue_stmt = select(func.count(Invoice.id)).where(
        Invoice.tenant_id == tenant_id,
        Invoice.status == "overdue",
    )
    overdue_count = (await session.execute(overdue_stmt)).scalar() or 0
    if overdue_count > 0:
        alerts.append({
            "type": "warning",
            "message": f"{overdue_count} faktur telah melewati jatuh tempo",
        })

    low_stock_stmt = select(func.count(StockItem.id)).where(
        StockItem.tenant_id == tenant_id,
        StockItem.quantity <= StockItem.min_quantity,
    )
    low_stock_count = (await session.execute(low_stock_stmt)).scalar() or 0
    if low_stock_count > 0:
        alerts.append({
            "type": "warning",
            "message": f"{low_stock_count} produk memiliki stok menipis",
        })

    # ── insights ──
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

    # ── recentTransactions: last 5 ──
    recent_transactions = []
    rt_stmt = (
        select(Transaction)
        .where(Transaction.tenant_id == tenant_id)
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .limit(5)
    )
    rt_rows = (await session.execute(rt_stmt)).scalars().all()
    for txn in rt_rows:
        recent_transactions.append({
            "id": str(txn.id),
            "date": txn.date.isoformat() if txn.date else None,
            "description": txn.description or "",
            "amount": money_str(txn.total_amount or Decimal("0")),
            "type": txn.transaction_type or "",
            "status": txn.status or "",
        })

    return DashboardResponse(
        period={
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "timezone": "UTC",
        },
        metrics=metrics,
        cash_flow=cash_flow,
        expense_composition=expense_composition,
        alerts=alerts,
        insights=insights,
        recent_transactions=recent_transactions,
    )
