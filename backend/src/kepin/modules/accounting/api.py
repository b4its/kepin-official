from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
import hashlib
import re
from typing import Any

from kepin.api.dependencies import get_current_user, get_session, TenantContext, get_tenant_context, get_tenant_membership, require_tenant_owner, ListParams, PeriodParams
from kepin.api.errors import NotFoundError, ConflictError, ValidationError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, money_str
from kepin.core.posting import post_journal as posting_engine_post, post_direct_journal
from kepin.core.audit import record_audit
from kepin.core import closing
from kepin.core.periods import build_fiscal_year
from kepin.db.models import Account, AccountBalance, AccountingPeriod, FiscalYear, JournalEntry, JournalLine, Membership, Transaction, User, BankAccount, BankTransaction, ReconciliationMatch


router = APIRouter(tags=["Accounting"])


# ── Schemas ──────────────────────────────────────────────────────────


class AccountSchema(ApiSchema):
    id: UUID
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
    counter_account_id: str | None = None
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


class BankAccountSchema(ApiSchema):
    id: str
    account_id: str
    account_name: str | None = None
    bank_name: str
    masked_number: str = ""
    status: str = "active"
    gl_balance: str = "0.00"
    statement_count: int = 0
    statement_total: str = "0.00"
    unmatched_count: int = 0
    unmatched_total: str = "0.00"


class BankAccountCreate(ApiSchema):
    account_id: str
    bank_name: str
    masked_number: str = ""


class BankAccountUpdate(ApiSchema):
    bank_name: str | None = None
    masked_number: str | None = None
    status: str | None = None


class BankTransactionSchema(ApiSchema):
    id: str
    bank_account_id: str
    external_id: str
    transaction_date: date
    description: str = ""
    amount: str
    matched: bool = False


class MatchCandidateSchema(ApiSchema):
    id: str
    transaction_number: str
    transaction_date: date
    description: str = ""
    amount: str
    score: int


class ReconciliationSuggestionSchema(ApiSchema):
    bank_transaction: BankTransactionSchema
    candidates: list[MatchCandidateSchema]


class BankTransactionCreate(ApiSchema):
    bank_account_id: str
    external_id: str
    transaction_date: date
    description: str = ""
    amount: str


class BankTransactionImportCreate(ApiSchema):
    bank_account_id: str
    csv: str


class BankTransactionImportResult(ApiSchema):
    created: int
    skipped: int
    errors: list[str]


# ── Helpers ──────────────────────────────────────────────────────────


