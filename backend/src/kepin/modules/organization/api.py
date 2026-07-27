from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from kepin.api.dependencies import get_session, TenantContext, get_tenant_context, get_tenant_membership, ListParams, PeriodParams
from kepin.api.errors import NotFoundError, ConflictError, ValidationError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, money_str
from kepin.core.time import resolve_period
from kepin.db.models import (
    Tenant,
    OrganizationSetting,
    Branch,
    Membership,
    TenantSidebarSetting,
    User,
    Subscription,
)


router = APIRouter(tags=["Organization"])


# ── Schemas ──────────────────────────────────────────────────────────


class OrganizationSettingResponse(ApiSchema):
    id: str
    tenant_id: str
    tenant_name: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_url: str | None = None
    timezone: str | None = None
    currency: str | None = None
    date_format: str | None = None
    fiscal_year_start: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrganizationSettingUpdate(ApiSchema):
    tenant_name: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_url: str | None = None
    timezone: str | None = None
    currency: str | None = None
    date_format: str | None = None
    fiscal_year_start: str | None = None


class BranchResponse(ApiSchema):
    id: str
    code: str
    name: str
    address: str | None = None
    is_main: bool = False
    status: str = "active"


class BranchCreate(ApiSchema):
    code: str
    name: str
    address: str | None = None


class BranchUpdate(ApiSchema):
    code: str | None = None
    name: str | None = None
    address: str | None = None
    status: str | None = None


class MemberResponse(ApiSchema):
    id: str
    user_id: str
    user_name: str | None = None
    user_email: str | None = None
    role_name: str | None = None
    status: str = "active"
    joined_at: datetime | None = None


class MemberCreate(ApiSchema):
    email: str
    name: str | None = None
    role: str = "staff"


class MemberUpdate(ApiSchema):
    role: str


class RoleResponse(ApiSchema):
    id: str
    name: str


class IntegrationResponse(ApiSchema):
    id: str | None = None
    provider: str | None = None
    display_name: str | None = None
    status: str = "disconnected"
    last_synced_at: datetime | None = None


