from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from kepin.api.dependencies import get_current_user, get_session, TenantContext, get_tenant_context, get_tenant_membership, require_tenant_owner, ListParams, PeriodParams
from kepin.api.errors import NotFoundError, ConflictError, ValidationError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, money_str, to_quantity, ZERO
from kepin.core.audit import record_audit
from kepin.core.subledger import (
    post_customer_payment_journal,
    post_invoice_journal,
    restore_stock_for_invoice,
    reverse_posted_journal,
)
from kepin.db.models import (
    Customer,
    Invoice,
    InvoiceLine,
    CustomerPayment,
    CustomerPaymentAllocation,
    JournalEntry,
    Membership,
    Product,
    User,
)

router = APIRouter(tags=["Sales"])


# ── Schemas ──────────────────────────────────────────────────────────


class CustomerSchema(ApiSchema):
    id: UUID
    code: str
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    tax_id: str = ""
    credit_limit: str
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CustomerCreate(ApiSchema):
    code: str
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    tax_id: str = ""
    credit_limit: str = "0"


class CustomerUpdate(ApiSchema):
    code: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    credit_limit: str | None = None
    status: str | None = None


class InvoiceLineInput(ApiSchema):
    product_id: str | None = None
    item_name: str
    quantity: str
    unit: str = ""
    unit_price: str
    tax_rate: str = "0"
    discount_amount: str = "0"


class InvoiceCreate(ApiSchema):
    customer_id: str
    invoice_date: date
    due_date: date
    branch_id: str | None = None
    notes: str = ""
    lines: list[InvoiceLineInput]


class InvoiceUpdate(ApiSchema):
    invoice_date: date | None = None
    due_date: date | None = None
    notes: str | None = None
    lines: list[InvoiceLineInput] | None = None


class InvoiceLineSchema(ApiSchema):
    id: str
    product_id: str | None = None
    item_name: str
    quantity: str
    unit: str = ""
    unit_price: str
    tax_rate: str
    discount_amount: str
    line_total: str
    line_number: int


class InvoiceSchema(ApiSchema):
    id: str
    invoice_number: str
    invoice_date: date
    due_date: date
    status: str
    customer_id: str
    subtotal: str
    tax_total: str
    discount_total: str
    total: str
    paid_amount: str
    balance_due: str
    notes: str = ""
    branch_id: str | None = None
    journal_entry_id: str | None = None
    lines: list[InvoiceLineSchema] = []
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CustomerPaymentSchema(ApiSchema):
    id: str
    payment_number: str
    payment_date: date
    amount: str
    method: str = ""
    reference: str = ""
    status: str
    customer_id: str
    branch_id: str | None = None
    journal_entry_id: str | None = None
    created_at: datetime | None = None


class PaymentAllocationInput(ApiSchema):
    invoice_id: str
    amount: str


class CustomerPaymentCreate(ApiSchema):
    customer_id: str
    payment_date: date
    amount: str
    method: str = ""
    reference: str = ""
    branch_id: str | None = None
    allocations: list[PaymentAllocationInput] = []


# ── Helpers ────────────────────────────────────────────────────────────


def _build_invoice_line_schema(line: InvoiceLine) -> InvoiceLineSchema:
    return InvoiceLineSchema(
        id=str(line.id),
        product_id=str(line.product_id) if line.product_id else None,
        item_name=line.item_name,
        quantity=money_str(line.quantity) if isinstance(line.quantity, Decimal) else str(line.quantity),
        unit=line.unit or "",
        unit_price=money_str(line.unit_price),
        tax_rate=money_str(line.tax_rate),
        discount_amount=money_str(line.discount_amount),
        line_total=money_str(line.line_total),
        line_number=line.line_number,
    )


