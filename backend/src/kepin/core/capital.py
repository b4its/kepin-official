from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.core.ids import new_uuid
from kepin.core.money import ZERO, to_money
from kepin.db.models import (
    Account,
    FiscalYear,
    JournalEntry,
    JournalLine,
    OrganizationSetting,
)

# Canonical journal number for the tenant's initial capital entry. There is
# exactly one such journal per tenant; it is fully managed by this module so
# that every financial report (neraca, arus kas, buku besar, dashboard) yang
# membaca journal_lines otomatis ikut berubah ketika modal awal diubah.
INITIAL_CAPITAL_JOURNAL_NUMBER = "MODAL-AWAL"

# Default akun yang menampung modal awal. Dibuat otomatis bila belum ada.
CAPITAL_CASH_CODE = "1-1002"
CAPITAL_CASH_DEF = ("Kas", "asset", "debit")
CAPITAL_EQUITY_CODE = "3-1001"
CAPITAL_EQUITY_DEF = ("Modal Disetor", "equity", "credit")


async def _get_or_create_account(
    session: AsyncSession,
    tenant_id: str,
    code: str,
    definition: tuple[str, str, str],
) -> Account:
    account = (
        await session.execute(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.code == code,
            )
        )
    ).scalar_one_or_none()
    if account:
        return account

    name, atype, normal_balance = definition
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
    await session.flush()
    return account


async def _resolve_capital_date(session: AsyncSession, tenant_id: str) -> date:
    """Tanggal jurnal modal awal: awal tahun buku bila ada, else hari ini."""
    fy = (
        await session.execute(
            select(FiscalYear)
            .where(FiscalYear.tenant_id == tenant_id)
            .order_by(FiscalYear.start_date.asc())
        )
    ).scalars().first()
    if fy:
        return fy.start_date
    return datetime.now(timezone.utc).date()


async def get_initial_capital(session: AsyncSession, tenant_id: str) -> Decimal:
    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()
    if not org:
        return ZERO
    return org.initial_capital or ZERO


async def set_initial_capital(
    session: AsyncSession,
    tenant_id: str,
    amount: Decimal,
) -> Decimal:
    """Tetapkan/ubah modal awal tenant.

    Menyimpan nilai di OrganizationSetting lalu membangun ulang satu jurnal
    kanonik ``MODAL-AWAL`` (Debit Kas / Kredit Modal). Karena seluruh laporan
    keuangan diagregasi dari journal_lines, mengubah modal awal otomatis
    memperbarui neraca, arus kas, buku besar, dan dashboard.

    Pemanggil bertanggung jawab melakukan ``session.commit()`` agar operasi
    bersifat atomik bersama audit/side-effect lainnya.
    """
    amount = to_money(amount)
    if amount < ZERO:
        from kepin.api.errors import ValidationError

        raise ValidationError(message="Modal awal tidak boleh negatif")

    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()
    if not org:
        from kepin.api.errors import NotFoundError

        raise NotFoundError(message="Pengaturan organisasi tidak ditemukan")

    org.initial_capital = amount
    org.updated_at = datetime.now(timezone.utc)

    # Hapus jurnal modal awal lama (bila ada) supaya angka lama tidak menumpuk.
    existing = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.journal_number == INITIAL_CAPITAL_JOURNAL_NUMBER,
            )
        )
    ).scalar_one_or_none()
    if existing:
        await session.execute(
            delete(JournalLine).where(
                JournalLine.journal_entry_id == existing.id,
                JournalLine.tenant_id == tenant_id,
            )
        )
        await session.execute(
            delete(JournalEntry).where(JournalEntry.id == existing.id)
        )
        await session.flush()

    # Modal awal nol berarti cukup menghapus jurnal — tidak ada baris baru.
    if amount == ZERO:
        await session.flush()
        return amount

    cash = await _get_or_create_account(
        session, tenant_id, CAPITAL_CASH_CODE, CAPITAL_CASH_DEF
    )
    equity = await _get_or_create_account(
        session, tenant_id, CAPITAL_EQUITY_CODE, CAPITAL_EQUITY_DEF
    )

    now = datetime.now(timezone.utc)
    journal_date = await _resolve_capital_date(session, tenant_id)

    journal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant_id,
        journal_number=INITIAL_CAPITAL_JOURNAL_NUMBER,
        journal_date=journal_date,
        reference="MODAL AWAL",
        description="Setoran modal awal",
        status="posted",
        posted_at=now,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(journal)
    await session.flush()

    session.add(
        JournalLine(
            id=new_uuid(),
            tenant_id=tenant_id,
            journal_entry_id=journal.id,
            account_id=cash.id,
            line_number=1,
            description="Setoran modal awal (kas)",
            debit=amount,
            credit=ZERO,
        )
    )
    session.add(
        JournalLine(
            id=new_uuid(),
            tenant_id=tenant_id,
            journal_entry_id=journal.id,
            account_id=equity.id,
            line_number=2,
            description="Setoran modal awal (modal)",
            debit=ZERO,
            credit=amount,
        )
    )
    await session.flush()
    return amount
