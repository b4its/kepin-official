from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import get_current_user, get_session
from kepin.api.errors import ConflictError, NotFoundError
from kepin.core.auth import create_token, decode_token, generate_join_code, hash_password, verify_password
from kepin.core.periods import ensure_fiscal_year
from kepin.core.totp import (
    generate_base32_secret,
    generate_recovery_codes,
    hash_recovery_codes,
    otpauth_uri,
    verify_recovery_code,
    verify_totp,
)
from kepin.db.models import Membership, Subscription, Tenant, User
from kepin.modules.auth.schemas import (
    AuthUserResponse,
    ChangePasswordRequest,
    CreateOrganizationRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    JoinByCodeRequest,
    JoinOrganizationRequest,
    LoginRequest,
    LoginResponse,
    MfaDisableRequest,
    MfaEnableRequest,
    MfaEnableResponse,
    MfaSetupResponse,
    MfaStatusResponse,
    MfaVerifyRequest,
    RegenerateJoinCodeRequest,
    RegisterRequest,
    ResetPasswordRequest,
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
            "joinCode": t.join_code,
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

    if user.mfa_enabled:
        mfa_token = create_token(str(user.id), purpose="mfa", expires_minutes=10)
        return LoginResponse(mfa_required=True, mfa_token=mfa_token)

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
            "isSuperadmin": user.is_superadmin,
        },
        tenants=tenants,
    )


@router.post("/mfa/verify", response_model=LoginResponse, summary="Verifikasi Kode MFA saat Login")
async def mfa_verify(body: MfaVerifyRequest, session: AsyncSession = Depends(get_session)):
    """Menyelesaikan login dua langkah: kode TOTP 6 digit atau recovery code."""
    payload = decode_token(body.mfa_token)
    if not payload or payload.get("purpose") != "mfa":
        raise HTTPException(status_code=401, detail="Token verifikasi MFA tidak valid atau kedaluwarsa")

    result = await session.execute(select(User).where(User.id == payload.get("sub")))
    user = result.scalar_one_or_none()
    if not user or not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(status_code=401, detail="MFA tidak aktif untuk akun ini")

    code = body.code.strip()
    if not verify_totp(user.mfa_secret, code):
        matched, remaining = verify_recovery_code(code, user.mfa_recovery_codes)
        if not matched:
            raise HTTPException(status_code=401, detail="Kode verifikasi salah")
        user.mfa_recovery_codes = json.dumps(remaining)
        await session.flush()

    token = create_token(str(user.id))
    tenants = await _user_tenants(session, str(user.id))
    await session.commit()

    return LoginResponse(
        access_token=token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "avatarUrl": user.avatar_url,
            "isSuperadmin": user.is_superadmin,
        },
        tenants=tenants,
    )


@router.get("/mfa/status", response_model=MfaStatusResponse, summary="Status MFA Akun")
async def mfa_status(
    user: User = Depends(get_current_user),
):
    return MfaStatusResponse(enabled=user.mfa_enabled, setup_at=user.mfa_created_at)


