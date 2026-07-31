from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.errors import ConflictError, ValidationError
from kepin.core.ids import new_uuid
from kepin.core.money import money_str, to_money, ZERO
from kepin.db.models import (
    Account,
    AccountingPeriod,
    IdempotencyKey,
    JournalEntry,
    JournalLine,
)


class PostingResult:
    def __init__(
        self,
        journal_entry: JournalEntry,
        lines: list[JournalLine],
        idempotent: bool = False,
    ):
        self.journal_entry = journal_entry
        self.lines = lines
        self.idempotent = idempotent


async def check_period_open(
    session: AsyncSession,
    tenant_id: str,
    journal_date: datetime.date,
) -> AccountingPeriod:
    period = (
        await session.execute(
            select(AccountingPeriod).where(
                AccountingPeriod.tenant_id == tenant_id,
                AccountingPeriod.start_date <= journal_date,
                AccountingPeriod.end_date >= journal_date,
                AccountingPeriod.status.in_(["open", "soft_closed"]),
            )
        )
    ).scalar_one_or_none()

    if not period:
        raise ValidationError(
            message=f"Tidak ada periode akuntansi yang terbuka untuk tanggal {journal_date.isoformat()}"
        )

    if period.status == "soft_closed":
        raise ValidationError(
            message=f"Periode akuntansi '{period.name}' sedang dalam status soft closed"
        )

    return period


async def check_period_for_posting(
    session: AsyncSession,
    tenant_id: str,
    journal_date: datetime.date,
) -> AccountingPeriod:
    period = (
        await session.execute(
            select(AccountingPeriod).where(
                AccountingPeriod.tenant_id == tenant_id,
                AccountingPeriod.start_date <= journal_date,
                AccountingPeriod.end_date >= journal_date,
            )
        )
    ).scalar_one_or_none()

    if not period:
        raise ValidationError(
            message=f"Tidak ada periode akuntansi yang mencakup tanggal {journal_date.isoformat()}"
        )

    if period.status not in ("open",):
        raise ValidationError(
            message=f"Periode akuntansi '{period.name}' tidak dalam status open (saat ini: {period.status})"
        )

    return period


async def check_idempotency(
    session: AsyncSession,
    tenant_id: str,
    idempotency_key: str | None,
    operation: str,
    source_type: str,
    source_id: str,
) -> IdempotencyKey | None:
    if not idempotency_key:
        return None

    record = (
        await session.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.tenant_id == tenant_id,
                IdempotencyKey.idempotency_key == idempotency_key,
            )
        )
    ).scalar_one_or_none()

    if record:
        if record.status == "completed" and record.source_type == source_type and record.source_id == source_id:
            return record

        raise ConflictError(
            message=f"Idempotency key '{idempotency_key}' sudah digunakan untuk operasi berbeda"
        )

    return None


