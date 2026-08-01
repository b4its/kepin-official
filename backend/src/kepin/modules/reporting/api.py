from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import and_, case, func, literal_column, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import (
    PeriodParams,
    TenantContext,
    get_session,
    get_tenant_context,
    get_tenant_membership,
)
from kepin.api.errors import NotFoundError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.time import resolve_period
from kepin.db.models import (
    Account,
    BankAccount,
    Customer,
    CustomerPayment,
    GoodsReceipt,
    GoodsReceiptLine,
    Invoice,
    JournalEntry,
    JournalLine,
    Membership,
    Product,
    PurchaseOrder,
    StockBalance,
    Supplier,
    SupplierPayment,
    Transaction,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


def _not_closing_journal():
    """Filter jurnal penutup (CLS-*) dan reversal-nya (REV-CLS-*) dari laporan laba/rugi."""
    return ~JournalEntry.journal_number.like("CLS-%"), ~JournalEntry.journal_number.like("REV-CLS-%")


def _journal_statuses():
    """Jurnal yang diperhitungkan laporan: posted + reversed.

    Jurnal original yang di-reverse (status 'reversed') tetap dihitung agar
    pasangan original+reversal-nya netral di laporan keuangan; tanpa ini
    reversal akan tampil sebagai posisi berlawanan yang salah.
    """
    return JournalEntry.status.in_(("posted", "reversed"))


async def _cash_account_ids(session: AsyncSession, tenant_id: str) -> list[str]:
    """Akun kas tunai (nama mengandung 'kas') + akun GL yang terhubung rekening bank."""
    bank_account_ids = (
        await session.execute(
            select(BankAccount.account_id).where(BankAccount.tenant_id == tenant_id)
        )
    ).scalars().all()
    rows = (
        await session.execute(
            select(Account.id).where(
                Account.tenant_id == tenant_id,
                Account.type == "asset",
                or_(
                    Account.name.ilike("%kas%"),
                    Account.id.in_(bank_account_ids),
                ),
            )
        )
    ).scalars().all()
    return list(rows)


class ReportMetadata(ApiSchema):
    tenant_name: str
    period: dict
    currency: str
    timezone: str
    generated_at: str
    basis: str = "accrual"


def _build_metadata(ctx: TenantContext, start: date, end: date) -> ReportMetadata:
    return ReportMetadata(
        tenant_name=ctx.slug,
        period={"startDate": start.isoformat(), "endDate": end.isoformat(), "timezone": ctx.timezone},
        currency="IDR",
        timezone=ctx.timezone,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/summary")
async def get_summary(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    start, end = params.resolve()
    metadata = _build_metadata(ctx, start, end)

    income_expense = (
        await session.execute(
            select(
                func.coalesce(
                    func.sum(case((Account.type == "income", JournalLine.credit - JournalLine.debit), else_=0)), 0
                ).label("income"),
                func.coalesce(
                    func.sum(case((Account.type == "expense", JournalLine.debit - JournalLine.credit), else_=0)), 0
                ).label("expense"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalEntry.journal_number.not_like("CLS-%"),
                JournalEntry.journal_number.not_like("REV-CLS-%"),
                JournalEntry.journal_date.between(start, end),
            )
        )
    ).one()

    income_val: Decimal = income_expense.income or Decimal("0")
    expense_val: Decimal = income_expense.expense or Decimal("0")
    profit_val = income_val - expense_val

    bar = (
        await session.execute(
            select(
                func.date_trunc(literal_column("'day'"), JournalEntry.journal_date).label("dt"),
                func.coalesce(
                    func.sum(case((Account.type == "income", JournalLine.credit - JournalLine.debit), else_=0)), 0
                ).label("income"),
                func.coalesce(
                    func.sum(case((Account.type == "expense", JournalLine.debit - JournalLine.credit), else_=0)), 0
                ).label("expense"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalEntry.journal_number.not_like("CLS-%"),
                JournalEntry.journal_number.not_like("REV-CLS-%"),
                JournalEntry.journal_date.between(start, end),
            )
            .group_by(func.date_trunc(literal_column("'day'"), JournalEntry.journal_date))
            .order_by(func.date_trunc(literal_column("'day'"), JournalEntry.journal_date))
        )
    ).all()

    series = [{"date": str(row.dt.date()), "income": str(row.income), "expense": str(row.expense)} for row in bar]

    composition = (
        await session.execute(
            select(
                Account.name,
                func.sum(JournalLine.debit - JournalLine.credit).label("amount"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalEntry.journal_number.not_like("CLS-%"),
                JournalEntry.journal_number.not_like("REV-CLS-%"),
                Account.type == "expense",
                JournalEntry.journal_date.between(start, end),
            )
            .group_by(Account.name)
            .order_by(func.sum(JournalLine.debit - JournalLine.credit).desc())
        )
    ).all()

    expense_composition = [{"name": row.name, "amount": str(row.amount)} for row in composition]

    return {
        "metadata": metadata.model_dump(mode="json"),
        "summary": {
            "income": str(income_val),
            "expense": str(expense_val),
            "profit": str(profit_val),
        },
        "series": series,
        "composition": expense_composition,
    }


@router.get("/profit-loss")
async def get_profit_loss(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    start, end = params.resolve()
    metadata = _build_metadata(ctx, start, end)

    rows = (
        await session.execute(
            select(
                Account.code,
                Account.name,
                Account.type,
                func.coalesce(func.sum(JournalLine.debit), 0).label("debit_total"),
                func.coalesce(func.sum(JournalLine.credit), 0).label("credit_total"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalEntry.journal_number.not_like("CLS-%"),
                JournalEntry.journal_number.not_like("REV-CLS-%"),
                Account.type.in_(["income", "expense"]),
                JournalEntry.journal_date.between(start, end),
            )
            .group_by(Account.code, Account.name, Account.type)
            .order_by(Account.code)
        )
    ).all()

    pl_rows = []
    total_income = Decimal("0")
    total_expense = Decimal("0")
    for row in rows:
        if row.type == "income":
            net = row.credit_total - row.debit_total
            total_income += net
        else:
            net = row.debit_total - row.credit_total
            total_expense += net
        pl_rows.append({
            "code": row.code,
            "name": row.name,
            "type": row.type,
            "debitTotal": str(row.debit_total),
            "creditTotal": str(row.credit_total),
            "net": str(net),
        })

    return {
        "metadata": metadata.model_dump(mode="json"),
        "summary": {
            "totalIncome": str(total_income),
            "totalExpense": str(total_expense),
            "netProfit": str(total_income - total_expense),
        },
        "rows": pl_rows,
    }


@router.get("/trial-balance")
async def get_trial_balance(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
    include_closing: bool = Query(False, alias="includeClosing", description="Sertakan jurnal penutup (CLS-*)"),
):
    start, end = params.resolve()
    metadata = _build_metadata(ctx, start, end)

    conditions = [
        JournalEntry.tenant_id == ctx.id,
        _journal_statuses(),
    ]
    if not include_closing:
        conditions.append(JournalEntry.journal_number.not_like("CLS-%"))
        conditions.append(JournalEntry.journal_number.not_like("REV-CLS-%"))

    rows = (
        await session.execute(
            select(
                Account.code,
                Account.name,
                Account.type,
                Account.normal_balance,
                func.coalesce(
                    func.sum(case((JournalEntry.journal_date < start, JournalLine.debit), else_=0)), 0
                ).label("opening_debit"),
                func.coalesce(
                    func.sum(case((JournalEntry.journal_date < start, JournalLine.credit), else_=0)), 0
                ).label("opening_credit"),
                func.coalesce(
                    func.sum(case((JournalEntry.journal_date.between(start, end), JournalLine.debit), else_=0)), 0
                ).label("period_debit"),
                func.coalesce(
                    func.sum(case((JournalEntry.journal_date.between(start, end), JournalLine.credit), else_=0)), 0
                ).label("period_credit"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(and_(*conditions), JournalEntry.journal_date <= end)
            .group_by(Account.code, Account.name, Account.type, Account.normal_balance)
            .order_by(Account.code)
        )
    ).all()

    tb_rows = []
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    for code, name, atype, normal_balance, op_d, op_c, p_d, p_c in rows:
        opening = (op_d or Decimal("0")) - (op_c or Decimal("0"))
        closing = opening + (p_d or Decimal("0")) - (p_c or Decimal("0"))
        debit = closing if closing >= 0 else Decimal("0")
        credit = -closing if closing < 0 else Decimal("0")
        total_debit += debit
        total_credit += credit
        tb_rows.append({
            "code": code,
            "name": name,
            "type": atype,
            "normalBalance": normal_balance,
            "openingBalance": str(opening),
            "periodDebit": str(p_d or Decimal("0")),
            "periodCredit": str(p_c or Decimal("0")),
            "closingBalance": str(closing),
            "debit": str(debit),
            "credit": str(credit),
        })

    return {
        "metadata": metadata.model_dump(mode="json"),
        "summary": {
            "totalDebit": str(total_debit),
            "totalCredit": str(total_credit),
            "balanced": total_debit == total_credit,
        },
        "rows": tb_rows,
    }


@router.get("/balance-sheet")
async def get_balance_sheet(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    _, end = params.resolve()

    rows = (
        await session.execute(
            select(
                Account.code,
                Account.name,
                Account.type,
                Account.normal_balance,
                func.coalesce(func.sum(JournalLine.debit), 0).label("debit_total"),
                func.coalesce(func.sum(JournalLine.credit), 0).label("credit_total"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                Account.type.in_(["asset", "liability", "equity"]),
                JournalEntry.journal_date <= end,
            )
            .group_by(Account.code, Account.name, Account.type, Account.normal_balance)
            .order_by(Account.code)
        )
    ).all()

    bs_rows = []
    totals: dict[str, Decimal] = {"asset": Decimal("0"), "liability": Decimal("0"), "equity": Decimal("0")}
    for row in rows:
        balance = row.debit_total - row.credit_total
        if row.normal_balance == "credit":
            balance = -balance
        totals[row.type] += balance
        bs_rows.append({
            "code": row.code,
            "name": row.name,
            "type": row.type,
            "balance": str(balance),
        })

    return {
        "metadata": _build_metadata(ctx, end, end).model_dump(mode="json"),
        "summary": {
            "totalAssets": str(totals["asset"]),
            "totalLiabilities": str(totals["liability"]),
            "totalEquity": str(totals["equity"]),
            "liabilitiesPlusEquity": str(totals["liability"] + totals["equity"]),
        },
        "rows": bs_rows,
    }


@router.get("/cash-flow")
async def get_cash_flow(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    start, end = params.resolve()
    metadata = _build_metadata(ctx, start, end)

    cash_accounts = await _cash_account_ids(session, ctx.id)

    if not cash_accounts:
        return {
            "metadata": metadata.model_dump(mode="json"),
            "summary": {"operating": "0.00", "investing": "0.00", "financing": "0.00", "netCashFlow": "0.00"},
            "rows": [],
        }

    rows = (
        await session.execute(
            select(
                JournalEntry.journal_date.label("dt"),
                JournalLine.description,
                JournalLine.debit,
                JournalLine.credit,
                Account.name.label("account_name"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalLine.account_id.in_(cash_accounts),
                JournalEntry.journal_date.between(start, end),
            )
            .order_by(JournalEntry.journal_date, JournalLine.id)
        )
    ).all()

    total_in = Decimal("0")
    total_out = Decimal("0")
    flow_rows = []
    for row in rows:
        flow_rows.append({
            "date": row.dt.isoformat() if hasattr(row.dt, "isoformat") else str(row.dt),
            "description": row.description or "",
            "accountName": row.account_name,
            "inflow": str(row.debit),
            "outflow": str(row.credit),
        })
        total_in += row.debit
        total_out += row.credit

    net = total_in - total_out
    return {
        "metadata": metadata.model_dump(mode="json"),
        "summary": {
            "operating": str(net),
            "investing": "0.00",
            "financing": "0.00",
            "netCashFlow": str(net),
        },
        "rows": flow_rows,
    }


@router.get("/general-ledger")
async def get_general_ledger(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    account_id: str | None = Query(None, alias="accountId"),
):
    start, end = params.resolve()

    conditions = [
        JournalEntry.tenant_id == ctx.id,
        _journal_statuses(),
        JournalEntry.journal_date.between(start, end),
    ]
    if account_id:
        conditions.append(JournalLine.account_id == account_id)

    total_q = (
        select(func.count(JournalLine.id))
        .select_from(JournalLine)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .where(and_(*conditions))
    )
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(
            JournalLine.id,
            JournalEntry.journal_number,
            JournalEntry.journal_date,
            JournalLine.description,
            Account.code.label("account_code"),
            Account.name.label("account_name"),
            JournalLine.debit,
            JournalLine.credit,
        )
        .select_from(JournalLine)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
        .where(and_(*conditions))
        .order_by(JournalEntry.journal_date, JournalEntry.id, JournalLine.line_number)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await session.execute(stmt)).all()

    items = [
        {
            "id": row.id,
            "journalNumber": row.journal_number,
            "date": row.journal_date.isoformat() if hasattr(row.journal_date, "isoformat") else str(row.journal_date),
            "description": row.description or "",
            "accountCode": row.account_code,
            "accountName": row.account_name,
            "debit": str(row.debit),
            "credit": str(row.credit),
        }
        for row in rows
    ]
    return make_paginated(
        items, page, page_size, total
    )


@router.get("/receivable-aging")
async def get_receivable_aging(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    today = date.today()

    invoices = (
        await session.execute(
            select(
                Invoice.id,
                Invoice.invoice_number,
                Invoice.invoice_date,
                Invoice.due_date,
                Invoice.balance_due,
                Customer.name.label("customer_name"),
            )
            .select_from(Invoice)
            .join(Customer, and_(Customer.id == Invoice.customer_id, Customer.tenant_id == ctx.id))
            .where(
                Invoice.tenant_id == ctx.id,
                Invoice.balance_due > 0,
            )
            .order_by(Invoice.due_date)
        )
    ).all()

    buckets = {"current": [], "1_30": [], "31_60": [], "61_90": [], "90_plus": []}
    totals = {"current": Decimal("0"), "1_30": Decimal("0"), "31_60": Decimal("0"), "61_90": Decimal("0"), "90_plus": Decimal("0")}

    for inv in invoices:
        days_overdue = (today - inv.due_date).days
        if days_overdue <= 0:
            bucket = "current"
        elif days_overdue <= 30:
            bucket = "1_30"
        elif days_overdue <= 60:
            bucket = "31_60"
        elif days_overdue <= 90:
            bucket = "61_90"
        else:
            bucket = "90_plus"

        entry = {
            "id": inv.id,
            "invoiceNumber": inv.invoice_number,
            "invoiceDate": inv.invoice_date.isoformat(),
            "dueDate": inv.due_date.isoformat(),
            "customerName": inv.customer_name,
            "balanceDue": str(inv.balance_due),
            "daysOverdue": max(0, days_overdue),
        }
        buckets[bucket].append(entry)
        totals[bucket] += inv.balance_due

    return {
        "metadata": {
            "tenantName": ctx.slug,
            "asOf": today.isoformat(),
            "currency": "IDR",
            "timezone": ctx.timezone,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "buckets": {
            "current": {"label": "Current", "total": str(totals["current"]), "items": buckets["current"]},
            "1_30": {"label": "1-30 Hari", "total": str(totals["1_30"]), "items": buckets["1_30"]},
            "31_60": {"label": "31-60 Hari", "total": str(totals["31_60"]), "items": buckets["31_60"]},
            "61_90": {"label": "61-90 Hari", "total": str(totals["61_90"]), "items": buckets["61_90"]},
            "90_plus": {"label": ">90 Hari", "total": str(totals["90_plus"]), "items": buckets["90_plus"]},
        },
        "grandTotal": str(sum(totals.values())),
    }


@router.get("/payable-aging")
async def get_payable_aging(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    """Aging hutang per supplier berbasis goods receipt (jurnal-linked) vs pembayaran supplier."""
    today = date.today()

    received_rows = (
        await session.execute(
            select(
                PurchaseOrder.supplier_id.label("supplier_id"),
                Supplier.name.label("supplier_name"),
                func.sum(GoodsReceiptLine.quantity * GoodsReceiptLine.unit_cost).label("received"),
                func.max(GoodsReceipt.received_at).label("last_receipt"),
            )
            .select_from(GoodsReceiptLine)
            .join(GoodsReceipt, GoodsReceipt.id == GoodsReceiptLine.goods_receipt_id)
            .join(PurchaseOrder, PurchaseOrder.id == GoodsReceipt.purchase_order_id)
            .join(Supplier, and_(Supplier.id == PurchaseOrder.supplier_id, Supplier.tenant_id == ctx.id))
            .where(
                GoodsReceipt.tenant_id == ctx.id,
                GoodsReceipt.journal_entry_id.is_not(None),
            )
            .group_by(PurchaseOrder.supplier_id, Supplier.name)
        )
    ).all()

    paid_rows = (
        await session.execute(
            select(
                SupplierPayment.supplier_id.label("supplier_id"),
                Supplier.name.label("supplier_name"),
                func.sum(SupplierPayment.amount).label("paid"),
            )
            .select_from(SupplierPayment)
            .join(Supplier, and_(Supplier.id == SupplierPayment.supplier_id, Supplier.tenant_id == ctx.id))
            .where(
                SupplierPayment.tenant_id == ctx.id,
                SupplierPayment.status == "posted",
                SupplierPayment.journal_entry_id.is_not(None),
            )
            .group_by(SupplierPayment.supplier_id, Supplier.name)
        )
    ).all()

    combined: dict[str, dict] = {}
    for row in received_rows:
        combined.setdefault(str(row.supplier_id), {
            "supplierId": str(row.supplier_id),
            "supplierName": row.supplier_name,
            "received": Decimal("0"),
            "paid": Decimal("0"),
            "lastReceipt": None,
        })
        combined[str(row.supplier_id)]["received"] = row.received or Decimal("0")
        combined[str(row.supplier_id)]["lastReceipt"] = row.last_receipt
    for row in paid_rows:
        combined.setdefault(str(row.supplier_id), {
            "supplierId": str(row.supplier_id),
            "supplierName": row.supplier_name,
            "received": Decimal("0"),
            "paid": Decimal("0"),
            "lastReceipt": None,
        })
        combined[str(row.supplier_id)]["paid"] = row.paid or Decimal("0")

    items = []
    grand = Decimal("0")
    for data in combined.values():
        outstanding = data["received"] - data["paid"]
        grand += outstanding
        if data["lastReceipt"] is not None:
            days = (today - data["lastReceipt"].date()).days
        else:
            days = 0
        if days <= 0:
            bucket = "current"
        elif days <= 30:
            bucket = "1_30"
        elif days <= 60:
            bucket = "31_60"
        elif days <= 90:
            bucket = "61_90"
        else:
            bucket = "90_plus"
        items.append({
            "supplierId": data["supplierId"],
            "supplierName": data["supplierName"],
            "received": str(data["received"]),
            "paid": str(data["paid"]),
            "outstanding": str(outstanding),
            "bucket": bucket,
            "daysSinceReceipt": max(0, days),
        })

    items.sort(key=lambda i: i["supplierName"])
    return {
        "metadata": {
            "tenantName": ctx.slug,
            "asOf": today.isoformat(),
            "currency": "IDR",
            "timezone": ctx.timezone,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "rows": items,
        "grandTotal": str(grand),
    }


@router.get("/stock-valuation")
async def get_stock_valuation(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    """Nilai persediaan: qty x average cost per produk + cross-check dengan GL Persediaan."""
    rows = (
        await session.execute(
            select(
                Product.sku,
                Product.name,
                StockBalance.quantity,
                StockBalance.average_cost,
            )
            .select_from(StockBalance)
            .join(Product, and_(Product.id == StockBalance.product_id, Product.tenant_id == ctx.id))
            .where(StockBalance.tenant_id == ctx.id)
            .order_by(Product.sku)
        )
    ).all()

    items = []
    total_value = Decimal("0")
    for sku, name, qty, avg_cost in rows:
        value = (qty or Decimal("0")) * (avg_cost or Decimal("0"))
        total_value += value
        items.append({
            "sku": sku,
            "productName": name,
            "quantity": str(qty or Decimal("0")),
            "averageCost": str(avg_cost or Decimal("0")),
            "value": str(value),
        })

    gl_value = Decimal("0")
    gl_rows = (
        await session.execute(
            select(Account.code, func.sum(JournalLine.debit - JournalLine.credit))
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                Account.code == "1-3001",
            )
            .group_by(Account.code)
        )
    ).all()
    if gl_rows:
        gl_value = gl_rows[0][1] or Decimal("0")

    return {
        "metadata": {
            "tenantName": ctx.slug,
            "asOf": date.today().isoformat(),
            "currency": "IDR",
            "timezone": ctx.timezone,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "summary": {
            "totalValue": str(total_value),
            "glInventoryValue": str(gl_value),
            "glDelta": str(total_value - gl_value),
        },
        "rows": items,
    }


@router.get("/investor")
async def get_investor_report(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    today = date.today()

    cash_accounts = await _cash_account_ids(session, ctx.id)
    cash_position = Decimal("0")
    if cash_accounts:
        cash_rows = (
            await session.execute(
                select(
                    func.coalesce(func.sum(JournalLine.debit), 0) - func.coalesce(func.sum(JournalLine.credit), 0)
                )
                .select_from(JournalLine)
                .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
                .where(
                    JournalEntry.tenant_id == ctx.id,
                    _journal_statuses(),
                    JournalLine.account_id.in_(cash_accounts),
                    JournalEntry.journal_date <= today,
                )
            )
        ).scalar()
        cash_position = cash_rows or Decimal("0")

    six_months_ago = today.replace(day=1)
    for _ in range(6):
        six_months_ago = six_months_ago.replace(day=1)
        if six_months_ago.month == 1:
            six_months_ago = six_months_ago.replace(year=six_months_ago.year - 1, month=12)
        else:
            six_months_ago = six_months_ago.replace(month=six_months_ago.month - 1)

    monthly = (
        await session.execute(
            select(
                func.date_trunc(literal_column("'month'"), JournalEntry.journal_date).label("month"),
                func.coalesce(
                    func.sum(case((Account.type == "income", JournalLine.credit - JournalLine.debit), else_=0)), 0
                ).label("revenue"),
                func.coalesce(
                    func.sum(case((Account.type == "expense", JournalLine.debit - JournalLine.credit), else_=0)), 0
                ).label("expense"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalEntry.journal_number.not_like("CLS-%"),
                JournalEntry.journal_number.not_like("REV-CLS-%"),
                JournalEntry.journal_date >= six_months_ago,
                JournalEntry.journal_date <= today,
            )
            .group_by(func.date_trunc(literal_column("'month'"), JournalEntry.journal_date))
            .order_by(func.date_trunc(literal_column("'month'"), JournalEntry.journal_date))
        )
    ).all()

    series = [{"month": str(row.month.date()), "revenue": str(row.revenue), "expense": str(row.expense)} for row in monthly]

    composition = (
        await session.execute(
            select(
                Account.name,
                func.sum(JournalLine.debit - JournalLine.credit).label("amount"),
            )
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == ctx.id))
            .where(
                JournalEntry.tenant_id == ctx.id,
                _journal_statuses(),
                JournalEntry.journal_number.not_like("CLS-%"),
                JournalEntry.journal_number.not_like("REV-CLS-%"),
                Account.type == "expense",
                JournalEntry.journal_date >= six_months_ago,
                JournalEntry.journal_date <= today,
            )
            .group_by(Account.name)
            .order_by(func.sum(JournalLine.debit - JournalLine.credit).desc())
        )
    ).all()

    expense_breakdown = [{"name": row.name, "amount": str(row.amount)} for row in composition]

    total_revenue_6m = sum((Decimal(str(r.revenue)) for r in monthly), Decimal("0"))
    total_expense_6m = sum((Decimal(str(r.expense)) for r in monthly), Decimal("0"))
    gross_margin = total_revenue_6m - total_expense_6m
    monthly_avg_expense = total_expense_6m / Decimal("6") if total_expense_6m else Decimal("0")
    burn_rate = monthly_avg_expense - (total_revenue_6m / Decimal("6"))
    runway = (cash_position / burn_rate) if burn_rate and burn_rate > 0 else None

    return {
        "metadata": _build_metadata(ctx, six_months_ago, today).model_dump(mode="json"),
        "metrics": {
            "revenue": str(total_revenue_6m),
            "grossMargin": str(gross_margin),
            "burnRate": str(burn_rate),
            "cashPosition": str(cash_position),
            "runway": str(round(runway, 1)) if runway is not None else None,
        },
        "series": series,
        "composition": expense_breakdown,
    }
