from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from kepin.api.dependencies import get_session, TenantContext, get_tenant_context, get_tenant_membership, require_tenant_owner, ListParams, PeriodParams
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
    Integration,
    BankAccount,
    BankTransaction,
)
from kepin.modules.auth.api import PLANS


router = APIRouter(tags=["Organization"])


def _normalize_role(role: str) -> str:
    if role in ("owner", "tenant_owner"):
        return "tenant_owner"
    if role in ("staff", "employee"):
        return "employee"
    raise ValidationError(message="Role tidak valid")


async def _active_owner_count(session: AsyncSession, tenant_id: str) -> int:
    return (
        await session.execute(
            select(func.count(Membership.id)).where(
                Membership.tenant_id == tenant_id,
                Membership.role_name == "tenant_owner",
                Membership.status == "active",
            )
        )
    ).scalar_one()


async def _assert_owner_can_change(
    session: AsyncSession,
    tenant: TenantContext,
    target: Membership,
    new_role: str | None = None,
) -> None:
    tenant_row = (
        await session.execute(select(Tenant).where(Tenant.id == tenant.id))
    ).scalar_one()
    if str(target.user_id) == str(tenant_row.owner_id):
        raise HTTPException(status_code=403, detail="Pemilik utama tenant harus dipindahkan melalui transfer ownership")
    if target.role_name == "tenant_owner" and new_role != "tenant_owner":
        owners = await _active_owner_count(session, tenant.id)
        if owners <= 1:
            raise ValidationError(message="Tenant harus memiliki minimal satu tenant_owner aktif")


# ── Schemas ──────────────────────────────────────────────────────────


class OrganizationSettingResponse(ApiSchema):
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
    error_message: str | None = None


class IntegrationCreate(ApiSchema):
    provider: str
    display_name: str


class IntegrationUpdate(ApiSchema):
    display_name: str | None = None
    status: str | None = None


class IntegrationSyncItem(ApiSchema):
    external_id: str
    transaction_date: date
    description: str = ""
    amount: str


class IntegrationSyncRequest(ApiSchema):
    bank_account_id: str
    transactions: list[IntegrationSyncItem]


class IntegrationSyncResponse(ApiSchema):
    integration: IntegrationResponse
    imported: int
    skipped: int


class BillingResponse(ApiSchema):
    tenant_id: str
    plan_code: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    features: list[str] = []