async def record_idempotency(
    session: AsyncSession,
    tenant_id: str,
    idempotency_key: str,
    operation: str,
    source_type: str,
    source_id: str,
    request_hash: str,
    result_id: str,
    status: str = "completed",
) -> IdempotencyKey:
    record = IdempotencyKey(
        id=new_uuid(),
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        operation=operation,
        source_type=source_type,
        source_id=source_id,
        request_hash=request_hash,
        status=status,
        result_id=result_id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(record)
    return record


async def validate_journal_invariants(
    session: AsyncSession,
    tenant_id: str,
    journal_id: str,
) -> list[JournalLine]:
    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant_id,
            )
        )
    ).scalar_one_or_none()

    if not journal:
        raise ValidationError(message="Jurnal tidak ditemukan")
    if journal.status != "draft":
        raise ValidationError(message="Hanya jurnal draft yang dapat diposting")

    lines = (
        (
            await session.execute(
                select(JournalLine).where(
                    JournalLine.journal_entry_id == journal.id,
                    JournalLine.tenant_id == tenant_id,
                )
            )
        )
        .scalars()
        .all()
    )

    if not lines:
        raise ValidationError(message="Jurnal tidak memiliki baris")

    if len(lines) < 2:
        raise ValidationError(message="Jurnal harus memiliki minimal 2 baris")

    total_debit = ZERO
    total_credit = ZERO
    active_accounts = set()

    for line in lines:
        if line.debit < ZERO or line.credit < ZERO:
            raise ValidationError(message="Nilai debit dan kredit tidak boleh negatif")
        if line.debit == ZERO and line.credit == ZERO:
            raise ValidationError(message="Nilai debit atau kredit harus lebih dari nol")
        if line.debit > ZERO and line.credit > ZERO:
            raise ValidationError(
                message=f"Satu baris tidak boleh memiliki debit dan kredit bersamaan (line {line.line_number})"
            )

        total_debit += line.debit
        total_credit += line.credit
        active_accounts.add(line.account_id)

    if total_debit != total_credit:
        raise ValidationError(
            message=f"Jurnal tidak balanced (debit: {money_str(total_debit)}, kredit: {money_str(total_credit)})"
        )

    for account_id in active_accounts:
        account = (
            await session.execute(
                select(Account).where(
                    Account.id == account_id,
                    Account.tenant_id == tenant_id,
                )
            )
        ).scalar_one_or_none()

        if not account:
            raise ValidationError(message=f"Akun {account_id} tidak ditemukan")
        if account.status != "active":
            raise ValidationError(message=f"Akun '{account.code} - {account.name}' tidak aktif")
        if not account.allow_posting:
            raise ValidationError(message=f"Akun '{account.code} - {account.name}' tidak mengizinkan posting")

    return list(lines)


