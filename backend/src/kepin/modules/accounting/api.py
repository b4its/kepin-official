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
from kepin.db.models import Account, AccountBalance, JournalEntry, JournalLine, Membership, Transaction, BankAccount, BankTransaction, ReconciliationMatch


router = APIRouter(tags=["Accounting"])


# ── Schemas ──────────────────────────────────────────────────────────


class AccountSchema(ApiSchema):
    id: str
    code: str
    name: str
    type: str
    normal_balance: str
    parent_id: str | None = None
    is_system: bool = False
    allow_posting: bool = True
    status: str = "active"
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AccountCreate(ApiSchema):
    code: str
    name: str
    type: str
    normal_balance: str
    parent_id: str | None = None
    is_system: bool = False
    allow_posting: bool = True


class AccountUpdate(ApiSchema):
    code: str | None = None
    name: str | None = None
    type: str | None = None
    normal_balance: str | None = None
    parent_id: str | None = None
    status: str | None = None
    allow_posting: bool | None = None


class AccountBalanceSchema(ApiSchema):
    account_id: str
    code: str
    name: str
    normal_balance: str
    debit_total: str = "0.00"
    credit_total: str = "0.00"
    balance: str = "0.00"


class TransactionSchema(ApiSchema):
    id: str
    transaction_number: str
    transaction_date: date
    type: str
    description: str
    amount: str
    account_id: str
    counter_account_id: str | None = None
    status: str = "draft"
    branch_id: str | None = None
    reference: str = ""
    journal_entry_id: str | None = None
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TransactionCreate(ApiSchema):
    transaction_date: date
    type: str
    description: str = ""
    amount: str
    account_id: str
    branch_id: str | None = None
    reference: str = ""


class TransactionUpdate(ApiSchema):
    transaction_date: date | None = None
    type: str | None = None
    description: str | None = None
    amount: str | None = None
    account_id: str | None = None
    counter_account_id: str | None = None
    branch_id: str | None = None
    reference: str | None = None


class TransactionPostResponse(ApiSchema):
    id: str
    status: str
    journal_entry_id: str
    transaction_number: str
    message: str = ""


class JournalLineSchema(ApiSchema):
    id: str
    account_id: str
    description: str = ""
    debit: str = "0.00"
    credit: str = "0.00"
    line_number: int = 0


class JournalSchema(ApiSchema):
    id: str
    journal_number: str
    journal_date: str
    reference: str = ""
    description: str = ""
    status: str = "draft"
    posted_at: str | None = None
    branch_id: str | None = None
    version: int = 1
    lines: list[JournalLineSchema] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class JournalCreate(ApiSchema):
    journal_date: date
    branch_id: str | None = None
    reference: str = ""
    description: str = ""
    lines: list[dict] = []


class JournalUpdate(ApiSchema):
    journal_date: date | None = None
    branch_id: str | None = None
    reference: str | None = None
    description: str | None = None
    lines: list[dict] | None = None


class ReconciliationSchema(ApiSchema):
    id: str
    bank_transaction_id: str
    transaction_id: str
    confidence: str = "0.00"
    status: str = "candidate"
    matched_at: str | None = None
    note: str = ""


class ReconciliationCreate(ApiSchema):
    bank_transaction_id: str
    transaction_id: str
    confidence: str = "0.00"
    note: str = ""


# ── Helpers ──────────────────────────────────────────────────────────


def _generate_number(prefix: str = "DOC") -> str:
    ts = datetime.now()
    return f"{prefix}-{ts.strftime('%Y%m%d%H%M%S')}-{ts.microsecond // 1000:03d}"


async def _get_journal_lines(
    session: AsyncSession, journal_entry_id: str, tenant_id: str
) -> list[JournalLine]:
    rows = (
        await session.execute(
            select(JournalLine)
            .where(
                JournalLine.journal_entry_id == journal_entry_id,
                JournalLine.tenant_id == tenant_id,
            )
            .order_by(JournalLine.line_number)
        )
    ).scalars().all()
    return list(rows)


# ═══════════════════════════════════════════════════════════════════════
#  ACCOUNTS
# ═══════════════════════════════════════════════════════════════════════