def _build_invoice_schema(invoice: Invoice, lines: list[InvoiceLine]) -> InvoiceSchema:
    return InvoiceSchema(
        id=str(invoice.id),
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        status=invoice.status,
        customer_id=str(invoice.customer_id),
        subtotal=money_str(invoice.subtotal),
        tax_total=money_str(invoice.tax_total),
        discount_total=money_str(invoice.discount_total),
        total=money_str(invoice.total),
        paid_amount=money_str(invoice.paid_amount),
        balance_due=money_str(invoice.balance_due),
        notes=invoice.notes or "",
        branch_id=str(invoice.branch_id) if invoice.branch_id else None,
        journal_entry_id=str(invoice.journal_entry_id) if invoice.journal_entry_id else None,
        lines=[_build_invoice_line_schema(l) for l in lines],
        version=invoice.version,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
    )


async def _next_invoice_number(
    session: AsyncSession,
    tenant_id: str,
) -> str:
    cnt = await session.execute(
        select(func.count(Invoice.id)).where(Invoice.tenant_id == tenant_id)
    )
    return f"INV-{cnt.scalar() or 0 + 1:06d}"


async def _next_payment_number(
    session: AsyncSession,
    tenant_id: str,
) -> str:
    cnt = await session.execute(
        select(func.count(CustomerPayment.id)).where(CustomerPayment.tenant_id == tenant_id)
    )
    return f"PAY-{cnt.scalar() or 0 + 1:06d}"


async def _get_invoice_lines(
    session: AsyncSession,
    invoice_id: str,
) -> list[InvoiceLine]:
    stmt = select(InvoiceLine).where(
        InvoiceLine.invoice_id == invoice_id
    ).order_by(InvoiceLine.line_number)
    return (await session.execute(stmt)).scalars().all()


def _compute_line_totals(
    lines_data: list[InvoiceLineInput],
) -> tuple[list[dict], Decimal, Decimal, Decimal]:
    subtotal = ZERO
    tax_total = ZERO
    discount_total = ZERO
    computed = []

    for line in lines_data:
        qty = to_quantity(line.quantity)
        unit_price = to_money(line.unit_price)
        tax_pct = to_money(line.tax_rate)
        discount = to_money(line.discount_amount)

        line_subtotal = (qty * unit_price).quantize(to_money("0.01").__class__(ZERO))
        tax_factor = tax_pct / Decimal("100")
        line_tax = (line_subtotal * tax_factor).quantize(to_money("0.01").__class__(ZERO))
        line_total = line_subtotal - discount + line_tax

        subtotal += line_subtotal
        tax_total += line_tax
        discount_total += discount

        computed.append({
            "qty": qty,
            "unit_price": unit_price,
            "tax_rate": tax_pct,
            "discount_amount": discount,
            "line_subtotal": line_subtotal,
            "line_tax": line_tax,
            "line_total": line_total,
        })

    return computed, subtotal, tax_total, discount_total


# ── Customers ─────────────────────────────────────────────────────────