class BillingResponse(ApiSchema):
    tenant_id: str
    plan_code: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    features: list[str] = []


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/organization", response_model=OrganizationSettingResponse, summary="Pengaturan Organisasi", description="Mengembalikan pengaturan organisasi tenant")
async def get_organization(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    if not org:
        raise NotFoundError(message="Pengaturan organisasi tidak ditemukan")
    return OrganizationSettingResponse.model_validate(org)


@router.patch("/organization", response_model=OrganizationSettingResponse, summary="Update Pengaturan", description="Memperbarui pengaturan organisasi tenant")
async def update_organization(
    body: OrganizationSettingUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    if not org:
        raise NotFoundError(message="Pengaturan organisasi tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(org, field, value)
    org.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(org)
    return OrganizationSettingResponse.model_validate(org)


@router.get("/branches", response_model=list[BranchResponse], summary="Daftar Cabang", description="Mengembalikan daftar cabang tenant")
async def list_branches(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(Branch)
            .where(Branch.tenant_id == tenant.id)
            .order_by(Branch.is_main.desc(), Branch.name)
        )
    ).scalars().all()
    return [BranchResponse.model_validate(b) for b in rows]


@router.post("/branches", response_model=BranchResponse, status_code=201, summary="Buat Cabang", description="Menambahkan cabang baru")
async def create_branch(
    body: BranchCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    dup = (
        await session.execute(
            select(Branch).where(
                Branch.tenant_id == tenant.id,
                Branch.code == body.code,
            )
        )
    ).scalar_one_or_none()
    if dup:
        raise ConflictError(message=f"Kode cabang '{body.code}' sudah digunakan")

    now = datetime.now(timezone.utc)
    branch = Branch(
        id=new_uuid(),
        tenant_id=tenant.id,
        code=body.code,
        name=body.name,
        address=body.address,
        is_main=False,
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    return BranchResponse.model_validate(branch)


@router.get("/branches/{branch_id}", response_model=BranchResponse, summary="Detail Cabang", description="Mengembalikan detail cabang")
async def get_branch(
    branch_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    branch = (
        await session.execute(
            select(Branch).where(
                Branch.id == branch_id,
                Branch.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not branch:
        raise NotFoundError(message="Cabang tidak ditemukan")
    return BranchResponse.model_validate(branch)


@router.patch("/branches/{branch_id}", response_model=BranchResponse, summary="Update Cabang", description="Memperbarui data cabang")
async def update_branch(
    body: BranchUpdate,
    branch_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    branch = (
        await session.execute(
            select(Branch).where(
                Branch.id == branch_id,
                Branch.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not branch:
        raise NotFoundError(message="Cabang tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(branch, field, value)
    branch.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(branch)
    return BranchResponse.model_validate(branch)


@router.delete("/branches/{branch_id}", status_code=204, summary="Hapus Cabang", description="Menghapus cabang")
async def delete_branch(
    branch_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    branch = (
        await session.execute(
            select(Branch).where(
                Branch.id == branch_id,
                Branch.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not branch:
        raise NotFoundError(message="Cabang tidak ditemukan")
    if branch.is_main:
        raise ValidationError(message="Cabang utama tidak dapat dihapus")
    await session.delete(branch)
    await session.commit()


@router.get("/members", response_model=list[MemberResponse], summary="Daftar Anggota", description="Mengembalikan daftar anggota tenant")
async def list_members(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            Membership.id,
            Membership.user_id,
            User.name,
            User.email,
            Membership.role_name,
            Membership.status,
            Membership.joined_at,
        )
        .join(User, User.id == Membership.user_id)
        .where(Membership.tenant_id == tenant.id)
        .order_by(Membership.joined_at)
    )
    rows = (await session.execute(stmt)).all()
    return [
        MemberResponse(
            id=str(r[0]),
            user_id=str(r[1]),
            user_name=r[2],
            user_email=r[3],
            role_name=r[4],
            status=r[5],
            joined_at=r[6],
        )
        for r in rows
    ]


@router.post("/members", response_model=MemberResponse, status_code=201, summary="Tambah Anggota", description="Menambahkan anggota baru ke tenant")
async def add_member(
    body: MemberCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    user = (
        await session.execute(select(User).where(User.email == body.email))
    ).scalar_one_or_none()

    if not user:
        now = datetime.now(timezone.utc)
        user = User(
            id=new_uuid(),
            name=body.name or body.email.split("@")[0],
            email=body.email,
            password_hash="",
            status="active",
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        await session.flush()

    existing = (
        await session.execute(
            select(Membership).where(
                Membership.tenant_id == tenant.id,
                Membership.user_id == user.id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise ConflictError(message="User sudah menjadi anggota tenant ini")

    now = datetime.now(timezone.utc)
    role = "tenant_owner" if body.role == "owner" else "employee"
    membership = Membership(
        id=new_uuid(),
        tenant_id=tenant.id,
        user_id=user.id,
        role_name=role,
        status="active",
        joined_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(membership)
    await session.commit()
    await session.refresh(membership)

    return MemberResponse(
        id=str(membership.id),
        user_id=str(user.id),
        user_name=user.name,
        user_email=user.email,
        role_name=membership.role_name,
        status=membership.status,
        joined_at=membership.joined_at,
    )


@router.patch("/members/{membership_id}", response_model=MemberResponse, summary="Update Anggota", description="Memperbarui peran anggota")
async def update_member_role(
    body: MemberUpdate,
    membership_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    membership = (
        await session.execute(
            select(Membership).where(
                Membership.id == membership_id,
                Membership.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not membership:
        raise NotFoundError(message="Anggota tidak ditemukan")

    role = "tenant_owner" if body.role == "owner" else "employee"
    membership.role_name = role
    membership.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(membership)

    user = (
        await session.execute(select(User).where(User.id == membership.user_id))
    ).scalar_one_or_none()

    return MemberResponse(
        id=str(membership.id),
        user_id=str(membership.user_id) if user else "",
        user_name=user.name if user else None,
        user_email=user.email if user else None,
        role_name=membership.role_name,
        status=membership.status,
        joined_at=membership.joined_at,
    )


@router.delete("/members/{membership_id}", status_code=204, summary="Hapus Anggota", description="Menghapus anggota dari tenant")
async def remove_member(
    membership_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    membership = (
        await session.execute(
            select(Membership).where(
                Membership.id == membership_id,
                Membership.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not membership:
        raise NotFoundError(message="Anggota tidak ditemukan")
    await session.delete(membership)
    await session.commit()


@router.get("/roles", response_model=list[RoleResponse], summary="Daftar Peran", description="Mengembalikan daftar peran yang tersedia")
async def list_roles():
    return [
        {"id": "tenant_owner", "name": "Pemilik"},
        {"id": "employee", "name": "Karyawan"},
    ]


@router.get("/integrations", response_model=list[IntegrationResponse], summary="Daftar Integrasi", description="Mengembalikan daftar integrasi tenant")
async def list_integrations(
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    return []


@router.get("/billing", response_model=BillingResponse, summary="Informasi Tagihan", description="Mengembalikan informasi langganan dan tagihan tenant")
async def get_billing(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    sub = (
        await session.execute(
            select(Subscription)
            .where(
                Subscription.tenant_id == tenant.id,
                Subscription.status == "active",
            )
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if not sub:
        return BillingResponse(
            tenant_id=tenant.id,
            plan_code="free",
            status="none",
            features=[],
        )

    return BillingResponse(
        tenant_id=tenant.id,
        plan_code=sub.plan_code,
        status=sub.status,
        start_date=sub.current_period_start.date() if sub.current_period_start else None,
        end_date=sub.current_period_end.date() if sub.current_period_end else None,
        features=[],
    )


# ── Sidebar Settings ──────────────────────────────────────────────────────


@router.get("/sidebar-settings", summary="Pengaturan Sidebar", description="Mengembalikan pengaturan visibilitas item sidebar untuk tenant")
async def get_sidebar_settings(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    row = (
        await session.execute(
            select(TenantSidebarSetting).where(TenantSidebarSetting.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    enabled_items = row.enabled_items if row else {}
    return {"tenantId": str(tenant.id), "enabledItems": enabled_items}


@router.put("/sidebar-settings", summary="Simpan Pengaturan Sidebar", description="Menyimpan pengaturan visibilitas item sidebar (hanya tenant_owner)")
async def update_sidebar_settings(
    body: dict,
    tenant: TenantContext = Depends(get_tenant_context),
    membership: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    if membership.role_name != "tenant_owner":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Hanya tenant_owner yang dapat mengubah pengaturan sidebar")

    enabled_items: dict = body.get("enabledItems", {})
    now = datetime.now(timezone.utc)

    row = (
        await session.execute(
            select(TenantSidebarSetting).where(TenantSidebarSetting.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()

    if row:
        row.enabled_items = enabled_items
        row.updated_at = now
        row.updated_by = membership.user_id
    else:
        row = TenantSidebarSetting(
            tenant_id=tenant.id,
            enabled_items=enabled_items,
            updated_at=now,
            updated_by=membership.user_id,
        )
        session.add(row)

    await session.commit()
    return {"tenantId": str(tenant.id), "enabledItems": enabled_items, "message": "Pengaturan sidebar berhasil disimpan"}
