from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import get_current_user, get_session
from kepin.api.errors import ConflictError, NotFoundError
from kepin.core.auth import create_token, generate_join_code, hash_password, verify_password
from kepin.db.models import Membership, Subscription, Tenant, User
from kepin.modules.auth.schemas import (
    AuthUserResponse,
    CreateOrganizationRequest,
    JoinOrganizationRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)

router = APIRouter(tags=["Auth"])

# ---------------------------------------------------------------------------
# Plan catalogue — single source of truth
# ---------------------------------------------------------------------------

PLANS: dict[str, dict] = {
    "free": {
        "code": "free",
        "name": "Free",
        "price": Decimal("0"),
        "currency": "IDR",
        "billing_period": "monthly",
        "description": "Untuk bisnis yang baru mulai",
        "features": [
            "1 pengguna",
            "Data hingga 100 transaksi/bulan",
            "Laporan dasar",
        ],
        "limits": {"users": 1, "transactions_per_month": 100, "branches": 1},
    },
    "basic": {
        "code": "basic",
        "name": "Basic",
        "price": Decimal("99000"),
        "currency": "IDR",
        "billing_period": "monthly",
        "description": "Untuk usaha kecil yang berkembang",
        "features": [
            "Hingga 5 pengguna",
            "Transaksi tak terbatas",
            "Laporan keuangan lengkap",
            "Manajemen inventori",
        ],
        "limits": {"users": 5, "transactions_per_month": None, "branches": 2},
    },
    "premium": {
        "code": "premium",
        "name": "Premium",
        "price": Decimal("299000"),
        "currency": "IDR",
        "billing_period": "monthly",
        "description": "Untuk bisnis menengah dengan kebutuhan lengkap",
        "features": [
            "Hingga 20 pengguna",
            "Semua fitur Basic",
            "Multi-cabang",
            "API access",
            "Integrasi akuntansi",
            "Prioritas dukungan",
        ],
        "limits": {"users": 20, "transactions_per_month": None, "branches": 10},
    },
    "platinum": {
        "code": "platinum",
        "name": "Platinum",
        "price": Decimal("799000"),
        "currency": "IDR",
        "billing_period": "monthly",
        "description": "Solusi lengkap tanpa batas untuk enterprise",
        "features": [
            "Pengguna tak terbatas",
            "Semua fitur Premium",
            "Cabang tak terbatas",
            "Dedicated support",
            "Custom integrasi",
            "SLA 99,9% uptime",
        ],
        "limits": {"users": None, "transactions_per_month": None, "branches": None},
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _user_tenants(session: AsyncSession, user_id: str) -> list[dict]:
    stmt = (
        select(Tenant, Membership.role_name)
        .join(Membership, Membership.tenant_id == Tenant.id)
        .where(Membership.user_id == user_id, Membership.status == "active")
        .order_by(Tenant.name)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": str(t.id),
            "slug": t.slug,
            "name": t.name,
            "role": role,
            "planCode": t.plan_code,
        }
        for t, role in rows
    ]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/plans", summary="Daftar Paket Langganan")
async def list_plans():
    """Mengembalikan semua paket langganan yang tersedia beserta harga dan fitur."""
    return {
        "plans": [
            {
                **{k: v for k, v in p.items() if k != "limits"},
                "price": str(p["price"]),
                "limits": p["limits"],
            }
            for p in PLANS.values()
        ]
    }


@router.post("/register", status_code=201, summary="Registrasi Pengguna Baru")
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise ConflictError(code="EMAIL_EXISTS", message="Email sudah terdaftar")

    user = User(
        id=str(secrets.token_hex(16)),
        email=body.email,
        name=body.name,
        password_hash=hash_password(body.password),
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(user)
    await session.flush()
    await session.commit()

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "message": "Registrasi berhasil. Silakan buat atau bergabung ke organisasi.",
    }


@router.post("/login", response_model=LoginResponse, summary="Login")
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
        )

    token = create_token(str(user.id))
    tenants = await _user_tenants(session, str(user.id))

    return LoginResponse(
        access_token=token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "avatarUrl": user.avatar_url,
        },
        tenants=tenants,
    )