@router.get("/customers", response_model=PaginatedResponse[CustomerSchema], summary="Daftar Pelanggan", description="Mengembalikan daftar pelanggan dengan pagination dan pencarian")
async def list_customers(
    session: AsyncSession = Depends(get_session),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    params: ListParams = Depends(),
):
    conditions = [Customer.tenant_id == tenant.id]
    if params.search:
        like = f"%{params.search}%"
        conditions.append(
            or_(Customer.name.ilike(like), Customer.code.ilike(like), Customer.email.ilike(like))
        )

    where = and_(*conditions)

    total_q = select(func.count(Customer.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Customer)
        .where(where)
        .order_by(Customer.name)
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [CustomerSchema.model_validate(c) for c in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/customers", response_model=CustomerSchema, status_code=201, summary="Buat Pelanggan", description="Menambahkan pelanggan baru")
async def create_customer(
    body: CustomerCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    dup = await session.execute(
        select(Customer).where(Customer.tenant_id == tenant.id, Customer.code == body.code)
    )
    if dup.scalar_one_or_none():
        raise ConflictError(message=f"Kode customer '{body.code}' sudah digunakan")

    now = datetime.now(timezone.utc)
    customer = Customer(
        id=new_uuid(),
        tenant_id=tenant.id,
        code=body.code,
        name=body.name,
        email=body.email or "",
        phone=body.phone or "",
        address=body.address or "",
        tax_id=body.tax_id or "",
        credit_limit=to_money(body.credit_limit),
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return CustomerSchema.model_validate(customer)


@router.get("/customers/{customer_id}", response_model=CustomerSchema, summary="Detail Pelanggan", description="Mengembalikan detail pelanggan")
async def get_customer(
    customer_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    c = await session.execute(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant.id)
    )
    customer = c.scalar_one_or_none()
    if not customer:
        raise NotFoundError(message="Customer tidak ditemukan")
    return CustomerSchema.model_validate(customer)


@router.patch("/customers/{customer_id}", response_model=CustomerSchema, summary="Update Pelanggan", description="Memperbarui data pelanggan")
async def update_customer(
    body: CustomerUpdate,
    customer_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    c = await session.execute(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant.id)
    )
    customer = c.scalar_one_or_none()
    if not customer:
        raise NotFoundError(message="Customer tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        if field == "credit_limit":
            setattr(customer, field, to_money(value))
        else:
            setattr(customer, field, value)
    customer.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(customer)
    return CustomerSchema.model_validate(customer)


@router.delete("/customers/{customer_id}", status_code=204, summary="Hapus Pelanggan", description="Menghapus pelanggan")
async def delete_customer(
    customer_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    c = await session.execute(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant.id)
    )
    customer = c.scalar_one_or_none()
    if not customer:
        raise NotFoundError(message="Customer tidak ditemukan")

    inv_cnt = await session.execute(
        select(func.count(Invoice.id)).where(
            Invoice.customer_id == customer_id,
            Invoice.tenant_id == tenant.id,
        )
    )
    if inv_cnt.scalar() or 0 > 0:
        raise ConflictError(message="Customer memiliki faktur")

    await session.delete(customer)
    await session.commit()


# ── Invoices ──────────────────────────────────────────────────────────


@router.get("/invoices", response_model=PaginatedResponse[InvoiceSchema], summary="Daftar Invoice", description="Mengembalikan daftar invoice dengan pagination dan filter")
async def list_invoices(
    session: AsyncSession = Depends(get_session),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    params: ListParams = Depends(),
    status: str | None = Query(None),
    customer_id: str | None = Query(None, alias="customerId"),
    period: PeriodParams = Depends(),
):
    conditions = [Invoice.tenant_id == tenant.id]

    if status:
        conditions.append(Invoice.status == status)
    if customer_id:
        conditions.append(Invoice.customer_id == customer_id)

    start_date, end_date = None, None
    if period.preset or (period.start_date and period.end_date):
        start_date, end_date = period.resolve()
        conditions.append(Invoice.invoice_date.between(start_date, end_date))

    where = and_(*conditions)

    total_q = select(func.count(Invoice.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Invoice)
        .where(where)
        .order_by(Invoice.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = []
    for inv in rows:
        lines = await _get_invoice_lines(session, str(inv.id))
        items.append(_build_invoice_schema(inv, lines))

    return make_paginated(items, params.page, params.page_size, total)


@router.post("/invoices", response_model=InvoiceSchema, status_code=201, summary="Buat Invoice", description="Membuat invoice baru dengan line items (total dihitung backend)")
async def create_invoice(
    body: InvoiceCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    customer = await session.execute(
        select(Customer).where(Customer.id == body.customer_id, Customer.tenant_id == tenant.id)
    )
    if not customer.scalar_one_or_none():
        raise NotFoundError(message="Customer tidak ditemukan")

    if not body.lines:
        raise ValidationError(message="Minimal satu item diperlukan")

    for line in body.lines:
        qty = to_quantity(line.quantity)
        price = to_money(line.unit_price)
        if qty <= ZERO:
            raise ValidationError(message=f"Quantity harus > 0 untuk item '{line.item_name}'")
        if price <= ZERO:
            raise ValidationError(message=f"Unit price harus > 0 untuk item '{line.item_name}'")

    computed, subtotal, tax_total, discount_total = _compute_line_totals(body.lines)
    total = subtotal + tax_total - discount_total

    invoice_number = await _next_invoice_number(session, tenant.id)
    now = datetime.now(timezone.utc)

    invoice = Invoice(
        id=new_uuid(),
        tenant_id=tenant.id,
        invoice_number=invoice_number,
        customer_id=body.customer_id,
        invoice_date=body.invoice_date,
        due_date=body.due_date,
        status="draft",
        subtotal=subtotal,
        tax_total=tax_total,
        discount_total=discount_total,
        total=total,
        paid_amount=ZERO,
        balance_due=total,
        notes=body.notes or "",
        branch_id=body.branch_id,
        created_at=now,
        updated_at=now,
    )
    session.add(invoice)
    await session.flush()

    for i, (line, comp) in enumerate(zip(body.lines, computed)):
        session.add(InvoiceLine(
            id=new_uuid(),
            tenant_id=tenant.id,
            invoice_id=invoice.id,
            line_number=i + 1,
            product_id=line.product_id,
            item_name=line.item_name,
            quantity=comp["qty"],
            unit=line.unit or "",
            unit_price=comp["unit_price"],
            tax_rate=comp["tax_rate"],
            discount_amount=comp["discount_amount"],
            line_total=comp["line_total"],
        ))

    await session.commit()
    await session.refresh(invoice)

    lines = await _get_invoice_lines(session, str(invoice.id))
    return _build_invoice_schema(invoice, lines)


@router.get("/invoices/{invoice_id}", response_model=InvoiceSchema, summary="Detail Invoice", description="Mengembalikan detail invoice beserta lines")
async def get_invoice(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant.id)
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")

    lines = await _get_invoice_lines(session, invoice_id)
    return _build_invoice_schema(invoice, lines)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceSchema, summary="Update Invoice", description="Memperbarui invoice draft")
async def update_invoice(
    body: InvoiceUpdate,
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant.id)
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")

    if invoice.status != "draft":
        raise ValidationError(message="Hanya faktur draft yang bisa diubah")

    patch = body.model_dump(exclude_unset=True)
    patch.pop("lines", None)

    for field, value in patch.items():
        setattr(invoice, field, value)

    if body.lines is not None:
        if not body.lines:
            raise ValidationError(message="Minimal satu item diperlukan")

        old_lines = await _get_invoice_lines(session, invoice_id)
        for ol in old_lines:
            await session.delete(ol)

        computed, subtotal, tax_total, discount_total = _compute_line_totals(body.lines)
        total = subtotal + tax_total - discount_total

        for i, (line, comp) in enumerate(zip(body.lines, computed)):
            session.add(InvoiceLine(
                id=new_uuid(),
                tenant_id=tenant.id,
                invoice_id=invoice.id,
                line_number=i + 1,
                product_id=line.product_id,
                item_name=line.item_name,
                quantity=comp["qty"],
                unit=line.unit or "",
                unit_price=comp["unit_price"],
                tax_rate=comp["tax_rate"],
                discount_amount=comp["discount_amount"],
                line_total=comp["line_total"],
            ))

        invoice.subtotal = subtotal
        invoice.tax_total = tax_total
        invoice.discount_total = discount_total
        invoice.total = total
        if invoice.paid_amount > total:
            invoice.paid_amount = total
        invoice.balance_due = total - invoice.paid_amount

    invoice.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(invoice)

    lines = await _get_invoice_lines(session, invoice_id)
    return _build_invoice_schema(invoice, lines)


@router.delete("/invoices/{invoice_id}", status_code=204, summary="Hapus Invoice", description="Menghapus invoice draft")
async def delete_invoice(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant.id)
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")
    if invoice.status != "draft":
        raise ValidationError(message="Hanya faktur draft yang bisa dihapus")

    lines = await _get_invoice_lines(session, invoice_id)
    for l in lines:
        await session.delete(l)

    await session.delete(invoice)
    await session.commit()


@router.post("/invoices/{invoice_id}/send", response_model=InvoiceSchema, summary="Kirim Invoice", description="Mengubah status invoice menjadi sent")
async def send_invoice(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant.id)
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")
    if invoice.status != "draft":
        raise ValidationError(message="Hanya faktur draft yang bisa dikirim")

    invoice.status = "sent"
    invoice.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(invoice)

    lines = await _get_invoice_lines(session, invoice_id)
    return _build_invoice_schema(invoice, lines)


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceSchema, summary="Batal Invoice", description="Membatalkan invoice")
async def cancel_invoice(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant.id)
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")
    if invoice.status not in ("draft", "sent"):
        raise ValidationError(message="Hanya faktur draft/sent yang bisa dibatalkan")

    invoice.status = "cancelled"
    invoice.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(invoice)

    lines = await _get_invoice_lines(session, invoice_id)
    return _build_invoice_schema(invoice, lines)


@router.post("/invoices/{invoice_id}/post", response_model=InvoiceSchema, summary="Posting Invoice", description="Memposting invoice ke buku besar (Piutang/Pendapatan/PPN + HPP/Persediaan) melalui Central Posting Engine")
async def post_invoice(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant.id,
        ).with_for_update()
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")
    if invoice.status not in ("draft", "sent"):
        raise ValidationError(message="Hanya faktur draft/sent yang bisa diposting")
    if invoice.journal_entry_id:
        raise ValidationError(message="Faktur ini sudah diposting ke buku besar")

    lines = await _get_invoice_lines(session, invoice_id)
    if not lines:
        raise ValidationError(message="Faktur tidak memiliki line items")

    await post_invoice_journal(
        session=session,
        tenant_id=tenant.id,
        user_id=str(user.id),
        invoice=invoice,
        lines=lines,
    )

    invoice.status = "posted"
    invoice.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="invoice.post",
        module="sales",
        object_type="invoice",
        object_id=str(invoice.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"invoiceNumber": invoice.invoice_number, "journalEntryId": str(invoice.journal_entry_id)},
    )
    await session.commit()
    await session.refresh(invoice)

    lines = await _get_invoice_lines(session, invoice_id)
    return _build_invoice_schema(invoice, lines)


@router.post("/invoices/{invoice_id}/reverse", response_model=InvoiceSchema, summary="Reverse Invoice", description="Membatalkan invoice yang sudah diposting (reversal jurnal + restorasi stok)")
async def reverse_invoice(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    inv = await session.execute(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant.id,
        ).with_for_update()
    )
    invoice = inv.scalar_one_or_none()
    if not invoice:
        raise NotFoundError(message="Faktur tidak ditemukan")
    if invoice.status != "posted":
        raise ValidationError(message="Hanya faktur posted yang bisa di-reverse")
    if not invoice.journal_entry_id:
        raise ValidationError(message="Faktur tidak memiliki jurnal untuk di-reverse")
    if invoice.paid_amount > ZERO:
        raise ValidationError(
            message="Faktur sudah memiliki pembayaran; batalkan pembayaran terlebih dahulu"
        )

    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == invoice.journal_entry_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not journal:
        raise NotFoundError(message="Jurnal invoice tidak ditemukan")

    await reverse_posted_journal(
        session=session,
        tenant_id=tenant.id,
        journal_id=str(journal.id),
        description_prefix="Retur",
    )
    await restore_stock_for_invoice(session, tenant.id, invoice)

    invoice.status = "cancelled"
    invoice.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="invoice.reverse",
        module="sales",
        object_type="invoice",
        object_id=str(invoice.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"invoiceNumber": invoice.invoice_number, "status": invoice.status},
    )
    await session.commit()
    await session.refresh(invoice)

    lines = await _get_invoice_lines(session, invoice_id)
    return _build_invoice_schema(invoice, lines)


@router.get("/invoices/{invoice_id}/pdf", summary="Download PDF Invoice", description="Mengunduh invoice dalam format PDF")
async def get_invoice_pdf(
    invoice_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    _ = invoice_id, tenant, session
    return {"status": "not_available", "message": "PDF generation not yet implemented"}


# ── Customer Payments ─────────────────────────────────────────────────


@router.get("/customer-payments", response_model=PaginatedResponse[CustomerPaymentSchema], summary="Daftar Pembayaran", description="Mengembalikan daftar pembayaran pelanggan")
async def list_customer_payments(
    session: AsyncSession = Depends(get_session),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    params: ListParams = Depends(),
):
    conditions = [CustomerPayment.tenant_id == tenant.id]

    where = and_(*conditions)

    total_q = select(func.count(CustomerPayment.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(CustomerPayment)
        .where(where)
        .order_by(CustomerPayment.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [CustomerPaymentSchema.model_validate(p) for p in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/customer-payments", response_model=CustomerPaymentSchema, status_code=201, summary="Buat Pembayaran", description="Mencatat pembayaran dari pelanggan (status draft, posting melalui engine)")
async def create_customer_payment(
    body: CustomerPaymentCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    customer = await session.execute(
        select(Customer).where(Customer.id == body.customer_id, Customer.tenant_id == tenant.id)
    )
    if not customer.scalar_one_or_none():
        raise NotFoundError(message="Customer tidak ditemukan")

    payment_amount = to_money(body.amount)
    if payment_amount <= ZERO:
        raise ValidationError(message="Jumlah pembayaran harus > 0")

    payment_number = await _next_payment_number(session, tenant.id)
    now = datetime.now(timezone.utc)

    total_allocated = ZERO
    if body.allocations:
        for alloc in body.allocations:
            total_allocated += to_money(alloc.amount)

        if total_allocated > payment_amount:
            raise ValidationError(message="Total alokasi melebihi jumlah pembayaran")

    payment = CustomerPayment(
        id=new_uuid(),
        tenant_id=tenant.id,
        payment_number=payment_number,
        customer_id=body.customer_id,
        payment_date=body.payment_date,
        amount=payment_amount,
        method=body.method or "",
        reference=body.reference or "",
        status="draft",
        branch_id=body.branch_id,
        created_at=now,
        updated_at=now,
    )
    session.add(payment)
    await session.flush()

    if body.allocations:
        for alloc in body.allocations:
            alloc_amount = to_money(alloc.amount)

            inv = await session.execute(
                select(Invoice).where(
                    Invoice.id == alloc.invoice_id,
                    Invoice.tenant_id == tenant.id,
                    Invoice.customer_id == body.customer_id,
                ).with_for_update()
            )
            invoice = inv.scalar_one_or_none()
            if not invoice:
                raise ValidationError(message=f"Faktur {alloc.invoice_id} tidak ditemukan")

            new_paid = invoice.paid_amount + alloc_amount
            if new_paid > invoice.total:
                raise ValidationError(
                    message=f"Jumlah pembayaran melebihi sisa tagihan faktur {invoice.invoice_number}"
                )

            session.add(CustomerPaymentAllocation(
                id=new_uuid(),
                tenant_id=tenant.id,
                payment_id=payment.id,
                invoice_id=invoice.id,
                amount=alloc_amount,
            ))

            invoice.paid_amount = new_paid
            invoice.balance_due = invoice.total - new_paid
            if invoice.balance_due <= ZERO:
                invoice.status = "paid"
            else:
                invoice.status = "partial"

    payment.updated_at = now
    await session.commit()
    await session.refresh(payment)

    return CustomerPaymentSchema.model_validate(payment)


@router.post("/customer-payments/{payment_id}/post", response_model=CustomerPaymentSchema, summary="Posting Pembayaran", description="Memposting pembayaran ke buku besar (Kas/Piutang) melalui Central Posting Engine")
async def post_customer_payment(
    payment_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    p = await session.execute(
        select(CustomerPayment).where(
            CustomerPayment.id == payment_id,
            CustomerPayment.tenant_id == tenant.id,
        ).with_for_update()
    )
    payment = p.scalar_one_or_none()
    if not payment:
        raise NotFoundError(message="Pembayaran tidak ditemukan")
    if payment.status != "draft":
        raise ValidationError(message="Hanya pembayaran draft yang dapat diposting")
    if payment.journal_entry_id:
        raise ValidationError(message="Pembayaran ini sudah diposting ke buku besar")

    await post_customer_payment_journal(
        session=session,
        tenant_id=tenant.id,
        user_id=str(user.id),
        payment=payment,
    )

    payment.status = "posted"
    payment.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="customer_payment.post",
        module="sales",
        object_type="customer_payment",
        object_id=str(payment.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"paymentNumber": payment.payment_number, "journalEntryId": str(payment.journal_entry_id)},
    )
    await session.commit()
    await session.refresh(payment)

    return CustomerPaymentSchema.model_validate(payment)


@router.post("/customer-payments/{payment_id}/void", response_model=CustomerPaymentSchema, summary="Void Pembayaran", description="Membatalkan pembayaran (reversal jurnal + restore alokasi)")
async def void_customer_payment(
    payment_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    p = await session.execute(
        select(CustomerPayment).where(
            CustomerPayment.id == payment_id,
            CustomerPayment.tenant_id == tenant.id,
        ).with_for_update()
    )
    payment = p.scalar_one_or_none()
    if not payment:
        raise NotFoundError(message="Pembayaran tidak ditemukan")
    if payment.status == "voided":
        raise ValidationError(message="Pembayaran sudah dibatalkan")

    if payment.journal_entry_id:
        journal = (
            await session.execute(
                select(JournalEntry).where(
                    JournalEntry.id == payment.journal_entry_id,
                    JournalEntry.tenant_id == tenant.id,
                )
            )
        ).scalar_one_or_none()
        if journal:
            await reverse_posted_journal(
                session=session,
                tenant_id=tenant.id,
                journal_id=str(journal.id),
                description_prefix="Void",
            )

    allocs = await session.execute(
        select(CustomerPaymentAllocation).where(
            CustomerPaymentAllocation.payment_id == payment.id,
            CustomerPaymentAllocation.tenant_id == tenant.id,
        )
    )
    allocations = allocs.scalars().all()

    for alloc in allocations:
        inv = await session.execute(
            select(Invoice).where(
                Invoice.id == alloc.invoice_id,
                Invoice.tenant_id == tenant.id,
            ).with_for_update()
        )
        invoice = inv.scalar_one_or_none()
        if invoice:
            invoice.paid_amount -= alloc.amount
            invoice.balance_due = invoice.total - invoice.paid_amount
            if invoice.balance_due >= invoice.total:
                invoice.status = "sent"
            elif invoice.balance_due > ZERO:
                invoice.status = "partial"
            else:
                invoice.status = "paid"

        await session.delete(alloc)

    payment.status = "voided"
    payment.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="customer_payment.void",
        module="sales",
        object_type="customer_payment",
        object_id=str(payment.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"paymentNumber": payment.payment_number, "status": payment.status},
    )
    await session.commit()
    await session.refresh(payment)

    return CustomerPaymentSchema.model_validate(payment)