async def post_journal(
    session: AsyncSession,
    tenant_id: str,
    journal_id: str,
    user_id: str,
    idempotency_key: str | None = None,
    request_hash: str | None = None,
) -> PostingResult:
    if idempotency_key:
        existing = await check_idempotency(
            session=session,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            operation="post_journal",
            source_type="journal",
            source_id=journal_id,
        )
        if existing and existing.status == "completed" and existing.result_id:
            journal = (
                await session.execute(
                    select(JournalEntry).where(JournalEntry.id == existing.result_id)
                )
            ).scalar_one_or_none()
            if journal:
                lines = (
                    (
                        await session.execute(
                            select(JournalLine).where(
                                JournalLine.journal_entry_id == journal.id,
                                JournalLine.tenant_id == tenant_id,
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                return PostingResult(journal, list(lines), idempotent=True)

    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant_id,
            ).with_for_update()
        )
    ).scalar_one_or_none()

    if not journal:
        raise ValidationError(message="Jurnal tidak ditemukan")

    if journal.status != "draft":
        if idempotency_key:
            existing = await check_idempotency(
                session=session,
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
                operation="post_journal",
                source_type="journal",
                source_id=journal_id,
            )
            if existing and existing.status == "completed" and existing.result_id:
                journal = (
                    await session.execute(
                        select(JournalEntry).where(JournalEntry.id == existing.result_id)
                    )
                ).scalar_one_or_none()
                if journal:
                    lines = (
                        (
                            await session.execute(
                                select(JournalLine).where(
                                    JournalLine.journal_entry_id == journal.id,
                                    JournalLine.tenant_id == tenant_id,
                                )
                            )
                        )
                        .scalars()
                        .all()
                    )
                    return PostingResult(journal, list(lines), idempotent=True)
        raise ValidationError(message="Hanya jurnal draft yang dapat diposting")

    lines = await validate_journal_invariants(session, tenant_id, journal_id)

    await check_period_for_posting(session, tenant_id, journal.journal_date)

    now = datetime.now(timezone.utc)
    journal.status = "posted"
    journal.posted_at = now
    journal.posted_by = user_id
    journal.updated_at = now
    journal.version = (journal.version or 1) + 1

    await session.flush()

    if idempotency_key and request_hash:
        await record_idempotency(
            session=session,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            operation="post_journal",
            source_type="journal",
            source_id=journal_id,
            request_hash=request_hash,
            result_id=str(journal.id),
        )

    return PostingResult(journal, lines)


async def post_direct_journal(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    journal_date: datetime.date,
    description: str,
    lines_data: list[dict],
    journal_number: str | None = None,
    reference: str = "",
    branch_id: str | None = None,
    idempotency_key: str | None = None,
    request_hash: str | None = None,
) -> PostingResult:
    if idempotency_key:
        existing = await check_idempotency(
            session=session,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            operation="post_direct_journal",
            source_type="direct",
            source_id="",
        )
        if existing and existing.status == "completed" and existing.result_id:
            journal = (
                await session.execute(
                    select(JournalEntry).where(JournalEntry.id == existing.result_id)
                )
            ).scalar_one_or_none()
            if journal:
                lines = (
                    (
                        await session.execute(
                            select(JournalLine).where(
                                JournalLine.journal_entry_id == journal.id,
                                JournalLine.tenant_id == tenant_id,
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                return PostingResult(journal, list(lines), idempotent=True)

    await check_period_for_posting(session, tenant_id, journal_date)

    if not lines_data or len(lines_data) < 2:
        raise ValidationError(message="Jurnal harus memiliki minimal 2 baris")

    total_debit = ZERO
    total_credit = ZERO

    for i, raw in enumerate(lines_data):
        debit = to_money(raw.get("debit", 0))
        credit = to_money(raw.get("credit", 0))

        if debit < ZERO or credit < ZERO:
            raise ValidationError(message="Nilai debit dan kredit tidak boleh negatif")
        if debit == ZERO and credit == ZERO:
            raise ValidationError(message=f"Baris {i+1}: nilai debit atau kredit harus lebih dari nol")
        if debit > ZERO and credit > ZERO:
            raise ValidationError(message=f"Baris {i+1}: tidak boleh memiliki debit dan kredit bersamaan")

        account = (
            await session.execute(
                select(Account).where(
                    Account.id == raw["account_id"],
                    Account.tenant_id == tenant_id,
                )
            )
        ).scalar_one_or_none()
        if not account:
            raise ValidationError(message=f"Akun {raw['account_id']} tidak ditemukan")
        if account.status != "active":
            raise ValidationError(message=f"Akun '{account.code} - {account.name}' tidak aktif")
        if not account.allow_posting:
            raise ValidationError(message=f"Akun '{account.code} - {account.name}' tidak mengizinkan posting")

        total_debit += debit
        total_credit += credit

    if total_debit != total_credit:
        raise ValidationError(
            message=f"Jurnal tidak balanced (debit: {money_str(total_debit)}, kredit: {money_str(total_credit)})"
        )

    now = datetime.now(timezone.utc)
    journal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        journal_number=journal_number or _generate_journal_number(),
        journal_date=journal_date,
        reference=reference,
        description=description,
        status="posted",
        posted_at=now,
        posted_by=user_id,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(journal)
    await session.flush()

    db_lines = []
    for i, raw in enumerate(lines_data):
        debit = to_money(raw.get("debit", 0))
        credit = to_money(raw.get("credit", 0))
        line = JournalLine(
            id=new_uuid(),
            tenant_id=tenant_id,
            journal_entry_id=journal.id,
            account_id=raw["account_id"],
            line_number=i + 1,
            description=raw.get("description", ""),
            debit=debit,
            credit=credit,
        )
        session.add(line)
        db_lines.append(line)

    await session.flush()

    if idempotency_key and request_hash:
        await record_idempotency(
            session=session,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            operation="post_direct_journal",
            source_type="direct",
            source_id="",
            request_hash=request_hash,
            result_id=str(journal.id),
        )

    return PostingResult(journal, db_lines)


def _generate_journal_number() -> str:
    import uuid
    return f"JNL-{uuid.uuid4().hex[:12].upper()}"
