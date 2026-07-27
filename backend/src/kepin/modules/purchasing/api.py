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
from kepin.core.money import to_money, money_str, to_quantity, ZERO
from kepin.db.models import (
    Supplier,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    Product,
    StockBalance,
    StockMovement,
    InventoryLocation,
)

router = APIRouter(tags=["Purchasing"])


# ── Schemas ──────────────────────────────────────────────────────────


class SupplierSchema(ApiSchema):
    id: str
    code: str
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    tax_id: str = ""
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SupplierCreate(ApiSchema):
    code: str
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    tax_id: str = ""


class SupplierUpdate(ApiSchema):
    code: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    status: str | None = None


class POLineInput(ApiSchema):
    product_id: str | None = None
    item_name: str
    quantity: str
    unit_price: str


class POCreate(ApiSchema):
    supplier_id: str
    order_date: date
    expected_date: date | None = None
    branch_id: str | None = None
    notes: str = ""
    lines: list[POLineInput]


class POUpdate(ApiSchema):
    expected_date: date | None = None
    notes: str | None = None
    lines: list[POLineInput] | None = None


class POLineSchema(ApiSchema):
    id: str
    product_id: str | None = None
    item_name: str
    quantity: str
    received_quantity: str
    unit_price: str
    line_total: str
    line_number: int


class POSchema(ApiSchema):
    id: str
    po_number: str
    order_date: date
    expected_date: str | None = None
    status: str
    supplier_id: str
    subtotal: str
    total: str
    notes: str = ""
    branch_id: str | None = None
    lines: list[POLineSchema] = []
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class POReceiveLineItem(ApiSchema):
    line_id: str
    quantity_received: str


class POReceiveRequest(ApiSchema):
    location_id: str
    lines: list[POReceiveLineItem]
    notes: str = ""


# ── Suppliers ─────────────────────────────────────────────────────────


