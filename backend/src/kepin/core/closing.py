from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.errors import ValidationError
from kepin.core.gl_mapping import (
    DEFAULT_ACCOUNT_CODES as GL,
    get_account_by_code,
)
from kepin.core.money import to_money, ZERO
from kepin.core.posting import PostingResult, post_direct_journal
from kepin.core.subledger import reverse_posted_journal
from kepin.db.models import Account, AccountingPeriod, JournalEntry, JournalLine


async def close_period(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    period: AccountingPeriod,
) -> PostingResult | None:
    """Tutup periode: pindahkan laba/rugi ke Laba Ditahan via jurnal penutup.

    Membuat jurnal penutup CLS-<periode> yang menolkan akun income/expense
    pada rentang periode dan mengkredit/mendebit Laba Ditahan (3-4002).
    Tidak membuat jurnal bila tidak ada aktivitas laba/rugi di periode tsb.
    """
    rows = (
        (
            await session.execute(
                select(
                    Account.id,
                    Account.code,
                    Account.type,
                    func.coalesce(func.sum(JournalLine.debit), 0).label("debit_total"),
                    func.coalesce(func.sum(JournalLine.credit), 0).label("credit_total"),
                )
                .select_from(JournalLine)
                .join(JournalEntry, JournalEntry.id == JournalLine.journal_entry_id)
                .join(Account, and_(Account.id == JournalLine.account_id, Account.tenant_id == tenant_id))
                .where(
                    JournalEntry.tenant_id == tenant_id,
                    JournalEntry.status.in_(("posted", "reversed")),
                    JournalEntry.journal_date.between(period.start_date, period.end_date),
                    Account.type.in_(["income", "expense"]),
                )
                .group_by(Account.id, Account.code, Account.type)
            )
        )
        .all()
    )

    lines_data: list[dict] = []
    total_dr = ZERO
    total_cr = ZERO
    for account_id, code, atype, debit_total, credit_total in rows:
        debit_total = debit_total or ZERO
        credit_total = credit_total or ZERO
        if atype == "income":
            net = credit_total - debit_total
            if net <= ZERO:
                continue
            lines_data.append(
                {
                    "account_id": str(account_id),
                    "debit": to_money(net),
                    "credit": ZERO,
                    "description": f"Penutupan {code}",
                }
            )
            total_dr += net
        else:
            net = debit_total - credit_total
            if net <= ZERO:
                continue
            lines_data.append(
                {
                    "account_id": str(account_id),
                    "debit": ZERO,
                    "credit": to_money(net),
                    "description": f"Penutupan {code}",
                }
            )
            total_cr += net

    if not lines_data:
        return None

    retained = await get_account_by_code(session, tenant_id, GL["retained_earnings"])
    if total_dr >= total_cr:
        lines_data.append(
            {
                "account_id": str(retained.id),
                "debit": ZERO,
                "credit": to_money(total_dr - total_cr),
                "description": "Laba berjalan ditutup ke Laba Ditahan",
            }
        )
    else:
        lines_data.append(
            {
                "account_id": str(retained.id),
                "debit": to_money(total_cr - total_dr),
                "credit": ZERO,
                "description": "Rugi berjalan ditutup ke Laba Ditahan",
            }
        )

    existing_closes = (
        await session.execute(
            select(func.count())
            .select_from(JournalEntry)
            .where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.journal_number.like(f"CLS-{period.name}%"),
            )
        )
    ).scalar() or 0
    journal_number = (
        f"CLS-{period.name}"
        if existing_closes == 0
        else f"CLS-{period.name}-{existing_closes + 1}"
    )

    result = await post_direct_journal(
        session=session,
        tenant_id=tenant_id,
        user_id=user_id,
        journal_date=period.end_date,
        description=f"Penutupan periode {period.name}",
        lines_data=lines_data,
        journal_number=journal_number,
    )

    period.closing_journal_id = result.journal_entry.id
    period.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return result


async def reopen_period(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    period: AccountingPeriod,
) -> JournalEntry | None:
    """Buka kembali periode: reverse jurnal penutup CLS-<periode> bila ada."""
    if not period.closing_journal_id:
        return None

    reversal = await reverse_posted_journal(
        session=session,
        tenant_id=tenant_id,
        journal_id=str(period.closing_journal_id),
        description_prefix="Retur penutupan periode",
    )

    period.closing_journal_id = None
    period.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return reversal


def is_closing_journal(journal_number: str | None) -> bool:
    return bool(journal_number and (journal_number.startswith("CLS-") or journal_number.startswith("REV-CLS-")))
