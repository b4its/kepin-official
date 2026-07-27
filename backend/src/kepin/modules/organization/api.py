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
    OrganizationSetting,
    Branch,
    Membership,
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


@router.get("/organization", response_model=OrganizationSettingResponse)
async def get_organization(
    tenant: TenantContext = Depends(get_tenant_context),
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


@router.patch("/organization", response_model=OrganizationSettingResponse)
async def update_organization(
    body: OrganizationSettingUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
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


@router.get("/branches", response_model=list[BranchResponse])
async def list_branches(
    tenant: TenantContext = Depends(get_tenant_context),
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


@router.post("/branches", response_model=BranchResponse, status_code=201)
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


@router.get("/branches/{branch_id}", response_model=BranchResponse)
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


@router.patch("/branches/{branch_id}", response_model=BranchResponse)
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


@router.delete("/branches/{branch_id}", status_code=204)
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


@router.get("/members", response_model=list[MemberResponse])
async def list_members(
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            Membership.id,
            Membership.user_id,
            User.name,
            User.email,
            Membership.role,
            Membership.status,
            Membership.created_at,
        )
        .join(User, User.id == Membership.user_id)
        .where(Membership.tenant_id == tenant.id)
        .order_by(Membership.created_at)
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


@router.post("/members", response_model=MemberResponse, status_code=201)
async def add_member(
    body: MemberCreate,
    tenant: TenantContext = Depends(get_tenant_context),
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
    membership = Membership(
        id=new_uuid(),
        tenant_id=tenant.id,
        user_id=user.id,
        role=body.role,
        status="active",
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
        role_name=membership.role,
        status=membership.status,
        joined_at=membership.created_at,
    )


@router.patch("/members/{membership_id}", response_model=MemberResponse)
async def update_member_role(
    body: MemberUpdate,
    membership_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
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

    membership.role = body.role
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
        role_name=membership.role,
        status=membership.status,
        joined_at=membership.created_at,
    )


@router.delete("/members/{membership_id}", status_code=204)
async def remove_member(
    membership_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
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


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles():
    return [
        {"id": "owner", "name": "Pemilik"},
        {"id": "manager", "name": "Manajer"},
        {"id": "accountant", "name": "Akuntan"},
        {"id": "staff", "name": "Staf"},
        {"id": "viewer", "name": "Viewer"},
    ]


@router.get("/integrations", response_model=list[IntegrationResponse])
async def list_integrations(
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    return []


@router.get("/billing", response_model=BillingResponse)
async def get_billing(
    tenant: TenantContext = Depends(get_tenant_context),
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
        start_date=sub.start_date,
        end_date=sub.end_date,
        features=[],
    )