@router.get("/accounts", response_model=PaginatedResponse[AccountSchema], summary="Daftar Akun", description="Mengembalikan daftar akun dengan pagination, pencarian, dan filter status")
async def list_accounts(
    params: ListParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    status: str | None = Query(None),
):
    filters = [Account.tenant_id == tenant.id]
    if params.search:
        p = f"%{params.search}%"
        filters.append(or_(Account.name.ilike(p), Account.code.ilike(p)))
    if status:
        filters.append(Account.status == status)

    total = (
        await session.execute(
            select(func.count()).select_from(Account).where(and_(*filters))
        )
    ).scalar() or 0

    q = (
        select(Account)
        .where(and_(*filters))
        .order_by(Account.code)
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(q)).scalars().all()
    items = [AccountSchema.model_validate(a) for a in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/accounts", response_model=AccountSchema, status_code=201, summary="Buat Akun", description="Membuat akun baru dalam chart of accounts")
async def create_account(
    body: AccountCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    dup = (
        await session.execute(
            select(Account).where(
                Account.tenant_id == tenant.id, Account.code == body.code
            )
        )
    ).scalar_one_or_none()
    if dup:
        raise ConflictError(message=f"Kode akun '{body.code}' sudah digunakan")

    now = datetime.now(timezone.utc)
    account = Account(
        id=new_uuid(),
        tenant_id=tenant.id,
        code=body.code,
        name=body.name,
        type=body.type,
        normal_balance=body.normal_balance,
        parent_id=body.parent_id,
        is_system=body.is_system,
        allow_posting=body.allow_posting,
        status="active",
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return AccountSchema.model_validate(account)


@router.get("/accounts/{account_id}", response_model=AccountSchema, summary="Detail Akun", description="Mengembalikan detail akun berdasarkan ID")
async def get_account(
    account_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    account = (
        await session.execute(
            select(Account).where(
                Account.id == account_id, Account.tenant_id == tenant.id
            )
        )
    ).scalar_one_or_none()
    if not account:
        raise NotFoundError(message="Akun tidak ditemukan")
    return AccountSchema.model_validate(account)


@router.patch("/accounts/{account_id}", response_model=AccountSchema, summary="Update Akun", description="Memperbarui data akun")
async def update_account(
    body: AccountUpdate,
    account_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    account = (
        await session.execute(
            select(Account).where(
                Account.id == account_id, Account.tenant_id == tenant.id
            )
        )
    ).scalar_one_or_none()
    if not account:
        raise NotFoundError(message="Akun tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    if "code" in patch and patch["code"] != account.code:
        dup = (
            await session.execute(
                select(Account).where(
                    Account.tenant_id == tenant.id,
                    Account.code == patch["code"],
                    Account.id != account_id,
                )
            )
        ).scalar_one_or_none()
        if dup:
            raise ConflictError(
                message=f"Kode akun '{patch['code']}' sudah digunakan"
            )

    for field, value in patch.items():
        setattr(account, field, value)
    account.updated_at = datetime.now(timezone.utc)
    account.version = account.version + 1 if account.version else 2

    await session.commit()
    await session.refresh(account)
    return AccountSchema.model_validate(account)


@router.delete("/accounts/{account_id}", status_code=204, summary="Hapus Akun", description="Menghapus akun (hanya jika tidak memiliki transaksi)")
async def delete_account(
    account_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    account = (
        await session.execute(
            select(Account).where(
                Account.id == account_id, Account.tenant_id == tenant.id
            )
        )
    ).scalar_one_or_none()
    if not account:
        raise NotFoundError(message="Akun tidak ditemukan")

    used = (
        await session.execute(
            select(func.count(JournalLine.id)).where(
                JournalLine.tenant_id == tenant.id,
                JournalLine.account_id == account_id,
            )
        )
    ).scalar() or 0
    if used > 0:
        raise ConflictError(
            message="Akun tidak dapat dihapus karena sudah digunakan dalam jurnal"
        )

    await session.delete(account)
    await session.commit()


@router.get(
    "/accounts/{account_id}/balance", response_model=AccountBalanceSchema,
    summary="Saldo Akun", description="Mengembalikan saldo akun berdasarkan jurnal yang sudah diposting"
)
async def get_account_balance(
    account_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    account = (
        await session.execute(
            select(Account).where(
                Account.id == account_id, Account.tenant_id == tenant.id
            )
        )
    ).scalar_one_or_none()
    if not account:
        raise NotFoundError(message="Akun tidak ditemukan")

    result = await session.execute(
        select(
            func.coalesce(func.sum(JournalLine.debit), 0),
            func.coalesce(func.sum(JournalLine.credit), 0),
        )
        .select_from(JournalLine)
        .join(JournalEntry, JournalEntry.id == JournalLine.journal_entry_id)
        .where(
            JournalLine.tenant_id == tenant.id,
            JournalLine.account_id == account_id,
            JournalEntry.status == "posted",
        )
    )
    debit_total, credit_total = result.one()

    if account.normal_balance == "debit":
        balance = debit_total - credit_total
    else:
        balance = credit_total - debit_total

    return AccountBalanceSchema(
        account_id=str(account.id),
        code=account.code,
        name=account.name,
        normal_balance=account.normal_balance,
        debit_total=money_str(debit_total),
        credit_total=money_str(credit_total),
        balance=money_str(balance),
    )


# ═══════════════════════════════════════════════════════════════════════
#  TRANSACTIONS
# ═══════════════════════════════════════════════════════════════════════


@router.get("/transactions", response_model=PaginatedResponse[TransactionSchema], summary="Daftar Transaksi", description="Mengembalikan daftar transaksi dengan pagination, pencarian, dan filter")
async def list_transactions(
    params: ListParams = Depends(),
    period: PeriodParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    txn_status: str | None = Query(None, alias="status"),
    branch_id: str | None = Query(None),
):
    filters = [Transaction.tenant_id == tenant.id]
    if params.search:
        filters.append(
            Transaction.description.ilike(f"%{params.search}%")
        )
    if txn_status:
        filters.append(Transaction.status == txn_status)
    if branch_id:
        filters.append(Transaction.branch_id == branch_id)

    period_start, period_end = period.resolve()
    if period_start and period_end:
        filters.append(
            and_(
                Transaction.transaction_date >= period_start,
                Transaction.transaction_date <= period_end,
            )
        )

    total = (
        await session.execute(
            select(func.count())
            .select_from(Transaction)
            .where(and_(*filters))
        )
    ).scalar() or 0

    q = (
        select(Transaction)
        .where(and_(*filters))
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(q)).scalars().all()
    items = [TransactionSchema.model_validate(t) for t in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/transactions", response_model=TransactionSchema, status_code=201, summary="Buat Transaksi", description="Membuat transaksi baru (status draft)")
async def create_transaction(
    body: TransactionCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    transaction = Transaction(
        id=new_uuid(),
        tenant_id=tenant.id,
        branch_id=body.branch_id,
        transaction_number=_generate_number("TRX"),
        transaction_date=body.transaction_date,
        type=body.type,
        description=body.description,
        amount=to_money(body.amount),
        account_id=body.account_id,
        status="draft",
        reference=body.reference,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return TransactionSchema.model_validate(transaction)


@router.get("/transactions/{transaction_id}", response_model=TransactionSchema, summary="Detail Transaksi", description="Mengembalikan detail transaksi")
async def get_transaction(
    transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi tidak ditemukan")
    return TransactionSchema.model_validate(txn)


@router.patch("/transactions/{transaction_id}", response_model=TransactionSchema, summary="Update Transaksi", description="Memperbarui transaksi draft")
async def update_transaction(
    body: TransactionUpdate,
    transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi tidak ditemukan")
    if txn.status != "draft":
        raise ValidationError(message="Hanya transaksi draft yang dapat diubah")

    patch = body.model_dump(exclude_unset=True)
    if "amount" in patch:
        patch["amount"] = to_money(patch["amount"])

    for field, value in patch.items():
        setattr(txn, field, value)
    txn.updated_at = datetime.now(timezone.utc)
    txn.version = (txn.version or 1) + 1

    await session.commit()
    await session.refresh(txn)
    return TransactionSchema.model_validate(txn)


@router.delete("/transactions/{transaction_id}", status_code=204, summary="Hapus Transaksi", description="Menghapus transaksi draft")
async def delete_transaction(
    transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi tidak ditemukan")
    if txn.status != "draft":
        raise ValidationError(message="Hanya transaksi draft yang dapat dihapus")

    await session.delete(txn)
    await session.commit()


@router.post(
    "/transactions/{transaction_id}/post", response_model=TransactionSchema,
    summary="Posting Transaksi", description="Memposting transaksi dan membuat jurnal otomatis"
)
async def post_transaction(
    transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi tidak ditemukan")
    if txn.status != "draft":
        raise ValidationError(message="Hanya transaksi draft yang dapat diposting")
    if not txn.counter_account_id:
        raise ValidationError(
            message="Akun lawan harus diisi sebelum diposting"
        )

    now = datetime.now(timezone.utc)
    amount = txn.amount

    journal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant.id,
        branch_id=txn.branch_id,
        journal_number=_generate_number("JNL"),
        journal_date=txn.transaction_date,
        reference=txn.reference or txn.transaction_number,
        description=txn.description,
        status="posted",
        posted_at=now,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(journal)
    await session.flush()

    if txn.type == "income":
        line1 = JournalLine(
            id=new_uuid(),
            tenant_id=tenant.id,
            journal_entry_id=journal.id,
            account_id=txn.counter_account_id,
            line_number=1,
            description=txn.description,
            debit=amount,
            credit=0,
        )
        line2 = JournalLine(
            id=new_uuid(),
            tenant_id=tenant.id,
            journal_entry_id=journal.id,
            account_id=txn.account_id,
            line_number=2,
            description=txn.description,
            debit=0,
            credit=amount,
        )
    else:
        line1 = JournalLine(
            id=new_uuid(),
            tenant_id=tenant.id,
            journal_entry_id=journal.id,
            account_id=txn.account_id,
            line_number=1,
            description=txn.description,
            debit=amount,
            credit=0,
        )
        line2 = JournalLine(
            id=new_uuid(),
            tenant_id=tenant.id,
            journal_entry_id=journal.id,
            account_id=txn.counter_account_id,
            line_number=2,
            description=txn.description,
            debit=0,
            credit=amount,
        )

    session.add_all([line1, line2])
    txn.journal_entry_id = journal.id
    txn.status = "posted"
    txn.updated_at = now
    txn.version = (txn.version or 1) + 1

    await session.commit()
    await session.refresh(txn)
    return TransactionSchema.model_validate(txn)


@router.post(
    "/transactions/{transaction_id}/void", response_model=TransactionSchema,
    summary="Void Transaksi", description="Membatalkan transaksi dengan membuat jurnal reversal"
)
async def void_transaction(
    transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi tidak ditemukan")
    if txn.status != "posted":
        raise ValidationError(
            message="Hanya transaksi posted yang dapat dibatalkan"
        )
    if not txn.journal_entry_id:
        raise ValidationError(message="Transaksi tidak memiliki jurnal terkait")

    original_journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == txn.journal_entry_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not original_journal:
        raise NotFoundError(message="Jurnal terkait tidak ditemukan")

    original_lines = (
        await session.execute(
            select(JournalLine)
            .where(
                JournalLine.journal_entry_id == original_journal.id,
                JournalLine.tenant_id == tenant.id,
            )
            .order_by(JournalLine.line_number)
        )
    ).scalars().all()

    now = datetime.now(timezone.utc)

    reversal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant.id,
        branch_id=txn.branch_id,
        journal_number=_generate_number("JNL"),
        journal_date=txn.transaction_date,
        reference=f"Reversal-{txn.transaction_number}",
        description=f"Pembatalan: {txn.description}",
        status="posted",
        posted_at=now,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(reversal)
    await session.flush()

    reversal_lines = []
    for line in original_lines:
        reversal_lines.append(
            JournalLine(
                id=new_uuid(),
                tenant_id=tenant.id,
                journal_entry_id=reversal.id,
                account_id=line.account_id,
                line_number=line.line_number,
                description=f"Pembatalan: {line.description}",
                debit=line.credit,
                credit=line.debit,
            )
        )
    session.add_all(reversal_lines)

    txn.status = "voided"
    txn.updated_at = now
    txn.version = (txn.version or 1) + 1

    await session.commit()
    await session.refresh(txn)
    return TransactionSchema.model_validate(txn)


# ═══════════════════════════════════════════════════════════════════════
#  JOURNALS
# ═══════════════════════════════════════════════════════════════════════


@router.get("/journals", response_model=PaginatedResponse[JournalSchema], summary="Daftar Jurnal", description="Mengembalikan daftar jurnal dengan pagination dan filter")
async def list_journals(
    params: ListParams = Depends(),
    period: PeriodParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    jnl_status: str | None = Query(None, alias="status"),
):
    filters = [JournalEntry.tenant_id == tenant.id]
    if params.search:
        p = f"%{params.search}%"
        filters.append(
            or_(
                JournalEntry.description.ilike(p),
                JournalEntry.reference.ilike(p),
                JournalEntry.journal_number.ilike(p),
            )
        )
    if jnl_status:
        filters.append(JournalEntry.status == jnl_status)

    period_start, period_end = period.resolve()
    if period_start and period_end:
        filters.append(
            and_(
                JournalEntry.journal_date >= period_start,
                JournalEntry.journal_date <= period_end,
            )
        )

    total = (
        await session.execute(
            select(func.count())
            .select_from(JournalEntry)
            .where(and_(*filters))
        )
    ).scalar() or 0

    q = (
        select(JournalEntry)
        .where(and_(*filters))
        .order_by(JournalEntry.journal_date.desc(), JournalEntry.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    journals = (await session.execute(q)).scalars().all()

    if not journals:
        return make_paginated([], params.page, params.page_size, total)

    journal_ids = [j.id for j in journals]
    all_lines = (
        await session.execute(
            select(JournalLine)
            .where(
                JournalLine.tenant_id == tenant.id,
                JournalLine.journal_entry_id.in_(journal_ids),
            )
            .order_by(JournalLine.journal_entry_id, JournalLine.line_number)
        )
    ).scalars().all()

    from collections import defaultdict
    lines_by_journal: dict[UUID, list[JournalLine]] = defaultdict(list)
    for line in all_lines:
        lines_by_journal[line.journal_entry_id].append(line)

    items = []
    for j in journals:
        lines = lines_by_journal.get(j.id, [])
        items.append(
            JournalSchema(
                id=str(j.id),
                journal_number=j.journal_number,
                journal_date=j.journal_date.isoformat(),
                reference=j.reference,
                description=j.description,
                status=j.status,
                posted_at=j.posted_at.isoformat() if j.posted_at else None,
                branch_id=str(j.branch_id) if j.branch_id else None,
                version=j.version,
                lines=[JournalLineSchema.model_validate(l) for l in lines],
                created_at=j.created_at,
                updated_at=j.updated_at,
            )
        )

    return make_paginated(items, params.page, params.page_size, total)


@router.post("/journals", response_model=JournalSchema, status_code=201, summary="Buat Jurnal", description="Membuat jurnal baru dengan lines debit/kredit")
async def create_journal(
    body: JournalCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    if not body.lines:
        raise ValidationError(message="Jurnal harus memiliki minimal 1 baris")

    now = datetime.now(timezone.utc)

    journal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant.id,
        branch_id=body.branch_id,
        journal_number=_generate_number("JNL"),
        journal_date=body.journal_date,
        reference=body.reference,
        description=body.description,
        status="draft",
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(journal)
    await session.flush()

    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    db_lines = []
    for i, raw in enumerate(body.lines):
        debit = to_money(raw.get("debit", 0))
        credit = to_money(raw.get("credit", 0))
        total_debit += debit
        total_credit += credit
        db_lines.append(
            JournalLine(
                id=new_uuid(),
                tenant_id=tenant.id,
                journal_entry_id=journal.id,
                account_id=raw["account_id"],
                line_number=i + 1,
                description=raw.get("description", ""),
                debit=debit,
                credit=credit,
            )
        )

    if total_debit != total_credit:
        raise ValidationError(
            message=f"Jurnal tidak balanced (debit: {money_str(total_debit)}, "
            f"kredit: {money_str(total_credit)})"
        )

    session.add_all(db_lines)
    await session.commit()
    await session.refresh(journal)

    lines = await _get_journal_lines(session, str(journal.id), tenant.id)
    return JournalSchema(
        id=str(journal.id),
        journal_number=journal.journal_number,
        journal_date=journal.journal_date.isoformat(),
        reference=journal.reference,
        description=journal.description,
        status=journal.status,
        posted_at=None,
        branch_id=str(journal.branch_id) if journal.branch_id else None,
        version=journal.version,
        lines=[JournalLineSchema.model_validate(l) for l in lines],
        created_at=journal.created_at,
        updated_at=journal.updated_at,
    )


@router.get("/journals/{journal_id}", response_model=JournalSchema, summary="Detail Jurnal", description="Mengembalikan detail jurnal beserta lines")
async def get_journal(
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not journal:
        raise NotFoundError(message="Jurnal tidak ditemukan")

    lines = await _get_journal_lines(session, journal_id, tenant.id)
    return JournalSchema(
        id=str(journal.id),
        journal_number=journal.journal_number,
        journal_date=journal.journal_date.isoformat(),
        reference=journal.reference,
        description=journal.description,
        status=journal.status,
        posted_at=journal.posted_at.isoformat() if journal.posted_at else None,
        branch_id=str(journal.branch_id) if journal.branch_id else None,
        version=journal.version,
        lines=[JournalLineSchema.model_validate(l) for l in lines],
        created_at=journal.created_at,
        updated_at=journal.updated_at,
    )


@router.patch("/journals/{journal_id}", response_model=JournalSchema, summary="Update Jurnal", description="Memperbarui jurnal draft")
async def update_journal(
    body: JournalUpdate,
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not journal:
        raise NotFoundError(message="Jurnal tidak ditemukan")
    if journal.status != "draft":
        raise ValidationError(message="Hanya jurnal draft yang dapat diubah")

    patch = body.model_dump(exclude_unset=True)
    lines_data = patch.pop("lines", None)

    for field, value in patch.items():
        setattr(journal, field, value)
    journal.updated_at = datetime.now(timezone.utc)
    journal.version = (journal.version or 1) + 1

    if lines_data is not None:
        existing = (
            await session.execute(
                select(JournalLine).where(
                    JournalLine.journal_entry_id == journal.id,
                    JournalLine.tenant_id == tenant.id,
                )
            )
        ).scalars().all()
        for line in existing:
            await session.delete(line)

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        for i, raw in enumerate(lines_data):
            debit = to_money(raw.get("debit", 0))
            credit = to_money(raw.get("credit", 0))
            total_debit += debit
            total_credit += credit
            session.add(
                JournalLine(
                    id=new_uuid(),
                    tenant_id=tenant.id,
                    journal_entry_id=journal.id,
                    account_id=raw["account_id"],
                    line_number=i + 1,
                    description=raw.get("description", ""),
                    debit=debit,
                    credit=credit,
                )
            )

        if total_debit != total_credit:
            raise ValidationError(
                message=f"Jurnal tidak balanced (debit: {money_str(total_debit)}, "
                f"kredit: {money_str(total_credit)})"
            )

    await session.commit()
    await session.refresh(journal)

    lines = await _get_journal_lines(session, journal_id, tenant.id)
    return JournalSchema(
        id=str(journal.id),
        journal_number=journal.journal_number,
        journal_date=journal.journal_date.isoformat(),
        reference=journal.reference,
        description=journal.description,
        status=journal.status,
        posted_at=journal.posted_at.isoformat() if journal.posted_at else None,
        branch_id=str(journal.branch_id) if journal.branch_id else None,
        version=journal.version,
        lines=[JournalLineSchema.model_validate(l) for l in lines],
        created_at=journal.created_at,
        updated_at=journal.updated_at,
    )


@router.delete("/journals/{journal_id}", status_code=204, summary="Hapus Jurnal", description="Menghapus jurnal draft")
async def delete_journal(
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not journal:
        raise NotFoundError(message="Jurnal tidak ditemukan")
    if journal.status != "draft":
        raise ValidationError(message="Hanya jurnal draft yang dapat dihapus")

    lines = (
        await session.execute(
            select(JournalLine).where(
                JournalLine.journal_entry_id == journal.id,
                JournalLine.tenant_id == tenant.id,
            )
        )
    ).scalars().all()
    for line in lines:
        await session.delete(line)

    await session.delete(journal)
    await session.commit()


@router.post("/journals/{journal_id}/post", response_model=JournalSchema, summary="Posting Jurnal", description="Memposting jurnal (divalidasi balance)")
async def post_journal(
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    journal = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not journal:
        raise NotFoundError(message="Jurnal tidak ditemukan")
    if journal.status != "draft":
        raise ValidationError(message="Hanya jurnal draft yang dapat diposting")

    lines = await _get_journal_lines(session, journal_id, tenant.id)
    if not lines:
        raise ValidationError(message="Jurnal tidak memiliki baris")

    total_debit = sum(l.debit for l in lines)
    total_credit = sum(l.credit for l in lines)
    if total_debit != total_credit:
        raise ValidationError(
            message=f"Jurnal tidak balanced (debit: {money_str(total_debit)}, "
            f"kredit: {money_str(total_credit)})"
        )

    now = datetime.now(timezone.utc)
    journal.status = "posted"
    journal.posted_at = now
    journal.updated_at = now
    journal.version = (journal.version or 1) + 1

    await session.commit()
    await session.refresh(journal)

    return JournalSchema(
        id=str(journal.id),
        journal_number=journal.journal_number,
        journal_date=journal.journal_date.isoformat(),
        reference=journal.reference,
        description=journal.description,
        status=journal.status,
        posted_at=journal.posted_at.isoformat() if journal.posted_at else None,
        branch_id=str(journal.branch_id) if journal.branch_id else None,
        version=journal.version,
        lines=[JournalLineSchema.model_validate(l) for l in lines],
        created_at=journal.created_at,
        updated_at=journal.updated_at,
    )


@router.post("/journals/{journal_id}/reverse", response_model=JournalSchema, summary="Reversal Jurnal", description="Membalik jurnal yang sudah diposting")
async def reverse_journal(
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    original = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not original:
        raise NotFoundError(message="Jurnal tidak ditemukan")
    if original.status != "posted":
        raise ValidationError(
            message="Hanya jurnal posted yang dapat di-reverse"
        )

    original_lines = await _get_journal_lines(
        session, journal_id, tenant.id
    )

    now = datetime.now(timezone.utc)

    reversal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant.id,
        branch_id=original.branch_id,
        journal_number=_generate_number("JNL"),
        journal_date=original.journal_date,
        reference=f"Reverse-{original.journal_number}",
        description=f"Reverse: {original.description}",
        status="posted",
        posted_at=now,
        reversed_entry_id=original.id,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(reversal)
    await session.flush()

    reversal_lines = []
    for i, line in enumerate(original_lines):
        reversal_lines.append(
            JournalLine(
                id=new_uuid(),
                tenant_id=tenant.id,
                journal_entry_id=reversal.id,
                account_id=line.account_id,
                line_number=i + 1,
                description=f"Reverse: {line.description}",
                debit=line.credit,
                credit=line.debit,
            )
        )
    session.add_all(reversal_lines)

    original.status = "reversed"
    original.updated_at = now
    original.version = (original.version or 1) + 1

    await session.commit()
    await session.refresh(reversal)

    lines = await _get_journal_lines(session, str(reversal.id), tenant.id)
    return JournalSchema(
        id=str(reversal.id),
        journal_number=reversal.journal_number,
        journal_date=reversal.journal_date.isoformat(),
        reference=reversal.reference,
        description=reversal.description,
        status=reversal.status,
        posted_at=reversal.posted_at.isoformat() if reversal.posted_at else None,
        branch_id=str(reversal.branch_id) if reversal.branch_id else None,
        version=reversal.version,
        lines=[JournalLineSchema.model_validate(l) for l in lines],
        created_at=reversal.created_at,
        updated_at=reversal.updated_at,
    )


# ═══════════════════════════════════════════════════════════════════════
#  RECONCILIATION
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/reconciliation", response_model=PaginatedResponse[ReconciliationSchema],
    summary="Daftar Rekonsiliasi", description="Mengembalikan daftar rekonsiliasi bank"
)
async def list_reconciliation(
    params: ListParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    status: str | None = Query(None),
):
    filters = [ReconciliationMatch.tenant_id == tenant.id]
    if status:
        filters.append(ReconciliationMatch.status == status)

    total = (
        await session.execute(
            select(func.count())
            .select_from(ReconciliationMatch)
            .where(and_(*filters))
        )
    ).scalar() or 0

    q = (
        select(ReconciliationMatch)
        .where(and_(*filters))
        .order_by(ReconciliationMatch.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(q)).scalars().all()

    items = []
    for r in rows:
        items.append(
            ReconciliationSchema(
                id=str(r.id),
                bank_transaction_id=str(r.bank_transaction_id),
                transaction_id=str(r.transaction_id),
                confidence=money_str(r.confidence),
                status=r.status,
                matched_at=r.matched_at.isoformat() if r.matched_at else None,
                note=r.note,
            )
        )

    return make_paginated(items, params.page, params.page_size, total)


@router.post(
    "/reconciliation/matches",
    response_model=ReconciliationSchema,
    status_code=201,
    summary="Buat Match", description="Mencocokkan transaksi bank dengan transaksi internal",
)
async def create_reconciliation_match(
    body: ReconciliationCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    bank_txn = (
        await session.execute(
            select(BankTransaction).where(
                BankTransaction.id == body.bank_transaction_id,
                BankTransaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not bank_txn:
        raise NotFoundError(message="Bank transaction tidak ditemukan")

    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == body.transaction_id,
                Transaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi tidak ditemukan")

    now = datetime.now(timezone.utc)
    match = ReconciliationMatch(
        id=new_uuid(),
        tenant_id=tenant.id,
        bank_transaction_id=body.bank_transaction_id,
        transaction_id=body.transaction_id,
        confidence=to_money(body.confidence),
        status="candidate",
        note=body.note,
        created_at=now,
        updated_at=now,
    )
    session.add(match)
    await session.commit()
    await session.refresh(match)

    return ReconciliationSchema(
        id=str(match.id),
        bank_transaction_id=str(match.bank_transaction_id),
        transaction_id=str(match.transaction_id),
        confidence=money_str(match.confidence),
        status=match.status,
        matched_at=match.matched_at.isoformat() if match.matched_at else None,
        note=match.note,
    )


@router.post(
    "/reconciliation/matches/{match_id}/confirm",
    response_model=ReconciliationSchema,
    summary="Konfirmasi Match", description="Mengkonfirmasi pencocokan rekonsiliasi",
)
async def confirm_reconciliation_match(
    match_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    match = (
        await session.execute(
            select(ReconciliationMatch).where(
                ReconciliationMatch.id == match_id,
                ReconciliationMatch.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not match:
        raise NotFoundError(message="Reconciliation match tidak ditemukan")
    if match.status == "confirmed":
        raise ValidationError(message="Match sudah dikonfirmasi")

    now = datetime.now(timezone.utc)
    match.status = "confirmed"
    match.matched_at = now
    match.updated_at = now

    await session.commit()
    await session.refresh(match)

    return ReconciliationSchema(
        id=str(match.id),
        bank_transaction_id=str(match.bank_transaction_id),
        transaction_id=str(match.transaction_id),
        confidence=money_str(match.confidence),
        status=match.status,
        matched_at=match.matched_at.isoformat() if match.matched_at else None,
        note=match.note,
    )


@router.delete(
    "/reconciliation/matches/{match_id}", status_code=204,
    summary="Hapus Match", description="Menghapus pencocokan rekonsiliasi",
)
async def delete_reconciliation_match(
    match_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    match = (
        await session.execute(
            select(ReconciliationMatch).where(
                ReconciliationMatch.id == match_id,
                ReconciliationMatch.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not match:
        raise NotFoundError(message="Reconciliation match tidak ditemukan")

    await session.delete(match)
    await session.commit()