@router.get("/suppliers", response_model=PaginatedResponse[SupplierSchema])
async def list_suppliers(
    session: AsyncSession = Depends(get_session),
    tenant: TenantContext = Depends(get_tenant_context),
    params: ListParams = Depends(),
):
    conditions = [Supplier.tenant_id == tenant.id]
    if params.search:
        like = f"%{params.search}%"
        conditions.append(or_(Supplier.name.ilike(like), Supplier.code.ilike(like), Supplier.email.ilike(like)))

    where = and_(*conditions)

    total_q = select(func.count(Supplier.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Supplier)
        .where(where)
        .order_by(Supplier.name)
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [SupplierSchema.model_validate(s) for s in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/suppliers", response_model=SupplierSchema, status_code=201)
async def create_supplier(
    body: SupplierCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    dup = await session.execute(
        select(Supplier).where(Supplier.tenant_id == tenant.id, Supplier.code == body.code)
    )
    if dup.scalar_one_or_none():
        raise ConflictError(message=f"Kode supplier '{body.code}' sudah digunakan")

    now = datetime.now(timezone.utc)
    supplier = Supplier(
        id=new_uuid(),
        tenant_id=tenant.id,
        code=body.code,
        name=body.name,
        email=body.email or "",
        phone=body.phone or "",
        address=body.address or "",
        tax_id=body.tax_id or "",
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(supplier)
    await session.commit()
    await session.refresh(supplier)
    return SupplierSchema.model_validate(supplier)


@router.get("/suppliers/{supplier_id}", response_model=SupplierSchema)
async def get_supplier(
    supplier_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    s = await session.execute(
        select(Supplier).where(Supplier.id == supplier_id, Supplier.tenant_id == tenant.id)
    )
    supplier = s.scalar_one_or_none()
    if not supplier:
        raise NotFoundError(message="Supplier tidak ditemukan")
    return SupplierSchema.model_validate(supplier)


@router.patch("/suppliers/{supplier_id}", response_model=SupplierSchema)
async def update_supplier(
    body: SupplierUpdate,
    supplier_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    s = await session.execute(
        select(Supplier).where(Supplier.id == supplier_id, Supplier.tenant_id == tenant.id)
    )
    supplier = s.scalar_one_or_none()
    if not supplier:
        raise NotFoundError(message="Supplier tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(supplier, field, value)
    supplier.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(supplier)
    return SupplierSchema.model_validate(supplier)


@router.delete("/suppliers/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    s = await session.execute(
        select(Supplier).where(Supplier.id == supplier_id, Supplier.tenant_id == tenant.id)
    )
    supplier = s.scalar_one_or_none()
    if not supplier:
        raise NotFoundError(message="Supplier tidak ditemukan")

    po_cnt = await session.execute(
        select(func.count(PurchaseOrder.id)).where(PurchaseOrder.supplier_id == supplier_id)
    )
    if po_cnt.scalar() or 0 > 0:
        raise ConflictError(message="Supplier memiliki purchase order")

    await session.delete(supplier)
    await session.commit()


# ── Purchase Orders ───────────────────────────────────────────────────


async def _next_po_number(
    session: AsyncSession,
    tenant_id: str,
) -> str:
    cnt = await session.execute(
        select(func.count(PurchaseOrder.id)).where(PurchaseOrder.tenant_id == tenant_id)
    )
    return f"PO-{cnt.scalar() or 0 + 1:06d}"


async def _build_po_lines(
    lines_data: list[POLineInput],
    tenant_id: str,
    po_id: str | None = None,
) -> list[PurchaseOrderLine]:
    lines = []
    subtotal = ZERO
    for i, line in enumerate(lines_data):
        qty = to_quantity(line.quantity)
        unit_price = to_money(line.unit_price)
        line_total = (qty * unit_price).quantize(to_money("0.01").__class__(ZERO))
        subtotal += (qty * unit_price).quantize(to_money("0.01").__class__(ZERO))

        lines.append(PurchaseOrderLine(
            id=new_uuid(),
            tenant_id=tenant_id,
            purchase_order_id=po_id,
            product_id=line.product_id,
            line_number=i + 1,
            item_name=line.item_name,
            quantity=qty,
            received_quantity=ZERO,
            unit_price=unit_price,
            line_total=(qty * unit_price).quantize(to_money("0.01").__class__(ZERO)),
        ))
    return lines, subtotal


@router.get("/purchase-orders", response_model=PaginatedResponse[POSchema])
async def list_purchase_orders(
    session: AsyncSession = Depends(get_session),
    tenant: TenantContext = Depends(get_tenant_context),
    params: ListParams = Depends(),
    status: str | None = Query(None),
    period: PeriodParams = Depends(),
):
    conditions = [PurchaseOrder.tenant_id == tenant.id]

    if status:
        conditions.append(PurchaseOrder.status == status)

    start_date, end_date = None, None
    if period.preset or (period.start_date and period.end_date):
        start_date, end_date = period.resolve()
        conditions.append(PurchaseOrder.order_date.between(start_date, end_date))

    where = and_(*conditions)

    total_q = select(func.count(PurchaseOrder.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(PurchaseOrder)
        .where(where)
        .order_by(PurchaseOrder.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = []
    for po in rows:
        line_stmt = select(PurchaseOrderLine).where(
            PurchaseOrderLine.purchase_order_id == po.id
        ).order_by(PurchaseOrderLine.line_number)
        po_lines = (await session.execute(line_stmt)).scalars().all()

        items.append(POSchema(
            id=str(po.id),
            po_number=po.po_number,
            order_date=po.order_date,
            expected_date=str(po.expected_date) if po.expected_date else None,
            status=po.status,
            supplier_id=str(po.supplier_id),
            subtotal=money_str(po.subtotal),
            total=money_str(po.total),
            notes=po.notes or "",
            branch_id=str(po.branch_id) if po.branch_id else None,
            lines=[POLineSchema(
                id=str(l.id),
                product_id=str(l.product_id) if l.product_id else None,
                item_name=l.item_name,
                quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
                received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
                unit_price=money_str(l.unit_price),
                line_total=money_str(l.line_total),
                line_number=l.line_number,
            ) for l in po_lines],
            version=po.version,
        ))
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/purchase-orders", response_model=POSchema, status_code=201)
async def create_purchase_order(
    body: POCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    supplier = await session.execute(
        select(Supplier).where(Supplier.id == body.supplier_id, Supplier.tenant_id == tenant.id)
    )
    if not supplier.scalar_one_or_none():
        raise NotFoundError(message="Supplier tidak ditemukan")

    if not body.lines:
        raise ValidationError(message="Minimal satu item diperlukan")

    po_number = await _next_po_number(session, tenant.id)
    now = datetime.now(timezone.utc)

    lines_data, subtotal = await _build_po_lines(body.lines, tenant.id)

    po = PurchaseOrder(
        id=new_uuid(),
        tenant_id=tenant.id,
        po_number=po_number,
        supplier_id=body.supplier_id,
        order_date=body.order_date,
        expected_date=body.expected_date,
        status="draft",
        subtotal=subtotal,
        tax_total=ZERO,
        total=subtotal,
        notes=body.notes or "",
        branch_id=body.branch_id,
        created_at=now,
        updated_at=now,
    )
    session.add(po)
    await session.flush()

    for line in lines_data:
        line.purchase_order_id = po.id
        session.add(line)

    await session.commit()
    await session.refresh(po)

    line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    po_lines = (await session.execute(line_stmt)).scalars().all()

    return POSchema(
        id=str(po.id),
        po_number=po.po_number,
        order_date=po.order_date,
        expected_date=str(po.expected_date) if po.expected_date else None,
        status=po.status,
        supplier_id=str(po.supplier_id),
        subtotal=money_str(po.subtotal),
        total=money_str(po.total),
        notes=po.notes or "",
        branch_id=str(po.branch_id) if po.branch_id else None,
        lines=[POLineSchema(
            id=str(l.id),
            product_id=str(l.product_id) if l.product_id else None,
            item_name=l.item_name,
            quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
            received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
            unit_price=money_str(l.unit_price),
            line_total=money_str(l.line_total),
            line_number=l.line_number,
        ) for l in po_lines],
        version=po.version,
    )


@router.get("/purchase-orders/{po_id}", response_model=POSchema)
async def get_purchase_order(
    po_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    po = await session.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant.id)
    )
    po = po.scalar_one_or_none()
    if not po:
        raise NotFoundError(message="Purchase order tidak ditemukan")

    line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    po_lines = (await session.execute(line_stmt)).scalars().all()

    return POSchema(
        id=str(po.id),
        po_number=po.po_number,
        order_date=po.order_date,
        expected_date=str(po.expected_date) if po.expected_date else None,
        status=po.status,
        supplier_id=str(po.supplier_id),
        subtotal=money_str(po.subtotal),
        total=money_str(po.total),
        notes=po.notes or "",
        branch_id=str(po.branch_id) if po.branch_id else None,
        lines=[POLineSchema(
            id=str(l.id),
            product_id=str(l.product_id) if l.product_id else None,
            item_name=l.item_name,
            quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
            received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
            unit_price=money_str(l.unit_price),
            line_total=money_str(l.line_total),
            line_number=l.line_number,
        ) for l in po_lines],
        version=po.version,
    )


@router.patch("/purchase-orders/{po_id}", response_model=POSchema)
async def update_purchase_order(
    body: POUpdate,
    po_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    po = await session.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant.id)
    )
    po = po.scalar_one_or_none()
    if not po:
        raise NotFoundError(message="Purchase order tidak ditemukan")

    if po.status != "draft":
        raise ValidationError(message="Hanya PO dengan status draft yang bisa diubah")

    patch = body.model_dump(exclude_unset=True)
    patch.pop("lines", None)

    for field, value in patch.items():
        setattr(po, field, value)

    if body.lines is not None:
        old_lines = await session.execute(
            select(PurchaseOrderLine).where(PurchaseOrderLine.purchase_order_id == po.id)
        )
        for ol in old_lines.scalars().all():
            await session.delete(ol)

        lines_data, subtotal = await _build_po_lines(body.lines, tenant.id, po.id)
        for line in lines_data:
            session.add(line)
        po.subtotal = subtotal
        po.total = subtotal

    po.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(po)

    line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    po_lines = (await session.execute(line_stmt)).scalars().all()

    return POSchema(
        id=str(po.id),
        po_number=po.po_number,
        order_date=po.order_date,
        expected_date=str(po.expected_date) if po.expected_date else None,
        status=po.status,
        supplier_id=str(po.supplier_id),
        subtotal=money_str(po.subtotal),
        total=money_str(po.total),
        notes=po.notes or "",
        branch_id=str(po.branch_id) if po.branch_id else None,
        lines=[POLineSchema(
            id=str(l.id),
            product_id=str(l.product_id) if l.product_id else None,
            item_name=l.item_name,
            quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
            received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
            unit_price=money_str(l.unit_price),
            line_total=money_str(l.line_total),
            line_number=l.line_number,
        ) for l in po_lines],
        version=po.version,
    )


@router.delete("/purchase-orders/{po_id}", status_code=204)
async def delete_purchase_order(
    po_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    po = await session.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant.id)
    )
    po = po.scalar_one_or_none()
    if not po:
        raise NotFoundError(message="Purchase order tidak ditemukan")
    if po.status != "draft":
        raise ValidationError(message="Hanya PO draft yang bisa dihapus")

    line_stmt = select(PurchaseOrderLine).where(PurchaseOrderLine.purchase_order_id == po.id)
    po_lines = (await session.execute(line_stmt)).scalars().all()
    for l in po_lines:
        await session.delete(l)

    await session.delete(po)
    await session.commit()


@router.post("/purchase-orders/{po_id}/send", response_model=POSchema)
async def send_purchase_order(
    po_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    po = await session.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant.id)
    )
    po = po.scalar_one_or_none()
    if not po:
        raise NotFoundError(message="Purchase order tidak ditemukan")
    if po.status != "draft":
        raise ValidationError(message="Hanya PO draft yang bisa dikirim")

    po.status = "sent"
    po.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(po)

    line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    po_lines = (await session.execute(line_stmt)).scalars().all()

    return POSchema(
        id=str(po.id),
        po_number=po.po_number,
        order_date=po.order_date,
        expected_date=str(po.expected_date) if po.expected_date else None,
        status=po.status,
        supplier_id=str(po.supplier_id),
        subtotal=money_str(po.subtotal),
        total=money_str(po.total),
        notes=po.notes or "",
        branch_id=str(po.branch_id) if po.branch_id else None,
        lines=[POLineSchema(
            id=str(l.id),
            product_id=str(l.product_id) if l.product_id else None,
            item_name=l.item_name,
            quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
            received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
            unit_price=money_str(l.unit_price),
            line_total=money_str(l.line_total),
            line_number=l.line_number,
        ) for l in po_lines],
        version=po.version,
    )


@router.post("/purchase-orders/{po_id}/receive", response_model=POSchema)
async def receive_purchase_order(
    body: POReceiveRequest,
    po_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    po = await session.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant.id)
    )
    po = po.scalar_one_or_none()
    if not po:
        raise NotFoundError(message="Purchase order tidak ditemukan")
    if po.status not in ("sent", "partial"):
        raise ValidationError(message="PO harus berstatus sent atau partial untuk diterima")

    loc = await session.execute(
        select(InventoryLocation).where(
            InventoryLocation.id == body.location_id,
            InventoryLocation.tenant_id == tenant.id,
        )
    )
    if not loc.scalar_one_or_none():
        raise NotFoundError(message="Lokasi tidak ditemukan")

    now = datetime.now(timezone.utc)
    today = now.date()
    po_tenant_id = tenant.id

    receipt_count = await session.execute(
        select(func.count(GoodsReceipt.id)).where(GoodsReceipt.tenant_id == po_tenant_id)
    )
    receipt_number = f"GR-{(receipt_count.scalar() or 0) + 1:06d}"

    receipt = GoodsReceipt(
        id=new_uuid(),
        tenant_id=po_tenant_id,
        branch_id=po.branch_id,
        purchase_order_id=po.id,
        receipt_number=receipt_number,
        received_at=now,
        status="completed",
        notes=body.notes or "",
        created_at=now,
        updated_at=now,
    )
    session.add(receipt)
    await session.flush()

    mov_count = await session.execute(
        select(func.count(StockMovement.id)).where(StockMovement.tenant_id == po_tenant_id)
    )
    base_mov = (mov_count.scalar() or 0) + 1

    receive_map = {rl.line_id: rl.quantity_received for rl in body.lines}

    po_line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    all_lines = (await session.execute(po_line_stmt)).scalars().all()

    any_received = False
    all_fully_received = True

    for po_line in all_lines:
        if po_line.id in receive_map:
            qty_str = receive_map[po_line.id]
            receive_qty = to_quantity(qty_str)

            if receive_qty <= ZERO:
                continue

            if po_line.received_quantity + receive_qty > po_line.quantity:
                raise ValidationError(
                    message=f"Jumlah diterima melebihi quantity PO untuk line {po_line.line_number}"
                )

            grl = GoodsReceiptLine(
                id=new_uuid(),
                tenant_id=po_tenant_id,
                goods_receipt_id=receipt.id,
                purchase_order_line_id=po_line.id,
                product_id=po_line.product_id,
                quantity=receive_qty,
                unit_cost=po_line.unit_price,
            )
            session.add(grl)

            po_line.received_quantity += receive_qty
            any_received = True

            if po_line.product_id:
                sb_result = await session.execute(
                    select(StockBalance).where(
                        StockBalance.tenant_id == po_tenant_id,
                        StockBalance.product_id == po_line.product_id,
                        StockBalance.location_id == body.location_id,
                    ).with_for_update()
                )
                sb = sb_result.scalar_one_or_none()

                if sb:
                    old_qty = sb.quantity
                    old_cost = sb.average_cost
                    new_qty = old_qty + receive_qty
                    if old_qty > 0:
                        new_avg = ((old_qty * old_cost) + (receive_qty * po_line.unit_price)) / new_qty
                    else:
                        new_avg = po_line.unit_price
                    before_stock = old_qty
                    sb.quantity = new_qty
                    sb.average_cost = to_money(new_avg)
                else:
                    sb = StockBalance(
                        tenant_id=po_tenant_id,
                        product_id=po_line.product_id,
                        location_id=body.location_id,
                        quantity=receive_qty,
                        average_cost=po_line.unit_price,
                    )
                    session.add(sb)
                    before_stock = ZERO
                    new_qty = receive_qty

                mn = f"MOV-{base_mov:06d}"
                base_mov += 1
                mov = StockMovement(
                    id=new_uuid(),
                    tenant_id=po_tenant_id,
                    product_id=po_line.product_id,
                    location_id=body.location_id,
                    movement_number=mn,
                    movement_date=today,
                    type="in",
                    quantity=receive_qty,
                    before_stock=before_stock,
                    after_stock=new_qty,
                    unit_cost=po_line.unit_price,
                    reason=f"Penerimaan PO #{po.po_number}",
                    reference_type="purchase_order",
                    reference_id=po.id,
                    created_at=now,
                )
                session.add(mov)

        if po_line.received_quantity < po_line.quantity:
            all_fully_received = False

    if not any_received:
        raise ValidationError(message="Tidak ada item yang diterima")

    if all_fully_received:
        po.status = "received"
    else:
        po.status = "partial"

    po.updated_at = now
    await session.commit()
    await session.refresh(po)

    line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    po_lines = (await session.execute(line_stmt)).scalars().all()

    return POSchema(
        id=str(po.id),
        po_number=po.po_number,
        order_date=po.order_date,
        expected_date=str(po.expected_date) if po.expected_date else None,
        status=po.status,
        supplier_id=str(po.supplier_id),
        subtotal=money_str(po.subtotal),
        total=money_str(po.total),
        notes=po.notes or "",
        branch_id=str(po.branch_id) if po.branch_id else None,
        lines=[POLineSchema(
            id=str(l.id),
            product_id=str(l.product_id) if l.product_id else None,
            item_name=l.item_name,
            quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
            received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
            unit_price=money_str(l.unit_price),
            line_total=money_str(l.line_total),
            line_number=l.line_number,
        ) for l in po_lines],
        version=po.version,
    )


@router.post("/purchase-orders/{po_id}/cancel", response_model=POSchema)
async def cancel_purchase_order(
    po_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    po = await session.execute(
        select(PurchaseOrder).where(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant.id)
    )
    po = po.scalar_one_or_none()
    if not po:
        raise NotFoundError(message="Purchase order tidak ditemukan")
    if po.status in ("received", "cancelled"):
        raise ValidationError(message="PO sudah diterima atau dibatalkan")

    po.status = "cancelled"
    po.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(po)

    line_stmt = select(PurchaseOrderLine).where(
        PurchaseOrderLine.purchase_order_id == po.id
    ).order_by(PurchaseOrderLine.line_number)
    po_lines = (await session.execute(line_stmt)).scalars().all()

    return POSchema(
        id=str(po.id),
        po_number=po.po_number,
        order_date=po.order_date,
        expected_date=str(po.expected_date) if po.expected_date else None,
        status=po.status,
        supplier_id=str(po.supplier_id),
        subtotal=money_str(po.subtotal),
        total=money_str(po.total),
        notes=po.notes or "",
        branch_id=str(po.branch_id) if po.branch_id else None,
        lines=[POLineSchema(
            id=str(l.id),
            product_id=str(l.product_id) if l.product_id else None,
            item_name=l.item_name,
            quantity=money_str(l.quantity) if isinstance(l.quantity, Decimal) else str(l.quantity),
            received_quantity=money_str(l.received_quantity) if isinstance(l.received_quantity, Decimal) else str(l.received_quantity),
            unit_price=money_str(l.unit_price),
            line_total=money_str(l.line_total),
            line_number=l.line_number,
        ) for l in po_lines],
        version=po.version,
    )