@router.get("/me", response_model=AuthUserResponse, summary="Profil Pengguna")
async def get_me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    tenants = await _user_tenants(session, str(user.id))
    return AuthUserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        phone=user.phone,
        avatar_url=user.avatar_url,
        tenants=tenants,
    )


@router.post("/create-organization", summary="Buat Organisasi Baru")
async def create_organization(
    body: CreateOrganizationRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Membuat tenant baru. Pengguna yang membuat otomatis menjadi **tenant_owner**.
    Pilih salah satu paket: `free`, `basic`, `premium`, atau `platinum`.
    Response menyertakan `joinCode` yang bisa dibagikan ke anggota lain.
    """
    slug_exists = await session.execute(select(Tenant).where(Tenant.slug == body.slug))
    if slug_exists.scalar_one_or_none():
        raise ConflictError(code="SLUG_EXISTS", message="Slug sudah digunakan")

    plan = PLANS[body.plan]          # body.plan is validated by Literal
    now = datetime.now(timezone.utc)
    join_code = generate_join_code()

    tenant = Tenant(
        id=str(secrets.token_hex(16)),
        owner_id=str(user.id),
        slug=body.slug,
        join_code=join_code,
        name=body.name,
        plan_code=body.plan,
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(tenant)
    await session.flush()

    membership = Membership(
        id=str(secrets.token_hex(16)),
        tenant_id=str(tenant.id),
        user_id=str(user.id),
        role_name="tenant_owner",
        status="active",
        joined_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(membership)

    # Create a subscription record tied to the chosen plan
    subscription = Subscription(
        id=str(secrets.token_hex(16)),
        tenant_id=str(tenant.id),
        plan_code=body.plan,
        status="active",
        started_at=now,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        amount=plan["price"],
        currency=plan["currency"],
        created_at=now,
        updated_at=now,
    )
    session.add(subscription)

    await session.flush()
    await session.commit()

    return {
        "tenant": {
            "id": str(tenant.id),
            "slug": tenant.slug,
            "name": tenant.name,
            "joinCode": tenant.join_code,
            "plan": {
                "code": plan["code"],
                "name": plan["name"],
                "price": str(plan["price"]),
                "billingPeriod": plan["billing_period"],
            },
        },
        "role": "tenant_owner",
        "message": f"Organisasi berhasil dibuat dengan paket {plan['name']}",
    }


@router.post("/join-organization", summary="Bergabung ke Organisasi")
async def join_organization(
    body: JoinOrganizationRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Bergabung ke tenant yang sudah ada menggunakan `tenant_id` dan `join_code`.
    Pengguna akan mendapat role **employee**.
    """
    result = await session.execute(
        select(Tenant).where(
            Tenant.id == body.tenant_id,
            Tenant.join_code == body.join_code,
        )
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundError(
            code="TENANT_NOT_FOUND",
            message="ID tenant atau kode bergabung tidak valid",
        )

    existing = await session.execute(
        select(Membership).where(
            Membership.tenant_id == tenant.id,
            Membership.user_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            code="ALREADY_MEMBER",
            message="Anda sudah menjadi anggota organisasi ini",
        )

    now = datetime.now(timezone.utc)
    membership = Membership(
        id=str(secrets.token_hex(16)),
        tenant_id=str(tenant.id),
        user_id=str(user.id),
        role_name="employee",
        status="active",
        joined_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(membership)
    await session.flush()
    await session.commit()

    return {
        "tenant": {
            "id": str(tenant.id),
            "slug": tenant.slug,
            "name": tenant.name,
            "planCode": tenant.plan_code,
        },
        "role": "employee",
        "message": "Berhasil bergabung ke organisasi",
    }
