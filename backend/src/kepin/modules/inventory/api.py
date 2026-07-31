from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from kepin.api.dependencies import get_current_user, get_session, TenantContext, get_tenant_context, get_tenant_membership, ListParams, PeriodParams
from kepin.api.errors import NotFoundError, ConflictError, ValidationError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, money_str, to_quantity, ZERO
from kepin.core.gl_mapping import DEFAULT_ACCOUNT_CODES as GL, get_account_by_code
from kepin.core.audit import record_audit
from kepin.core.subledger import post_stock_movement_journal
from kepin.db.models import (
    Membership,
    Product,
    InventoryLocation,
    StockBalance,
    StockMovement,
    User,
)

router = APIRouter(tags=["Inventory"])


# ── Schemas ──────────────────────────────────────────────────────────


class ProductSchema(ApiSchema):
    id: str
    sku: str
    name: str
    category: str = ""
    unit: str = ""
    sale_price: str
    cost_price: str
    minimum_stock: str
    status: str = "active"
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProductCreate(ApiSchema):
    sku: str
    name: str
    category: str = ""
    unit: str = ""
    sale_price: str = "0"
    cost_price: str = "0"
    minimum_stock: str = "0"


class ProductUpdate(ApiSchema):
    sku: str | None = None
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    sale_price: str | None = None
    cost_price: str | None = None
    minimum_stock: str | None = None
    status: str | None = None


class StockBalanceSchema(ApiSchema):
    product_id: str
    product_name: str = ""
    sku: str = ""
    location_id: str
    location_name: str = ""
    quantity: str
    average_cost: str


class StockMovementSchema(ApiSchema):
    id: str
    movement_number: str
    movement_date: date
    type: str
    product_id: str
    product_name: str = ""
    location_id: str
    location_name: str = ""
    quantity: str
    before_stock: str
    after_stock: str
    unit_cost: str
    reason: str = ""
    reference_type: str = ""
    reference_id: str | None = None
    journal_entry_id: str | None = None
    created_at: datetime | None = None


class StockReceiptCreate(ApiSchema):
    product_id: str
    location_id: str
    quantity: str
    unit_cost: str = "0"
    reason: str = ""


class StockIssueCreate(ApiSchema):
    product_id: str
    location_id: str
    quantity: str
    reason: str = ""


class StockAdjustmentCreate(ApiSchema):
    product_id: str
    location_id: str
    new_quantity: str
    reason: str = ""


