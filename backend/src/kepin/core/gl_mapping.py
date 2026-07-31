from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.errors import ValidationError
from kepin.core.ids import new_uuid
from kepin.db.models import Account

# Default GL account codes used by the Central Posting Engine for
# subledger-to-GL integration. These must exist per tenant before posting.
DEFAULT_ACCOUNT_CODES = {
    "ar": "1-2001",
    "inventory": "1-3001",
    "cash": "1-1002",
    "bank": "1-1003",
    "ap": "2-1001",
    "vat_out": "2-2005",
    "vat_in": "1-4006",
    "revenue": "4-1001",
    "cogs": "6-1001",
    "stock_diff": "3-4001",
    "retained_earnings": "3-4002",
}

DEFAULT_ACCOUNT_DEFS = {
    "6-1001": ("Harga Pokok Penjualan", "expense", "debit"),
    "3-4001": ("Selisih Persediaan", "equity", "credit"),
    "3-4002": ("Laba Ditahan", "equity", "credit"),
}


async def get_account_by_code(
    session: AsyncSession,
    tenant_id: str,
    code: str,
) -> Account:
    account = (
        await session.execute(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.code == code,
            )
        )
    ).scalar_one_or_none()
    if not account:
        raise ValidationError(
            message=f"Akun default '{code}' tidak ditemukan. Jalankan backfill akun default."
        )
    return account


async def ensure_gl_defaults(
    session: AsyncSession,
    tenant_id: str,
) -> list[Account]:
    existing = (
        await session.execute(
            select(Account.code).where(
                Account.tenant_id == tenant_id,
                Account.code.in_(list(DEFAULT_ACCOUNT_DEFS.keys())),
            )
        )
    ).scalars().all()
    existing_codes = set(existing)

    created: list[Account] = []
    for code, (name, atype, normal_balance) in DEFAULT_ACCOUNT_DEFS.items():
        if code in existing_codes:
            continue
        account = Account(
            id=new_uuid(),
            tenant_id=tenant_id,
            code=code,
            name=name,
            type=atype,
            normal_balance=normal_balance,
            is_system=True,
            allow_posting=True,
            status="active",
        )
        session.add(account)
        created.append(account)

    if created:
        await session.flush()

    return created


async def get_cash_account_for_method(
    session: AsyncSession,
    tenant_id: str,
    method: str,
) -> Account:
    method = (method or "").lower()
    if any(k in method for k in ("bank", "transfer", "bca", "mandiri", "bni", "bri")):
        return await get_account_by_code(session, tenant_id, DEFAULT_ACCOUNT_CODES["bank"])
    return await get_account_by_code(session, tenant_id, DEFAULT_ACCOUNT_CODES["cash"])