class BillingHistoryItemResponse(ApiSchema):
    id: str
    plan_code: str
    plan_name: str
    price: str
    currency: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    created_at: datetime


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/organization", response_model=OrganizationSettingResponse, summary="Pengaturan Organisasi", description="Mengembalikan pengaturan organisasi tenant")
async def get_organization(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    tenant_row = (await session.execute(select(Tenant).where(Tenant.id == tenant.id))).scalar_one()
    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    if not org:
        raise NotFoundError(message="Pengaturan organisasi tidak ditemukan")
    meta = org.org_meta or {}
    return OrganizationSettingResponse(
        tenant_id=str(org.tenant_id),
        tenant_name=tenant_row.name,
        legal_name=org.legal_name,
        tax_id=org.tax_id,
        address=org.address,
        phone=meta.get("phone"),
        email=meta.get("email"),
        website=meta.get("website"),
        logo_url=meta.get("logo_url"),
        timezone=org.timezone,
        currency=org.currency,
        date_format=meta.get("date_format"),
        fiscal_year_start=str(org.fiscal_year_start_month),
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


@router.patch("/organization", response_model=OrganizationSettingResponse, summary="Update Pengaturan", description="Memperbarui pengaturan organisasi tenant")
async def update_organization(
    body: OrganizationSettingUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    if not org:
        raise NotFoundError(message="Pengaturan organisasi tidak ditemukan")

    tenant_row = (await session.execute(select(Tenant).where(Tenant.id == tenant.id))).scalar_one()
    patch = body.model_dump(exclude_unset=True)
    meta = dict(org.org_meta or {})
    for field, value in patch.items():
        if field == "tenant_name":
            tenant_row.name = value
            tenant_row.updated_at = datetime.now(timezone.utc)
        elif field == "fiscal_year_start":
            org.fiscal_year_start_month = int(value)
        elif field in {"phone", "email", "website", "logo_url", "date_format"}:
            meta[field] = value
        elif hasattr(org, field):
            setattr(org, field, value)
    org.org_meta = meta
    org.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(org)
    return OrganizationSettingResponse(
        tenant_id=str(org.tenant_id),
        tenant_name=tenant_row.name,
        legal_name=org.legal_name,
        tax_id=org.tax_id,
        address=org.address,
        phone=meta.get("phone"),
        email=meta.get("email"),
        website=meta.get("website"),
        logo_url=meta.get("logo_url"),
        timezone=org.timezone,
        currency=org.currency,
        date_format=meta.get("date_format"),
        fiscal_year_start=str(org.fiscal_year_start_month),
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


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
    _m: Membership = Depends(require_tenant_owner),
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(require_tenant_owner),
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
    _m: Membership = Depends(require_tenant_owner),
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
    _m: Membership = Depends(require_tenant_owner),
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
    role = _normalize_role(body.role)
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
    actor: Membership = Depends(require_tenant_owner),
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

    if str(membership.id) == str(actor.id):
        raise HTTPException(status_code=403, detail="Tidak dapat mengubah peran sendiri")

    role = _normalize_role(body.role)
    await _assert_owner_can_change(session, tenant, membership, role)
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
    actor: Membership = Depends(require_tenant_owner),
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
    if str(membership.id) == str(actor.id):
        raise HTTPException(status_code=403, detail="Tidak dapat menghapus keanggotaan sendiri")
    await _assert_owner_can_change(session, tenant, membership, None)
    await session.delete(membership)
    await session.commit()


@router.get("/roles", response_model=list[RoleResponse], summary="Daftar Peran", description="Mengembalikan daftar peran yang tersedia")
async def list_roles(
    _m: Membership = Depends(get_tenant_membership),
):
    return [
        {"id": "tenant_owner", "name": "Pemilik"},
        {"id": "employee", "name": "Karyawan"},
    ]


@router.get("/integrations", response_model=list[IntegrationResponse], summary="Daftar Integrasi", description="Mengembalikan daftar integrasi tenant")
async def list_integrations(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(Integration)
            .where(Integration.tenant_id == tenant.id)
            .order_by(Integration.display_name, Integration.provider)
        )
    ).scalars().all()
    return [
        IntegrationResponse(
            id=str(row.id),
            provider=row.provider,
            display_name=row.display_name,
            status=row.status,
            last_synced_at=row.last_synced_at,
            error_message=row.error_message,
        )
        for row in rows
    ]


@router.post("/integrations", response_model=IntegrationResponse, status_code=201, summary="Tambah Integrasi")
async def create_integration(
    body: IntegrationCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
    provider = body.provider.strip().lower()
    display_name = body.display_name.strip()
    if not provider or not display_name:
        raise ValidationError(message="Provider dan nama integrasi wajib diisi")

    integration = Integration(
        id=new_uuid(),
        tenant_id=tenant.id,
        provider=provider,
        display_name=display_name,
        status="disconnected",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(integration)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise ConflictError(message="Provider dan nama integrasi sudah digunakan")
    await session.refresh(integration)
    return IntegrationResponse(
        id=str(integration.id),
        provider=integration.provider,
        display_name=integration.display_name,
        status=integration.status,
        last_synced_at=integration.last_synced_at,
        error_message=integration.error_message,
    )


@router.patch("/integrations/{integration_id}", response_model=IntegrationResponse, summary="Update Integrasi")
async def update_integration(
    body: IntegrationUpdate,
    integration_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
    integration = (
        await session.execute(
            select(Integration).where(
                Integration.id == integration_id,
                Integration.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not integration:
        raise NotFoundError(message="Integrasi tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    if "display_name" in patch:
        display_name = patch["display_name"].strip()
        if not display_name:
            raise ValidationError(message="Nama integrasi wajib diisi")
        integration.display_name = display_name
    if "status" in patch:
        if patch["status"] not in {"active", "disconnected", "error"}:
            raise ValidationError(message="Status integrasi tidak valid")
        integration.status = patch["status"]
    integration.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(integration)
    return IntegrationResponse(
        id=str(integration.id),
        provider=integration.provider,
        display_name=integration.display_name,
        status=integration.status,
        last_synced_at=integration.last_synced_at,
        error_message=integration.error_message,
    )


@router.delete(
    "/integrations/{integration_id}",
    status_code=204,
    summary="Hapus Integrasi",
    description="Menghapus integrasi tenant; transaksi bank yang sudah diimpor tetap tersimpan",
)
async def delete_integration(
    integration_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
    integration = (
        await session.execute(
            select(Integration).where(
                Integration.id == integration_id,
                Integration.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not integration:
        raise NotFoundError(message="Integrasi tidak ditemukan")
    await session.delete(integration)
    await session.commit()
    return Response(status_code=204)


@router.post(
    "/integrations/{integration_id}/sync",
    response_model=IntegrationSyncResponse,
    status_code=200,
    summary="Sinkronisasi Integrasi",
    description="Impor batch transaksi bank dari provider integrasi; hanya untuk integrasi aktif",
)
async def sync_integration(
    body: IntegrationSyncRequest,
    integration_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
    integration = (
        await session.execute(
            select(Integration).where(
                Integration.id == integration_id,
                Integration.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not integration:
        raise NotFoundError(message="Integrasi tidak ditemukan")
    if integration.status != "active":
        raise ValidationError(message="Integrasi tidak aktif; aktifkan terlebih dahulu")

    bank = (
        await session.execute(
            select(BankAccount).where(
                BankAccount.id == body.bank_account_id,
                BankAccount.tenant_id == tenant.id,
                BankAccount.status == "active",
            )
        )
    ).scalar_one_or_none()
    if not bank:
        raise NotFoundError(message="Rekening bank aktif tidak ditemukan")

    existing = set(
        (
            await session.execute(
                select(BankTransaction.external_id).where(
                    BankTransaction.tenant_id == tenant.id,
                    BankTransaction.bank_account_id == bank.id,
                )
            )
        ).scalars().all()
    )

    now = datetime.now(timezone.utc)
    imported = 0
    skipped = 0
    seen: set[str] = set()
    rows: list[BankTransaction] = []
    for item in body.transactions:
        external_id = item.external_id.strip()
        if not external_id or external_id in existing or external_id in seen:
            skipped += 1
            continue
        amount = to_money(item.amount)
        if amount == Decimal("0"):
            raise ValidationError(message="Jumlah transaksi bank tidak boleh nol")
        seen.add(external_id)
        rows.append(
            BankTransaction(
                id=new_uuid(),
                tenant_id=tenant.id,
                bank_account_id=bank.id,
                external_id=external_id,
                transaction_date=item.transaction_date,
                description=item.description.strip(),
                amount=amount,
                raw_payload={"provider": integration.provider, "sync_at": now.isoformat()},
                created_at=now,
            )
        )

    if rows:
        session.add_all(rows)
        imported = len(rows)
    integration.last_synced_at = now
    integration.error_message = None
    integration.updated_at = now
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        integration.error_message = "Sinkronisasi gagal: duplikat external ID dalam satu batch"
        await session.commit()
        raise ConflictError(message="Sinkronisasi gagal: duplikat external ID dalam satu batch")

    return IntegrationSyncResponse(
        integration=IntegrationResponse(
            id=str(integration.id),
            provider=integration.provider,
            display_name=integration.display_name,
            status=integration.status,
            last_synced_at=integration.last_synced_at,
            error_message=integration.error_message,
        ),
        imported=imported,
        skipped=skipped,
    )


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
            features=PLANS["free"]["features"],
        )

    plan = PLANS.get(sub.plan_code, PLANS["free"])
    return BillingResponse(
        tenant_id=tenant.id,
        plan_code=sub.plan_code,
        status=sub.status,
        start_date=sub.current_period_start.date() if sub.current_period_start else None,
        end_date=sub.current_period_end.date() if sub.current_period_end else None,
        features=plan["features"],
    )


@router.get("/billing-history", response_model=list[BillingHistoryItemResponse], summary="Riwayat Langganan", description="Mengembalikan riwayat langganan tenant (semua status, terbaru di atas)")
async def get_billing_history(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(Subscription)
            .where(Subscription.tenant_id == tenant.id)
            .order_by(Subscription.created_at.desc())
        )
    ).scalars().all()

    return [
        BillingHistoryItemResponse(
            id=str(s.id),
            plan_code=s.plan_code,
            plan_name=PLANS.get(s.plan_code, PLANS["free"])["name"],
            price=str(s.amount),
            currency=s.currency,
            status=s.status,
            start_date=s.current_period_start.date() if s.current_period_start else None,
            end_date=s.current_period_end.date() if s.current_period_end else None,
            created_at=s.created_at,
        )
        for s in rows
    ]


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
    membership: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
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