def _product_schema(p: Product) -> ProductSchema:
    return ProductSchema(
        id=str(p.id),
        sku=p.sku,
        name=p.name,
        category=p.category or "",
        unit=p.unit or "",
        sale_price=money_str(p.sale_price),
        cost_price=money_str(p.cost_price),
        minimum_stock=money_str(p.minimum_stock),
        status=p.status,
        version=p.version or 1,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


# ── Products ─────────────────────────────────────────────────────────


@router.get("/products", response_model=PaginatedResponse[ProductSchema])
async def list_products(
    session: AsyncSession = Depends(get_session),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    params: ListParams = Depends(),
):
    conditions = [Product.tenant_id == tenant.id]
    if params.search:
        like = f"%{params.search}%"
        conditions.append(or_(Product.name.ilike(like), Product.sku.ilike(like), Product.category.ilike(like)))

    where = and_(*conditions)

    total_q = select(func.count(Product.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Product)
        .where(where)
        .order_by(Product.name)
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [_product_schema(p) for p in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/products", response_model=ProductSchema, status_code=201)
async def create_product(
    body: ProductCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    dup = await session.execute(
        select(Product).where(Product.tenant_id == tenant.id, Product.sku == body.sku)
    )
    if dup.scalar_one_or_none():
        raise ConflictError(message=f"SKU '{body.sku}' sudah digunakan")

    now = datetime.now(timezone.utc)
    product = Product(
        id=new_uuid(),
        tenant_id=tenant.id,
        sku=body.sku,
        name=body.name,
        category=body.category or "",
        unit=body.unit or "",
        sale_price=to_money(body.sale_price),
        cost_price=to_money(body.cost_price),
        minimum_stock=to_quantity(body.minimum_stock),
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return _product_schema(product)


@router.get("/products/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    p = await session.execute(
        select(Product).where(Product.id == product_id, Product.tenant_id == tenant.id)
    )
    product = p.scalar_one_or_none()
    if not product:
        raise NotFoundError(message="Produk tidak ditemukan")
    return _product_schema(product)


@router.patch("/products/{product_id}", response_model=ProductSchema)
async def update_product(
    body: ProductUpdate,
    product_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    p = await session.execute(
        select(Product).where(Product.id == product_id, Product.tenant_id == tenant.id)
    )
    product = p.scalar_one_or_none()
    if not product:
        raise NotFoundError(message="Produk tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        if field in ("sale_price", "cost_price"):
            setattr(product, field, to_money(value))
        elif field == "minimum_stock":
            setattr(product, field, to_quantity(value))
        else:
            setattr(product, field, value)
    product.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(product)
    return _product_schema(product)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    p = await session.execute(
        select(Product).where(Product.id == product_id, Product.tenant_id == tenant.id)
    )
    product = p.scalar_one_or_none()
    if not product:
        raise NotFoundError(message="Produk tidak ditemukan")

    cnt = await session.execute(
        select(func.count(StockMovement.id)).where(
            StockMovement.product_id == product_id,
            StockMovement.tenant_id == tenant.id,
        )
    )
    if cnt.scalar() or 0 > 0:
        raise ConflictError(message="Produk memiliki riwayat pergerakan stok")

    await session.delete(product)
    await session.commit()


# ── Stock ─────────────────────────────────────────────────────────────


class InventoryLocationSchema(ApiSchema):
    id: str
    code: str
    name: str
    status: str = "active"
    branch_id: str | None = None


@router.get("/inventory-locations", response_model=list[InventoryLocationSchema], summary="Daftar Lokasi", description="Mengembalikan daftar lokasi inventori milik tenant")
async def list_inventory_locations(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(InventoryLocation)
        .where(InventoryLocation.tenant_id == tenant.id)
        .order_by(InventoryLocation.name)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        InventoryLocationSchema(
            id=str(loc.id),
            code=loc.code,
            name=loc.name,
            status=loc.status,
            branch_id=str(loc.branch_id) if loc.branch_id else None,
        )
        for loc in rows
    ]


@router.get("/stock-balances", response_model=list[StockBalanceSchema])
async def list_stock_balances(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            StockBalance.product_id,
            Product.name,
            Product.sku,
            StockBalance.location_id,
            InventoryLocation.name,
            StockBalance.quantity,
            StockBalance.average_cost,
        )
        .join(Product, and_(
            Product.tenant_id == StockBalance.tenant_id,
            Product.id == StockBalance.product_id,
        ))
        .join(InventoryLocation, and_(
            InventoryLocation.tenant_id == StockBalance.tenant_id,
            InventoryLocation.id == StockBalance.location_id,
        ))
        .where(StockBalance.tenant_id == tenant.id)
        .order_by(Product.name, InventoryLocation.name)
    )
    rows = (await session.execute(stmt)).all()
    return [
        StockBalanceSchema(
            product_id=str(r[0]),
            product_name=r[1],
            sku=r[2],
            location_id=str(r[3]),
            location_name=r[4],
            quantity=money_str(r[5]),
            average_cost=money_str(r[6]),
        )
        for r in rows
    ]


@router.get("/stock-movements", response_model=PaginatedResponse[StockMovementSchema])
async def list_stock_movements(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
):
    conditions = [StockMovement.tenant_id == tenant.id]

    where = and_(*conditions)

    total_q = select(func.count(StockMovement.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(
            StockMovement,
            Product.name.label("product_name"),
            InventoryLocation.name.label("location_name"),
        )
        .join(Product, and_(
            StockMovement.product_id == Product.id,
            Product.tenant_id == tenant.id,
        ))
        .join(InventoryLocation, and_(
            StockMovement.location_id == InventoryLocation.id,
            InventoryLocation.tenant_id == tenant.id,
        ))
        .where(where)
        .order_by(StockMovement.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).all()

    items = [
        StockMovementSchema(
            id=str(m.id),
            movement_number=m.movement_number,
            movement_date=m.movement_date,
            type=m.type,
            product_id=str(m.product_id),
            product_name=product_name,
            location_id=str(m.location_id),
            location_name=location_name,
            quantity=money_str(m.quantity),
            before_stock=money_str(m.before_stock),
            after_stock=money_str(m.after_stock),
            unit_cost=money_str(m.unit_cost),
            reason=m.reason or "",
            reference_type=m.reference_type or "",
            reference_id=str(m.reference_id) if m.reference_id else None,
            journal_entry_id=str(m.journal_entry_id) if m.journal_entry_id else None,
            created_at=m.created_at,
        )
        for m, product_name, location_name in rows
    ]
    return make_paginated(items, params.page, params.page_size, total)


async def _next_movement_number(
    session: AsyncSession,
    tenant_id: str,
) -> str:
    cnt = await session.execute(
        select(func.count(StockMovement.id)).where(StockMovement.tenant_id == tenant_id)
    )
    return f"MOV-{cnt.scalar() or 0 + 1:06d}"


async def _lock_stock_balance(
    session: AsyncSession,
    tenant_id: str,
    product_id: str,
    location_id: str,
) -> StockBalance | None:
    result = await session.execute(
        select(StockBalance).where(
            StockBalance.tenant_id == tenant_id,
            StockBalance.product_id == product_id,
            StockBalance.location_id == location_id,
        ).with_for_update()
    )
    return result.scalar_one_or_none()


@router.post("/stock-movements/receipts", response_model=StockMovementSchema, status_code=201)
async def create_stock_receipt(
    body: StockReceiptCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.execute(
        select(Product).where(Product.id == body.product_id, Product.tenant_id == tenant.id)
    )
    p = product.scalar_one_or_none()
    if not p:
        raise NotFoundError(message="Produk tidak ditemukan")

    loc_result = await session.execute(
        select(InventoryLocation).where(InventoryLocation.id == body.location_id, InventoryLocation.tenant_id == tenant.id)
    )
    location = loc_result.scalar_one_or_none()
    if not location:
        raise NotFoundError(message="Lokasi tidak ditemukan")

    receipt_qty = to_quantity(body.quantity)
    unit_cost = to_money(body.unit_cost)
    today = datetime.now(timezone.utc).date()

    sb = await _lock_stock_balance(session, tenant.id, body.product_id, body.location_id)

    if sb:
        old_qty = sb.quantity
        old_cost = sb.average_cost
        new_qty = old_qty + receipt_qty
        if old_qty > 0:
            new_avg = ((old_qty * old_cost) + (receipt_qty * unit_cost)) / new_qty
        else:
            new_avg = unit_cost
        before_stock = old_qty
        sb.quantity = new_qty
        sb.average_cost = to_money(new_avg)
    else:
        sb = StockBalance(
            tenant_id=tenant.id,
            product_id=body.product_id,
            location_id=body.location_id,
            quantity=receipt_qty,
            average_cost=unit_cost,
        )
        session.add(sb)
        before_stock = ZERO
        new_qty = sb.quantity

    mn = await _next_movement_number(session, tenant.id)
    mov = StockMovement(
        id=new_uuid(),
        tenant_id=tenant.id,
        product_id=body.product_id,
        location_id=body.location_id,
        movement_number=mn,
        movement_date=today,
        type="in",
        quantity=receipt_qty,
        before_stock=before_stock,
        after_stock=new_qty,
        unit_cost=unit_cost,
        reason=body.reason or "Penerimaan stok",
        reference_type="manual",
        reference_id=None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(mov)
    await session.flush()

    if unit_cost > ZERO:
        diff_account = await get_account_by_code(session, tenant.id, GL["stock_diff"])
        await post_stock_movement_journal(
            session=session,
            tenant_id=tenant.id,
            user_id=str(user.id),
            movement=mov,
            counterpart_account=diff_account,
            description=f"Penerimaan stok {p.name} ({mov.movement_number})",
        )

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="stock_movement.receipt",
        module="inventory",
        object_type="stock_movement",
        object_id=str(mov.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"movementNumber": mov.movement_number, "journalEntryId": str(mov.journal_entry_id) if mov.journal_entry_id else None},
    )
    await session.commit()
    await session.refresh(mov)

    return StockMovementSchema(
        id=str(mov.id),
        movement_number=mov.movement_number,
        movement_date=mov.movement_date,
        type=mov.type,
        product_id=str(mov.product_id),
        product_name=p.name,
        location_id=str(mov.location_id),
        location_name=location.name,
        quantity=money_str(mov.quantity),
        before_stock=money_str(mov.before_stock),
        after_stock=money_str(mov.after_stock),
        unit_cost=money_str(mov.unit_cost),
        reason=mov.reason or "",
        reference_type=mov.reference_type or "",
        reference_id=str(mov.reference_id) if mov.reference_id else None,
        journal_entry_id=str(mov.journal_entry_id) if mov.journal_entry_id else None,
        created_at=mov.created_at,
    )


@router.post("/stock-movements/issues", response_model=StockMovementSchema, status_code=201)
async def create_stock_issue(
    body: StockIssueCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.execute(
        select(Product).where(Product.id == body.product_id, Product.tenant_id == tenant.id)
    )
    p = product.scalar_one_or_none()
    if not p:
        raise NotFoundError(message="Produk tidak ditemukan")

    loc = await session.execute(
        select(InventoryLocation).where(InventoryLocation.id == body.location_id, InventoryLocation.tenant_id == tenant.id)
    )
    l = loc.scalar_one_or_none()
    if not l:
        raise NotFoundError(message="Lokasi tidak ditemukan")

    issue_qty = to_quantity(body.quantity)
    today = datetime.now(timezone.utc).date()

    sb = await _lock_stock_balance(session, tenant.id, body.product_id, body.location_id)
    if not sb or sb.quantity < issue_qty:
        raise ValidationError(message="Stok tidak mencukupi")

    before_stock = sb.quantity
    new_qty = sb.quantity - issue_qty
    sb.quantity = new_qty

    mn = await _next_movement_number(session, tenant.id)
    mov = StockMovement(
        id=new_uuid(),
        tenant_id=tenant.id,
        product_id=body.product_id,
        location_id=body.location_id,
        movement_number=mn,
        movement_date=today,
        type="out",
        quantity=issue_qty,
        before_stock=before_stock,
        after_stock=new_qty,
        unit_cost=sb.average_cost,
        reason=body.reason or "Pengeluaran stok",
        reference_type="manual",
        reference_id=None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(mov)
    await session.flush()

    cogs_account = await get_account_by_code(session, tenant.id, GL["cogs"])
    await post_stock_movement_journal(
        session=session,
        tenant_id=tenant.id,
        user_id=str(user.id),
        movement=mov,
        counterpart_account=cogs_account,
        description=f"Pengeluaran stok {p.name} ({mov.movement_number})",
    )

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="stock_movement.issue",
        module="inventory",
        object_type="stock_movement",
        object_id=str(mov.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"movementNumber": mov.movement_number, "journalEntryId": str(mov.journal_entry_id) if mov.journal_entry_id else None},
    )
    await session.commit()
    await session.refresh(mov)

    return StockMovementSchema(
        id=str(mov.id),
        movement_number=mov.movement_number,
        movement_date=mov.movement_date,
        type=mov.type,
        product_id=str(mov.product_id),
        product_name=p.name,
        location_id=str(mov.location_id),
        location_name=l.name,
        quantity=money_str(mov.quantity),
        before_stock=money_str(mov.before_stock),
        after_stock=money_str(mov.after_stock),
        unit_cost=money_str(mov.unit_cost),
        reason=mov.reason or "",
        reference_type=mov.reference_type or "",
        reference_id=str(mov.reference_id) if mov.reference_id else None,
        journal_entry_id=str(mov.journal_entry_id) if mov.journal_entry_id else None,
        created_at=mov.created_at,
    )


@router.post("/stock-movements/adjustments", response_model=StockMovementSchema, status_code=201)
async def create_stock_adjustment(
    body: StockAdjustmentCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.execute(
        select(Product).where(Product.id == body.product_id, Product.tenant_id == tenant.id)
    )
    p = product.scalar_one_or_none()
    if not p:
        raise NotFoundError(message="Produk tidak ditemukan")

    loc = await session.execute(
        select(InventoryLocation).where(InventoryLocation.id == body.location_id, InventoryLocation.tenant_id == tenant.id)
    )
    l = loc.scalar_one_or_none()
    if not l:
        raise NotFoundError(message="Lokasi tidak ditemukan")

    new_qty = to_quantity(body.new_quantity)
    today = datetime.now(timezone.utc).date()

    sb = await _lock_stock_balance(session, tenant.id, body.product_id, body.location_id)

    if sb:
        before_stock = sb.quantity
        diff = new_qty - before_stock
        sb.quantity = new_qty
        if diff >= 0:
            movement_type = "in"
        else:
            movement_type = "out"
            diff = -diff
    else:
        sb = StockBalance(
            tenant_id=tenant.id,
            product_id=body.product_id,
            location_id=body.location_id,
            quantity=new_qty,
            average_cost=ZERO,
        )
        session.add(sb)
        before_stock = ZERO
        diff = new_qty
        movement_type = "in" if new_qty > 0 else "out"

    actual_qty = diff if diff >= ZERO else -diff

    mn = await _next_movement_number(session, tenant.id)
    mov = StockMovement(
        id=new_uuid(),
        tenant_id=tenant.id,
        product_id=body.product_id,
        location_id=body.location_id,
        movement_number=mn,
        movement_date=today,
        type="adjustment",
        quantity=actual_qty,
        before_stock=before_stock,
        after_stock=new_qty,
        unit_cost=sb.average_cost,
        reason=body.reason or "Penyesuaian stok",
        reference_type="adjustment",
        reference_id=None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(mov)
    await session.flush()

    diff_account = await get_account_by_code(session, tenant.id, GL["stock_diff"])
    if sb.average_cost > ZERO:
        await post_stock_movement_journal(
            session=session,
            tenant_id=tenant.id,
            user_id=str(user.id),
            movement=mov,
            counterpart_account=diff_account,
            description=f"Penyesuaian stok {p.name} ({mov.movement_number})",
            effective_type=movement_type,
        )

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="stock_movement.adjustment",
        module="inventory",
        object_type="stock_movement",
        object_id=str(mov.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"movementNumber": mov.movement_number, "journalEntryId": str(mov.journal_entry_id) if mov.journal_entry_id else None},
    )
    await session.commit()
    await session.refresh(mov)

    return StockMovementSchema(
        id=str(mov.id),
        movement_number=mov.movement_number,
        movement_date=mov.movement_date,
        type=mov.type,
        product_id=str(mov.product_id),
        product_name=p.name,
        location_id=str(mov.location_id),
        location_name=l.name,
        quantity=money_str(mov.quantity),
        before_stock=money_str(mov.before_stock),
        after_stock=money_str(mov.after_stock),
        unit_cost=money_str(mov.unit_cost),
        reason=mov.reason or "",
        reference_type=mov.reference_type or "",
        reference_id=str(mov.reference_id) if mov.reference_id else None,
        journal_entry_id=str(mov.journal_entry_id) if mov.journal_entry_id else None,
        created_at=mov.created_at,
    )