@router.post("/mfa/setup", response_model=MfaSetupResponse, summary="Mulai Setup MFA")
async def mfa_setup(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Menghasilkan secret TOTP baru. Secret ini belum aktif sampai /mfa/enable dijalankan."""
    if user.mfa_enabled:
        raise ConflictError(code="MFA_ALREADY_ENABLED", message="MFA sudah aktif")

    secret = generate_base32_secret()
    user.mfa_secret = secret
    user.mfa_recovery_codes = None
    await session.flush()
    await session.commit()

    return MfaSetupResponse(secret=secret, otpauth_uri=otpauth_uri(secret, user.email))


@router.post("/mfa/enable", response_model=MfaEnableResponse, summary="Aktifkan MFA")
async def mfa_enable(
    body: MfaEnableRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Verifikasi kode dari authenticator untuk mengaktifkan MFA. Mengembalikan recovery codes (hanya sekali)."""
    if user.mfa_enabled:
        raise ConflictError(code="MFA_ALREADY_ENABLED", message="MFA sudah aktif")
    if not user.mfa_secret:
        raise HTTPException(status_code=400, detail="Mulai setup MFA terlebih dahulu")

    if not verify_totp(user.mfa_secret, body.code.strip()):
        raise HTTPException(status_code=401, detail="Kode verifikasi salah")

    recovery_codes = generate_recovery_codes()
    user.mfa_enabled = True
    user.mfa_created_at = datetime.now(timezone.utc)
    user.mfa_recovery_codes = hash_recovery_codes(recovery_codes)
    await session.flush()
    await session.commit()

    return MfaEnableResponse(recovery_codes=recovery_codes)


@router.post("/mfa/disable", summary="Nonaktifkan MFA")
async def mfa_disable(
    body: MfaDisableRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Nonaktifkan MFA setelah memverifikasi kode TOTP yang sedang berlaku."""
    if not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA tidak aktif")

    if not verify_totp(user.mfa_secret, body.code.strip()):
        raise HTTPException(status_code=401, detail="Kode verifikasi salah")

    user.mfa_enabled = False
    user.mfa_secret = None
    user.mfa_recovery_codes = None
    user.mfa_created_at = None
    await session.flush()
    await session.commit()

    return {"message": "MFA berhasil dinonaktifkan"}


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/forgot-password", response_model=ForgotPasswordResponse, summary="Minta Reset Password")
async def forgot_password(body: ForgotPasswordRequest, session: AsyncSession = Depends(get_session)):
    """Mengirim token reset password ke email terdaftar (anti-enumerasi).

    Belum ada infrastruktur SMTP, sehingga token dikembalikan dalam response
    sebagai ``devResetToken`` agar alur bisa diuji end-to-end. Saat email
    service tersedia, pengiriman token lewat email menggantikan ini.
    """
    result = await session.execute(select(User).where(User.email == body.email.strip().lower()))
    user = result.scalar_one_or_none()

    if user:
        token = secrets.token_urlsafe(32)
        user.password_reset_token = _hash_reset_token(token)
        user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        await session.flush()
        await session.commit()
        return ForgotPasswordResponse(
            message="Jika email terdaftar, tautan reset akan dikirim.",
            dev_reset_token=token,
        )

    return ForgotPasswordResponse(message="Jika email terdaftar, tautan reset akan dikirim.")


@router.post("/reset-password", summary="Reset Password dengan Token")
async def reset_password(body: ResetPasswordRequest, session: AsyncSession = Depends(get_session)):
    """Mengganti password menggunakan token sekali pakai dari forgot-password."""
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password minimal 8 karakter")

    token_hash = _hash_reset_token(body.token.strip())
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(User).where(User.password_reset_token == token_hash)
    )
    user = result.scalar_one_or_none()
    if not user or not user.password_reset_expires_at or user.password_reset_expires_at < now:
        raise HTTPException(status_code=401, detail="Token reset tidak valid atau sudah kedaluwarsa")

    user.password_hash = hash_password(body.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    await session.flush()
    await session.commit()

    return {"message": "Password berhasil direset. Silakan login dengan password baru."}


@router.post("/change-password", summary="Ganti Password (Saat Login)")
async def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Mengganti password akun setelah memverifikasi password saat ini.

    Catatan: karena JWT bersifat stateless, sesi yang sudah aktif tetap
    berlaku sampai tokennya kedaluwarsa.
    """
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Password saat ini salah")

    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password minimal 8 karakter")

    if verify_password(body.new_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Password baru harus berbeda dari password saat ini")

    user.password_hash = hash_password(body.new_password)
    await session.flush()
    await session.commit()

    return {"message": "Password berhasil diganti"}


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
        is_superadmin=user.is_superadmin,
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

    await ensure_fiscal_year(session, str(tenant.id), ref_date=datetime.now(timezone.utc).date())

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


@router.get("/join-info", summary="Info Organisasi berdasarkan Kode Bergabung")
async def join_info(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    """Mengembalikan informasi organisasi berdasarkan join_code."""
    result = await session.execute(select(Tenant).where(Tenant.join_code == code))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundError(
            code="INVALID_JOIN_CODE",
            message="Kode bergabung tidak valid",
        )
    return {
        "tenant": {
            "id": str(tenant.id),
            "slug": tenant.slug,
            "name": tenant.name,
            "planCode": tenant.plan_code,
        },
    }


@router.post("/join-by-code", summary="Bergabung ke Organisasi via Kode")
async def join_by_code(
    body: JoinByCodeRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Bergabung ke tenant hanya menggunakan join_code."""
    result = await session.execute(
        select(Tenant).where(Tenant.join_code == body.join_code)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundError(
            code="INVALID_JOIN_CODE",
            message="Kode bergabung tidak valid",
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


@router.post("/regenerate-join-code", summary="Perbarui Kode Bergabung")
async def regenerate_join_code(
    body: RegenerateJoinCodeRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Menghasilkan ulang join_code untuk tenant yang dimiliki user."""
    result = await session.execute(
        select(Membership).where(
            Membership.tenant_id == body.tenant_id,
            Membership.user_id == user.id,
            Membership.role_name.in_(["tenant_owner", "admin"]),
            Membership.status == "active",
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pemilik atau admin organisasi yang dapat memperbarui kode bergabung",
        )

    result = await session.execute(select(Tenant).where(Tenant.id == body.tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundError(
            code="TENANT_NOT_FOUND",
            message="Organisasi tidak ditemukan",
        )

    tenant.join_code = generate_join_code()
    tenant.updated_at = datetime.now(timezone.utc)
    await session.flush()
    await session.commit()

    return {
        "joinCode": tenant.join_code,
        "message": "Kode bergabung berhasil diperbarui",
    }