def _journal_statuses():
    """Jurnal yang diperhitungkan (posted + reversed) agar pasangan
    original+reversal netral di saldo akun."""
    return JournalEntry.status.in_(("posted", "reversed"))


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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
            _journal_statuses(),
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
    _m: Membership = Depends(get_tenant_membership),
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
        counter_account_id=body.counter_account_id,
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
    summary="Posting Transaksi", description="Memposting transaksi melalui Central Posting Engine (validasi period, idempotency)"
)
async def post_transaction(
    transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    x_idempotency_key: str | None = Header(None, alias="X-Idempotency-Key"),
):
    txn = (
        await session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant.id,
            ).with_for_update()
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
        status="draft",
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
    await session.flush()

    await posting_engine_post(
        session=session,
        tenant_id=tenant.id,
        journal_id=str(journal.id),
        user_id=str(user.id),
        idempotency_key=x_idempotency_key,
        request_hash=repr({"transaction_id": transaction_id, "type": txn.type, "amount": money_str(amount)}),
    )

    txn.journal_entry_id = journal.id
    txn.status = "posted"
    txn.updated_at = now
    txn.version = (txn.version or 1) + 1

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="transaction.post",
        module="accounting",
        object_type="transaction",
        object_id=str(txn.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"transactionNumber": txn.transaction_number, "journalEntryId": str(journal.id)},
    )
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
    _m: Membership = Depends(require_tenant_owner),
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
        reversed_entry_id=original_journal.id,
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
    account_filter_id: str | None = Query(None, alias="accountId"),
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
    if account_filter_id:
        filters.append(
            JournalEntry.id.in_(
                select(JournalLine.journal_entry_id).where(
                    JournalLine.tenant_id == tenant.id,
                    JournalLine.account_id == account_filter_id,
                )
            )
        )

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
    _m: Membership = Depends(require_tenant_owner),
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
        account_id = raw.get("account_id") or raw.get("accountId")
        if not account_id:
            raise ValidationError(message=f"Baris jurnal {i + 1} belum memilih akun")
        debit = to_money(raw.get("debit", 0))
        credit = to_money(raw.get("credit", 0))
        total_debit += debit
        total_credit += credit
        db_lines.append(
            JournalLine(
                id=new_uuid(),
                tenant_id=tenant.id,
                journal_entry_id=journal.id,
                account_id=account_id,
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(require_tenant_owner),
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
            account_id = raw.get("account_id") or raw.get("accountId")
            if not account_id:
                raise ValidationError(message=f"Baris jurnal {i + 1} belum memilih akun")
            debit = to_money(raw.get("debit", 0))
            credit = to_money(raw.get("credit", 0))
            total_debit += debit
            total_credit += credit
            session.add(
                JournalLine(
                    id=new_uuid(),
                    tenant_id=tenant.id,
                    journal_entry_id=journal.id,
                    account_id=account_id,
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
    _m: Membership = Depends(require_tenant_owner),
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

    await session.execute(
        delete(JournalLine).where(
            JournalLine.journal_entry_id == journal.id,
            JournalLine.tenant_id == tenant.id,
        )
    )
    await session.execute(delete(JournalEntry).where(JournalEntry.id == journal.id))
    await session.commit()


@router.post("/journals/{journal_id}/post", response_model=JournalSchema, summary="Posting Jurnal", description="Memposting jurnal melalui Central Posting Engine (validasi balance, period, idempotency)")
async def post_journal(
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    x_idempotency_key: str | None = Header(None, alias="X-Idempotency-Key"),
):
    result =     await posting_engine_post(
        session=session,
        tenant_id=tenant.id,
        journal_id=journal_id,
        user_id=str(user.id),
        idempotency_key=x_idempotency_key,
        request_hash=repr({"journal_id": journal_id}),
    )

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="journal.post",
        module="accounting",
        object_type="journal_entry",
        object_id=str(result.journal_entry.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={
            "journalNumber": result.journal_entry.journal_number,
            "journalDate": result.journal_entry.journal_date.isoformat(),
        },
    )
    await session.commit()
    await session.refresh(result.journal_entry)

    return JournalSchema(
        id=str(result.journal_entry.id),
        journal_number=result.journal_entry.journal_number,
        journal_date=result.journal_entry.journal_date.isoformat(),
        reference=result.journal_entry.reference,
        description=result.journal_entry.description,
        status=result.journal_entry.status,
        posted_at=result.journal_entry.posted_at.isoformat() if result.journal_entry.posted_at else None,
        branch_id=str(result.journal_entry.branch_id) if result.journal_entry.branch_id else None,
        version=result.journal_entry.version,
        lines=[JournalLineSchema.model_validate(l) for l in result.lines],
        created_at=result.journal_entry.created_at,
        updated_at=result.journal_entry.updated_at,
    )


@router.post("/journals/{journal_id}/reverse", response_model=JournalSchema, summary="Reversal Jurnal", description="Membalik jurnal yang sudah diposting")
async def reverse_journal(
    journal_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
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

    existing_reversal = (
        await session.execute(
            select(JournalEntry.id).where(
                JournalEntry.reversed_entry_id == original.id,
                JournalEntry.tenant_id == tenant.id,
            )
        )
    ).first()
    if existing_reversal:
        raise ValidationError(
            message="Jurnal ini sudah memiliki reversal"
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

    original.updated_at = now
    original.version = (original.version or 1) + 1
    original.status = "reversed"

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="journal.reverse",
        module="accounting",
        object_type="journal_entry",
        object_id=str(original.id),
        actor_id=None,
        actor_name="",
        after={
            "reversalJournalId": str(reversal.id),
            "reversalNumber": reversal.journal_number,
        },
    )
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


@router.get("/bank-accounts", response_model=list[BankAccountSchema], summary="Daftar Rekening Bank")
async def list_bank_accounts(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        await session.execute(
            select(BankAccount, Account.name)
            .join(Account, Account.id == BankAccount.account_id)
            .where(BankAccount.tenant_id == tenant.id, Account.tenant_id == tenant.id)
            .order_by(BankAccount.bank_name)
        )
    ).all()
    bank_ids = [str(bank.id) for bank, _ in rows]
    account_ids = [str(bank.account_id) for bank, _ in rows]

    gl_balances = {}
    if account_ids:
        gl_rows = (
            await session.execute(
                select(JournalLine.account_id, func.sum(JournalLine.debit - JournalLine.credit))
                .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
                .where(
                    JournalLine.tenant_id == tenant.id,
                    JournalEntry.tenant_id == tenant.id,
                    JournalEntry.status.in_(("posted", "reversed")),
                    JournalLine.account_id.in_(account_ids),
                )
                .group_by(JournalLine.account_id)
            )
        ).all()
        gl_balances = {str(account_id): bal for account_id, bal in gl_rows}

    statement_counts = {}
    statement_totals = {}
    unmatched_counts = {}
    unmatched_totals = {}
    if bank_ids:
        cnt_rows = (
            await session.execute(
                select(BankTransaction.bank_account_id, func.count(), func.coalesce(func.sum(BankTransaction.amount), 0))
                .where(
                    BankTransaction.tenant_id == tenant.id,
                    BankTransaction.bank_account_id.in_(bank_ids),
                )
                .group_by(BankTransaction.bank_account_id)
            )
        ).all()
        statement_counts = {str(bank_account_id): n for bank_account_id, n, _ in cnt_rows}
        statement_totals = {str(bank_account_id): total for bank_account_id, _, total in cnt_rows}

        unm_rows = (
            await session.execute(
                select(BankTransaction.bank_account_id, func.count(BankTransaction.id), func.coalesce(func.sum(BankTransaction.amount), 0))
                .outerjoin(
                    ReconciliationMatch,
                    ReconciliationMatch.bank_transaction_id == BankTransaction.id,
                )
                .where(
                    BankTransaction.tenant_id == tenant.id,
                    BankTransaction.bank_account_id.in_(bank_ids),
                    ReconciliationMatch.id.is_(None),
                )
                .group_by(BankTransaction.bank_account_id)
            )
        ).all()
        unmatched_counts = {str(bank_account_id): n for bank_account_id, n, _ in unm_rows}
        unmatched_totals = {str(bank_account_id): total for bank_account_id, _, total in unm_rows}

    return [
        BankAccountSchema(
            id=str(bank.id),
            account_id=str(bank.account_id),
            account_name=account_name,
            bank_name=bank.bank_name,
            masked_number=bank.masked_number,
            status=bank.status,
            gl_balance=money_str(gl_balances.get(str(bank.account_id), Decimal("0"))),
            statement_count=statement_counts.get(str(bank.id), 0),
            statement_total=money_str(statement_totals.get(str(bank.id), Decimal("0"))),
            unmatched_count=unmatched_counts.get(str(bank.id), 0),
            unmatched_total=money_str(unmatched_totals.get(str(bank.id), Decimal("0"))),
        )
        for bank, account_name in rows
    ]


@router.post("/bank-accounts", response_model=BankAccountSchema, status_code=201, summary="Tambah Rekening Bank")
async def create_bank_account(
    body: BankAccountCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
    account = (
        await session.execute(
            select(Account).where(Account.id == body.account_id, Account.tenant_id == tenant.id, Account.status == "active")
        )
    ).scalar_one_or_none()
    if not account:
        raise NotFoundError(message="Akun GL bank tidak ditemukan")
    if account.type != "asset":
        raise ValidationError(message="Rekening bank harus menggunakan akun aset")

    bank = BankAccount(
        id=new_uuid(),
        tenant_id=tenant.id,
        account_id=account.id,
        bank_name=body.bank_name.strip(),
        masked_number=body.masked_number.strip(),
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    if not bank.bank_name:
        raise ValidationError(message="Nama bank wajib diisi")
    session.add(bank)
    await session.commit()
    await session.refresh(bank)
    return BankAccountSchema(
        id=str(bank.id),
        account_id=str(bank.account_id),
        account_name=account.name,
        bank_name=bank.bank_name,
        masked_number=bank.masked_number,
        status=bank.status,
    )


@router.patch(
    "/bank-accounts/{bank_account_id}",
    response_model=BankAccountSchema,
    summary="Update Rekening Bank",
    description="Memperbarui nama bank, nomor tersamarkan, atau status rekening.",
)
async def update_bank_account(
    bank_account_id: str = Path(...),
    body: BankAccountUpdate = ...,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    bank = (
        await session.execute(
            select(BankAccount).where(
                BankAccount.id == bank_account_id,
                BankAccount.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not bank:
        raise NotFoundError(message="Rekening bank tidak ditemukan")

    before = {
        "bankName": bank.bank_name,
        "maskedNumber": bank.masked_number,
        "status": bank.status,
    }
    if body.bank_name is not None:
        bank_name = body.bank_name.strip()
        if not bank_name:
            raise ValidationError(message="Nama bank wajib diisi")
        bank.bank_name = bank_name
    if body.masked_number is not None:
        bank.masked_number = body.masked_number.strip()
    if body.status is not None:
        if body.status not in ("active", "inactive"):
            raise ValidationError(message="Status rekening harus 'active' atau 'inactive'")
        bank.status = body.status
    bank.updated_at = datetime.now(timezone.utc)

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="bank_account.update",
        module="accounting",
        object_type="bank_account",
        object_id=str(bank.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        before=before,
        after={
            "bankName": bank.bank_name,
            "maskedNumber": bank.masked_number,
            "status": bank.status,
        },
    )
    await session.commit()
    await session.refresh(bank)

    account_name = (
        await session.execute(select(Account.name).where(Account.id == bank.account_id))
    ).scalar_one_or_none()
    return BankAccountSchema(
        id=str(bank.id),
        account_id=str(bank.account_id),
        account_name=account_name,
        bank_name=bank.bank_name,
        masked_number=bank.masked_number,
        status=bank.status,
    )


@router.delete(
    "/bank-accounts/{bank_account_id}",
    status_code=204,
    summary="Hapus Rekening Bank",
    description="Menghapus rekening bank (hanya jika tidak memiliki transaksi bank).",
)
async def delete_bank_account(
    bank_account_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    bank = (
        await session.execute(
            select(BankAccount).where(
                BankAccount.id == bank_account_id,
                BankAccount.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not bank:
        raise NotFoundError(message="Rekening bank tidak ditemukan")

    txn_count = (
        await session.execute(
            select(func.count())
            .select_from(BankTransaction)
            .where(BankTransaction.bank_account_id == bank.id)
        )
    ).scalar() or 0
    if txn_count > 0:
        raise ConflictError(message="Tidak dapat menghapus rekening yang memiliki transaksi bank")

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="bank_account.delete",
        module="accounting",
        object_type="bank_account",
        object_id=str(bank.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        before={"bankName": bank.bank_name, "status": bank.status},
    )
    await session.delete(bank)
    await session.commit()


@router.get("/bank-transactions", response_model=PaginatedResponse[BankTransactionSchema], summary="Daftar Transaksi Bank")
async def list_bank_transactions(
    params: ListParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    bank_account_id: str | None = Query(None, alias="bankAccountId"),
):
    filters = [BankTransaction.tenant_id == tenant.id]
    if bank_account_id:
        filters.append(BankTransaction.bank_account_id == bank_account_id)
    if params.search:
        pattern = f"%{params.search.strip()}%"
        filters.append(
            or_(
                BankTransaction.external_id.ilike(pattern),
                BankTransaction.description.ilike(pattern),
            )
        )
    total = (await session.execute(select(func.count()).select_from(BankTransaction).where(and_(*filters)))).scalar() or 0
    rows = (
        await session.execute(
            select(BankTransaction)
            .where(and_(*filters))
            .order_by(BankTransaction.transaction_date.desc(), BankTransaction.created_at.desc())
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )
    ).scalars().all()
    matched_ids = {
        str(x)
        for x in (
            await session.execute(
                select(ReconciliationMatch.bank_transaction_id).where(
                    ReconciliationMatch.tenant_id == tenant.id,
                    ReconciliationMatch.status == "confirmed",
                )
            )
        )
        .scalars()
        .all()
    }
    items = [
        BankTransactionSchema(
            id=str(row.id),
            bank_account_id=str(row.bank_account_id),
            external_id=row.external_id,
            transaction_date=row.transaction_date,
            description=row.description,
            amount=money_str(row.amount),
            matched=str(row.id) in matched_ids,
        )
        for row in rows
    ]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/bank-transactions", response_model=BankTransactionSchema, status_code=201, summary="Impor Transaksi Bank")
async def create_bank_transaction(
    body: BankTransactionCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    session: AsyncSession = Depends(get_session),
):
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
    if not body.external_id.strip():
        raise ValidationError(message="External ID transaksi bank wajib diisi")
    amount = to_money(body.amount)
    if amount == Decimal("0"):
        raise ValidationError(message="Jumlah transaksi bank tidak boleh nol")
    transaction = BankTransaction(
        id=new_uuid(),
        tenant_id=tenant.id,
        bank_account_id=bank.id,
        external_id=body.external_id.strip(),
        transaction_date=body.transaction_date,
        description=body.description.strip(),
        amount=amount,
        raw_payload={},
        created_at=datetime.now(timezone.utc),
    )
    session.add(transaction)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise ConflictError(message="External ID transaksi bank sudah pernah diimpor")
    await session.refresh(transaction)
    return BankTransactionSchema(
        id=str(transaction.id),
        bank_account_id=str(transaction.bank_account_id),
        external_id=transaction.external_id,
        transaction_date=transaction.transaction_date,
        description=transaction.description,
        amount=money_str(transaction.amount),
    )


def _parse_bank_amount(raw: str) -> Decimal:
    s = raw.strip().replace(" ", "").replace("Rp", "").replace("rp", "")
    if "," in s:
        return Decimal(s.replace(".", "").replace(",", "."))
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        return Decimal(s.replace(".", ""))
    return Decimal(s)


@router.post(
    "/bank-transactions/import",
    response_model=BankTransactionImportResult,
    summary="Impor Statement CSV",
    description="Mengimpor transaksi bank dari teks CSV (format: tanggal;deskripsi;jumlah per baris). Idempoten: baris yang sama akan dilewati.",
)
async def import_bank_transactions_csv(
    body: BankTransactionImportCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
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
    if not body.csv.strip():
        raise ValidationError(message="CSV kosong")

    lines = body.csv.strip().splitlines()
    if len(lines) > 200:
        raise ValidationError(message="Maksimal 200 baris per impor")

    now = datetime.now(timezone.utc)
    parsed: list[BankTransaction] = []
    errors: list[str] = []
    for i, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("tanggal") or lower.startswith("date"):
            continue
        parts = line.split(";") if ";" in line else line.split(",")
        if len(parts) != 3:
            errors.append(f"Baris {i}: format salah (butuh tanggal;deskripsi;jumlah)")
            continue
        date_str, desc, amount_str = (p.strip() for p in parts)
        try:
            tdate = date.fromisoformat(date_str)
        except ValueError:
            errors.append(f"Baris {i}: tanggal tidak valid '{date_str}'")
            continue
        if not desc:
            errors.append(f"Baris {i}: deskripsi kosong")
            continue
        try:
            amount = _parse_bank_amount(amount_str)
        except Exception:
            errors.append(f"Baris {i}: jumlah tidak valid '{amount_str}'")
            continue
        if amount == Decimal("0"):
            errors.append(f"Baris {i}: jumlah nol")
            continue
        ext = f"CSV-{hashlib.md5(f'{tdate}|{desc}|{amount}'.encode()).hexdigest()[:10]}"
        parsed.append(
            BankTransaction(
                id=new_uuid(),
                tenant_id=tenant.id,
                bank_account_id=bank.id,
                external_id=ext,
                transaction_date=tdate,
                description=desc,
                amount=amount,
                raw_payload={"source": "csv"},
                created_at=now,
            )
        )

    existing = set(
        (
            await session.execute(
                select(BankTransaction.external_id).where(
                    BankTransaction.tenant_id == tenant.id,
                    BankTransaction.bank_account_id == bank.id,
                    BankTransaction.external_id.in_([t.external_id for t in parsed]),
                )
            )
        )
        .scalars()
        .all()
    )
    to_create = [t for t in parsed if t.external_id not in existing]
    skipped = len(parsed) - len(to_create)

    session.add_all(to_create)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise ConflictError(message="Impor gagal karena bentrok external ID, coba lagi")

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="bank_transaction.import",
        module="accounting",
        object_type="bank_transaction",
        object_id=str(bank.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        before={"bankName": bank.bank_name},
        after={"created": len(to_create), "skipped": skipped, "errors": len(errors)},
    )

    return BankTransactionImportResult(
        created=len(to_create),
        skipped=skipped,
        errors=errors,
    )


@router.delete(
    "/bank-transactions/{bank_transaction_id}",
    status_code=204,
    summary="Hapus Transaksi Bank",
    description="Menghapus transaksi bank yang salah impor (hanya jika belum dicocokkan dalam rekonsiliasi).",
)
async def delete_bank_transaction(
    bank_transaction_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    txn = (
        await session.execute(
            select(BankTransaction).where(
                BankTransaction.id == bank_transaction_id,
                BankTransaction.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not txn:
        raise NotFoundError(message="Transaksi bank tidak ditemukan")

    match_count = (
        await session.execute(
            select(func.count())
            .select_from(ReconciliationMatch)
            .where(ReconciliationMatch.bank_transaction_id == txn.id)
        )
    ).scalar() or 0
    if match_count > 0:
        raise ConflictError(message="Tidak dapat menghapus transaksi yang sudah dicocokkan dengan rekonsiliasi")

    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="bank_transaction.delete",
        module="accounting",
        object_type="bank_transaction",
        object_id=str(txn.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        before={
            "externalId": txn.external_id,
            "amount": money_str(txn.amount),
            "transactionDate": txn.transaction_date.isoformat(),
        },
    )
    await session.delete(txn)
    await session.commit()


@router.get(
    "/reconciliation", response_model=PaginatedResponse[ReconciliationSchema],
    summary="Daftar Rekonsiliasi", description="Mengembalikan daftar rekonsiliasi bank"
)
async def list_reconciliation(
    params: ListParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
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


@router.get(
    "/reconciliation/suggestions",
    response_model=PaginatedResponse[ReconciliationSuggestionSchema],
    summary="Saran Pencocokan",
    description="Mencari kandidat transaksi internal untuk transaksi bank yang belum dicocokkan (amount sama, tanggal berdekatan)",
)
async def reconciliation_suggestions(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    bank_account_id: str | None = Query(None, alias="bankAccountId"),
    date_gap_days: int = Query(7, ge=1, le=30),
):
    matched_sub = select(ReconciliationMatch.bank_transaction_id).where(
        ReconciliationMatch.tenant_id == tenant.id,
        ReconciliationMatch.status == "confirmed",
    )
    filters = [
        BankTransaction.tenant_id == tenant.id,
        ~BankTransaction.id.in_(matched_sub),
    ]
    if bank_account_id:
        filters.append(BankTransaction.bank_account_id == bank_account_id)
    stmts = (
        await session.execute(
            select(BankTransaction)
            .where(and_(*filters))
            .order_by(BankTransaction.transaction_date.desc())
            .limit(50)
        )
    ).scalars().all()

    gap = timedelta(days=date_gap_days)
    items: list[ReconciliationSuggestionSchema] = []
    for stmt in stmts:
        txn_rows = (
            await session.execute(
                select(Transaction)
                .where(
                    Transaction.tenant_id == tenant.id,
                    Transaction.status == "posted",
                    func.abs(Transaction.amount) == abs(stmt.amount),
                    Transaction.transaction_date.between(stmt.transaction_date - gap, stmt.transaction_date + gap),
                )
                .order_by(Transaction.transaction_date.desc())
                .limit(5)
            )
        ).scalars().all()
        if not txn_rows:
            continue
        candidates = []
        for t in txn_rows:
            gap_days = abs((t.transaction_date - stmt.transaction_date).days)
            score = max(20, 100 - gap_days * 5)
            candidates.append(
                MatchCandidateSchema(
                    id=str(t.id),
                    transaction_number=t.transaction_number,
                    transaction_date=t.transaction_date,
                    description=t.description or "",
                    amount=money_str(t.amount),
                    score=score,
                )
            )
        candidates.sort(key=lambda c: (-c.score, c.transaction_date))
        items.append(
            ReconciliationSuggestionSchema(
                bank_transaction=BankTransactionSchema(
                    id=str(stmt.id),
                    bank_account_id=str(stmt.bank_account_id),
                    external_id=stmt.external_id,
                    transaction_date=stmt.transaction_date,
                    description=stmt.description,
                    amount=money_str(stmt.amount),
                    matched=False,
                ),
                candidates=candidates,
            )
        )

    return make_paginated(items, 1, len(items), len(items))


@router.post(
    "/reconciliation/matches",
    response_model=ReconciliationSchema,
    status_code=201,
    summary="Buat Match", description="Mencocokkan transaksi bank dengan transaksi internal",
)
async def create_reconciliation_match(
    body: ReconciliationCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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
    _m: Membership = Depends(get_tenant_membership),
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


# ═══════════════════════════════════════════════════════════════════════
#  FISCAL YEAR & ACCOUNTING PERIODS
# ═══════════════════════════════════════════════════════════════════════


class FiscalYearSchema(ApiSchema):
    id: str
    name: str
    start_date: date
    end_date: date
    status: str
    periods: list[dict] = []


class FiscalYearCreate(ApiSchema):
    name: str | None = None
    start_date: date
    end_date: date


class PeriodSchema(ApiSchema):
    id: str
    name: str
    start_date: date
    end_date: date
    status: str
    closing_journal_id: str | None = None


@router.get("/fiscal-years", response_model=list[FiscalYearSchema], summary="Daftar Tahun Buku", description="Mengembalikan daftar tahun buku beserta periodenya")
async def list_fiscal_years(
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    years = (
        (
            await session.execute(
                select(FiscalYear)
                .where(FiscalYear.tenant_id == tenant.id)
                .order_by(FiscalYear.start_date.desc())
            )
        )
        .scalars()
        .all()
    )

    items = []
    for fy in years:
        periods = (
            (
                await session.execute(
                    select(AccountingPeriod)
                    .where(AccountingPeriod.fiscal_year_id == fy.id)
                    .order_by(AccountingPeriod.start_date)
                )
            )
            .scalars()
            .all()
        )
        items.append(
            FiscalYearSchema(
                id=str(fy.id),
                name=fy.name,
                start_date=fy.start_date,
                end_date=fy.end_date,
                status=fy.status,
                periods=[
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "startDate": p.start_date.isoformat(),
                        "endDate": p.end_date.isoformat(),
                        "status": p.status,
                    }
                    for p in periods
                ],
            )
        )
    return items


@router.post(
    "/fiscal-years",
    response_model=FiscalYearSchema,
    status_code=201,
    summary="Buat Tahun Buku",
    description="Membuat tahun buku baru beserta 12 periode bulanan. Rentang tidak boleh tumpang tindih dengan tahun buku yang sudah ada.",
)
async def create_fiscal_year(
    body: FiscalYearCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if body.start_date > body.end_date:
        raise ValidationError(message="Tanggal mulai harus sebelum tanggal akhir")

    name = (body.name or "").strip() or f"Tahun Buku {body.start_date.year}"
    if len(name) > 80:
        raise ValidationError(message="Nama tahun buku terlalu panjang (maks 80 karakter)")

    overlap = (
        await session.execute(
            select(FiscalYear.id).where(
                FiscalYear.tenant_id == tenant.id,
                FiscalYear.start_date <= body.end_date,
                FiscalYear.end_date >= body.start_date,
            )
        )
    ).scalar_one_or_none()
    if overlap:
        raise ConflictError(message="Sudah ada tahun buku untuk rentang tanggal tersebut")

    same_name = (
        await session.execute(
            select(FiscalYear.id).where(
                FiscalYear.tenant_id == tenant.id,
                FiscalYear.name == name,
            )
        )
    ).scalar_one_or_none()
    if same_name:
        raise ConflictError(message=f"Nama tahun buku '{name}' sudah digunakan")

    fy, periods = await build_fiscal_year(
        session=session,
        tenant_id=tenant.id,
        start_date=body.start_date,
        end_date=body.end_date,
        name=name,
    )
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="fiscal_year.create",
        module="accounting",
        object_type="fiscal_year",
        object_id=str(fy.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={
            "name": fy.name,
            "startDate": fy.start_date.isoformat(),
            "endDate": fy.end_date.isoformat(),
            "periodCount": len(periods),
        },
    )
    await session.commit()

    return FiscalYearSchema(
        id=str(fy.id),
        name=fy.name,
        start_date=fy.start_date,
        end_date=fy.end_date,
        status=fy.status,
        periods=[
            {
                "id": str(p.id),
                "name": p.name,
                "startDate": p.start_date.isoformat(),
                "endDate": p.end_date.isoformat(),
                "status": p.status,
            }
            for p in periods
        ],
    )


@router.post(
    "/fiscal-years/{fiscal_year_id}/close",
    response_model=FiscalYearSchema,
    summary="Tutup Tahun Buku",
    description="Menutup tahun buku. Semua periode harus sudah ditutup terlebih dahulu.",
)
async def close_fiscal_year(
    fiscal_year_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    fy = (
        await session.execute(
            select(FiscalYear).where(
                FiscalYear.id == fiscal_year_id,
                FiscalYear.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not fy:
        raise NotFoundError(message="Tahun buku tidak ditemukan")
    if fy.status == "closed":
        raise ValidationError(message="Tahun buku sudah ditutup")

    open_periods = (
        (
            await session.execute(
                select(AccountingPeriod)
                .where(
                    AccountingPeriod.fiscal_year_id == fy.id,
                    AccountingPeriod.status != "closed",
                )
                .order_by(AccountingPeriod.start_date)
            )
        )
        .scalars()
        .all()
    )
    if open_periods:
        names = ", ".join(p.name for p in open_periods[:5])
        raise ValidationError(
            message=f"Tidak dapat menutup tahun buku selama periode masih terbuka: {names}"
        )

    fy.status = "closed"
    fy.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="fiscal_year.close",
        module="accounting",
        object_type="fiscal_year",
        object_id=str(fy.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"name": fy.name, "status": fy.status},
    )
    await session.commit()
    await session.refresh(fy)
    return FiscalYearSchema(
        id=str(fy.id),
        name=fy.name,
        start_date=fy.start_date,
        end_date=fy.end_date,
        status=fy.status,
        periods=[],
    )


@router.post(
    "/fiscal-years/{fiscal_year_id}/reopen",
    response_model=FiscalYearSchema,
    summary="Buka Kembali Tahun Buku",
    description="Membuka kembali tahun buku yang sudah ditutup (khusus tenant_owner).",
)
async def reopen_fiscal_year(
    fiscal_year_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    fy = (
        await session.execute(
            select(FiscalYear).where(
                FiscalYear.id == fiscal_year_id,
                FiscalYear.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not fy:
        raise NotFoundError(message="Tahun buku tidak ditemukan")
    if fy.status == "open":
        raise ValidationError(message="Tahun buku sudah terbuka")

    locked_periods = (
        (
            await session.execute(
                select(AccountingPeriod.id).where(
                    AccountingPeriod.fiscal_year_id == fy.id,
                    AccountingPeriod.status == "locked",
                )
            )
        )
        .scalars()
        .all()
    )
    if locked_periods:
        raise ValidationError(message="Tahun buku tidak dapat dibuka selama ada periode terkunci")

    fy.status = "open"
    fy.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="fiscal_year.reopen",
        module="accounting",
        object_type="fiscal_year",
        object_id=str(fy.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={"name": fy.name, "status": fy.status},
    )
    await session.commit()
    await session.refresh(fy)
    return FiscalYearSchema(
        id=str(fy.id),
        name=fy.name,
        start_date=fy.start_date,
        end_date=fy.end_date,
        status=fy.status,
        periods=[],
    )


@router.post("/periods/{period_id}/close", response_model=PeriodSchema, summary="Tutup Periode", description="Menutup periode akuntansi (status menjadi closed, laba/rugi ditutup ke Laba Ditahan)")
async def close_period(
    period_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    period = (
        await session.execute(
            select(AccountingPeriod).where(
                AccountingPeriod.id == period_id,
                AccountingPeriod.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not period:
        raise NotFoundError(message="Periode tidak ditemukan")
    if period.status == "closed":
        raise ValidationError(message="Periode sudah ditutup")
    if period.status == "locked":
        raise ValidationError(message="Periode terkunci dan tidak dapat ditutup")

    result = await closing.close_period(
        session=session,
        tenant_id=tenant.id,
        user_id=str(user.id),
        period=period,
    )

    period.status = "closed"
    period.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="period.close",
        module="accounting",
        object_type="accounting_period",
        object_id=str(period.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={
            "name": period.name,
            "status": period.status,
            "closingJournalId": str(result.journal_entry.id) if result else None,
        },
    )
    await session.commit()
    await session.refresh(period)

    return PeriodSchema(
        id=str(period.id),
        name=period.name,
        start_date=period.start_date,
        end_date=period.end_date,
        status=period.status,
        closing_journal_id=str(period.closing_journal_id) if period.closing_journal_id else None,
    )


@router.post("/periods/{period_id}/reopen", response_model=PeriodSchema, summary="Buka Kembali Periode", description="Membuka kembali periode akuntansi (khusus tenant_owner)")
async def reopen_period(
    period_id: str = Path(...),
    tenant: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(require_tenant_owner),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    period = (
        await session.execute(
            select(AccountingPeriod).where(
                AccountingPeriod.id == period_id,
                AccountingPeriod.tenant_id == tenant.id,
            )
        )
    ).scalar_one_or_none()
    if not period:
        raise NotFoundError(message="Periode tidak ditemukan")
    if period.status == "open":
        raise ValidationError(message="Periode sudah terbuka")
    if period.status == "locked":
        raise ValidationError(message="Periode terkunci dan tidak dapat dibuka kembali")

    reversal = await closing.reopen_period(
        session=session,
        tenant_id=tenant.id,
        user_id=str(user.id),
        period=period,
    )

    period.status = "open"
    period.updated_at = datetime.now(timezone.utc)
    await record_audit(
        session=session,
        tenant_id=tenant.id,
        action="period.reopen",
        module="accounting",
        object_type="accounting_period",
        object_id=str(period.id),
        actor_id=user.id,
        actor_name=user.name or user.email,
        after={
            "name": period.name,
            "status": period.status,
            "reversedClosingJournalId": str(reversal.id) if reversal else None,
        },
    )
    await session.commit()
    await session.refresh(period)

    return PeriodSchema(
        id=str(period.id),
        name=period.name,
        start_date=period.start_date,
        end_date=period.end_date,
        status=period.status,
        closing_journal_id=str(period.closing_journal_id) if period.closing_journal_id else None,
    )
