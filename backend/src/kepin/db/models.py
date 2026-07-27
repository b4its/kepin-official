from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    Uuid,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kepin.db.base import Base


# ---------------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------------


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    legal_name: Mapped[str] = mapped_column(String(200), default="")
    sector: Mapped[str] = mapped_column(String(80), default="")
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Jakarta")
    currency: Mapped[str] = mapped_column(String(3), default="IDR")
    plan_code: Mapped[str] = mapped_column(String(40), default="trial")
    status: Mapped[str] = mapped_column(
        String(24),
        CheckConstraint("status IN ('active', 'trial', 'suspended')", name="ck_tenant_status"),
        default="trial",
    )
    onboarding_status: Mapped[str] = mapped_column(String(24), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(32), default="")
    avatar_url: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(24), default="active")
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    role_name: Mapped[str] = mapped_column(String(40))
    permissions: Mapped[dict] = mapped_column(JSONB, default={})
    status: Mapped[str] = mapped_column(String(24), default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class Plan(Base):
    __tablename__ = "plans"

    code: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    billing_period: Mapped[str] = mapped_column(String(24))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3), default="IDR")
    entitlements: Mapped[dict] = mapped_column(JSONB, default={})
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), unique=True)
    plan_code: Mapped[str] = mapped_column(String(40), ForeignKey("plans.code"))
    status: Mapped[str] = mapped_column(String(24))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class SubscriptionEvent(Base):
    __tablename__ = "subscription_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    subscription_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("subscriptions.id"))
    event_type: Mapped[str] = mapped_column(String(40))
    buyer_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    buyer_name_snapshot: Mapped[str] = mapped_column(String(160), default="")
    buyer_email_snapshot: Mapped[str] = mapped_column(String(255), default="")
    plan_code: Mapped[str] = mapped_column(String(40))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_meta: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    severity: Mapped[str] = mapped_column(String(24))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner: Mapped[str] = mapped_column(String(100), default="")
    timeline: Mapped[list] = mapped_column(JSONB, default=[])
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class PlatformAuditEvent(Base):
    __tablename__ = "platform_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    actor_name: Mapped[str] = mapped_column(String(160), default="")
    action: Mapped[str] = mapped_column(String(80))
    object_type: Mapped[str] = mapped_column(String(80))
    object_id: Mapped[str] = mapped_column(String(80), default="")
    before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    request_id: Mapped[str] = mapped_column(String(80), default="")
    correlation_id: Mapped[str] = mapped_column(String(80), default="")
    audit_meta: Mapped[dict] = mapped_column("metadata", JSONB, default={})


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    event_type: Mapped[str] = mapped_column(String(80))
    aggregate_type: Mapped[str] = mapped_column(String(80), default="")
    aggregate_id: Mapped[str] = mapped_column(String(80), default="")
    payload: Mapped[dict] = mapped_column(JSONB)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------


class OrganizationSetting(Base):
    __tablename__ = "organization_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(200), default="")
    tax_id: Mapped[str] = mapped_column(String(40), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Jakarta")
    currency: Mapped[str] = mapped_column(String(3), default="IDR")
    fiscal_year_start_month: Mapped[int] = mapped_column(Integer, default=1)
    invoice_prefix: Mapped[str] = mapped_column(String(16), default="INV")
    po_prefix: Mapped[str] = mapped_column(String(16), default="PO")
    org_meta: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class Integration(Base):
    __tablename__ = "integrations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "provider", "display_name", name="uq_integration_tenant_provider_display"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    provider: Mapped[str] = mapped_column(String(40))
    display_name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="active")
    config_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class Branch(Base):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_branch_code_tenant"),
        UniqueConstraint("tenant_id", "id", name="uq_branch_tenant_id"),
        Index("uq_branch_main_per_tenant", "tenant_id", "is_main", postgresql_where=text("is_main = true")),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    code: Mapped[str] = mapped_column(String(24))
    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str] = mapped_column(Text, default="")
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


# ---------------------------------------------------------------------------
# Accounting
# ---------------------------------------------------------------------------


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_account_tenant_id"),
        UniqueConstraint("tenant_id", "code", name="uq_account_code_tenant"),
        ForeignKeyConstraint(
            ["tenant_id", "parent_id"],
            ["accounts.tenant_id", "accounts.id"],
            name="fk_account_parent",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(
        String(24),
        CheckConstraint("type IN ('asset', 'liability', 'equity', 'income', 'expense')", name="ck_account_type"),
    )
    normal_balance: Mapped[str] = mapped_column(
        String(8),
        CheckConstraint("normal_balance IN ('debit', 'credit')", name="ck_account_normal_balance"),
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_posting: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(
        String(16),
        CheckConstraint("status IN ('active', 'inactive')", name="ck_account_status"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )
    version: Mapped[int] = mapped_column(Integer, default=1)


class AccountBalance(Base):
    __tablename__ = "account_balances"
    __table_args__ = (
        PrimaryKeyConstraint("tenant_id", "account_id", "branch_id", "period_date", name="pk_account_balances"),
        ForeignKeyConstraint(
            ["tenant_id", "account_id"],
            ["accounts.tenant_id", "accounts.id"],
            name="fk_account_balances_account",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "branch_id"],
            ["branches.tenant_id", "branches.id"],
            name="fk_account_balances_branch",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    period_date: Mapped[date] = mapped_column(Date)
    debit_total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    credit_total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "journal_number", name="uq_journal_entry_number_tenant"),
        Index("ix_journal_entries_tenant_date_status", "tenant_id", "journal_date", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    journal_number: Mapped[str] = mapped_column(String(40))
    journal_date: Mapped[date] = mapped_column(Date)
    reference: Mapped[str] = mapped_column(String(80), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(24),
        CheckConstraint("status IN ('draft', 'posted', 'reversed')", name="ck_journal_entry_status"),
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    reversed_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("journal_entries.id"), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )
    version: Mapped[int] = mapped_column(Integer, default=1)


class JournalLine(Base):
    __tablename__ = "journal_lines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "journal_entry_id", "line_number", name="uq_journal_line_entry_line"),
        CheckConstraint("debit >= 0", name="ck_journal_line_debit"),
        CheckConstraint("credit >= 0", name="ck_journal_line_credit"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("journal_entries.id"))
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    line_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")
    debit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "transaction_number", name="uq_transaction_number_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    transaction_number: Mapped[str] = mapped_column(String(40))
    transaction_date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(
        String(24),
        CheckConstraint("type IN ('income', 'expense', 'transfer')", name="ck_transaction_type"),
    )
    description: Mapped[str] = mapped_column(Text, default="")
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    counter_account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(24),
        CheckConstraint("status IN ('draft', 'posted', 'voided')", name="ck_transaction_status"),
    )
    reference: Mapped[str] = mapped_column(String(80), default="")
    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("journal_entries.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )
    version: Mapped[int] = mapped_column(Integer, default=1)


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    bank_name: Mapped[str] = mapped_column(String(160))
    masked_number: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "bank_account_id", "external_id", name="uq_bank_txn_external"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    bank_account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bank_accounts.id"))
    external_id: Mapped[str] = mapped_column(String(80))
    transaction_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(255), default="")
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    raw_payload: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )


class ReconciliationMatch(Base):
    __tablename__ = "reconciliation_matches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    bank_transaction_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bank_transactions.id"))
    transaction_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("transactions.id"))
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    status: Mapped[str] = mapped_column(String(24), default="candidate")
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


# ---------------------------------------------------------------------------
# Sales
# ---------------------------------------------------------------------------


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_customer_code_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    tax_id: Mapped[str] = mapped_column(String(40), default="")
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_number", name="uq_invoice_number_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(40))
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customers.id"))
    invoice_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("journal_entries.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )
    version: Mapped[int] = mapped_column(Integer, default=1)


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_id", "line_number", name="uq_invoice_line_invoice_line"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    invoice_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("invoices.id"))
    line_number: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("products.id"), nullable=True)
    item_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    unit: Mapped[str] = mapped_column(String(16), default="")
    unit_price: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(20, 2))


class CustomerPayment(Base):
    __tablename__ = "customer_payments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    payment_number: Mapped[str] = mapped_column(String(40))
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customers.id"))
    payment_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    method: Mapped[str] = mapped_column(String(40), default="")
    reference: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(24), default="draft")
    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("journal_entries.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class CustomerPaymentAllocation(Base):
    __tablename__ = "customer_payment_allocations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "payment_id", "invoice_id", name="uq_payment_alloc_payment_invoice"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    payment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customer_payments.id"))
    invoice_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("invoices.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))


# ---------------------------------------------------------------------------
# Purchasing
# ---------------------------------------------------------------------------


class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_supplier_code_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    tax_id: Mapped[str] = mapped_column(String(40), default="")
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "po_number", name="uq_purchase_order_po_tenant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    po_number: Mapped[str] = mapped_column(String(40))
    supplier_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("suppliers.id"))
    order_date: Mapped[date] = mapped_column(Date)
    expected_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )
    version: Mapped[int] = mapped_column(Integer, default=1)


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "purchase_order_id", "line_number", name="uq_po_line_po_line"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("purchase_orders.id"))
    product_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("products.id"), nullable=True)
    line_number: Mapped[int] = mapped_column(Integer)
    item_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(20, 2))


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("purchase_orders.id"))
    receipt_number: Mapped[str] = mapped_column(String(40))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), default="completed")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class GoodsReceiptLine(Base):
    __tablename__ = "goods_receipt_lines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    goods_receipt_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("goods_receipts.id"))
    purchase_order_line_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("purchase_order_lines.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("products.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(20, 2))


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_product_sku_tenant"),
        UniqueConstraint("tenant_id", "id", name="uq_product_tenant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    sku: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), default="")
    unit: Mapped[str] = mapped_column(String(16), default="")
    sale_price: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )
    version: Mapped[int] = mapped_column(Integer, default=1)


class InventoryLocation(Base):
    __tablename__ = "inventory_locations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "branch_id", "code", name="uq_inv_location_branch_code"),
        UniqueConstraint("tenant_id", "id", name="uq_inv_location_tenant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("branches.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(24))
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now, default=datetime.now
    )


class StockBalance(Base):
    __tablename__ = "stock_balances"
    __table_args__ = (
        PrimaryKeyConstraint("tenant_id", "product_id", "location_id", name="pk_stock_balances"),
        ForeignKeyConstraint(
            ["tenant_id", "product_id"],
            ["products.tenant_id", "products.id"],
            name="fk_stock_balances_product",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "location_id"],
            ["inventory_locations.tenant_id", "inventory_locations.id"],
            name="fk_stock_balances_location",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    location_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    average_cost: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("products.id"))
    location_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("inventory_locations.id"))
    movement_number: Mapped[str] = mapped_column(String(40))
    movement_date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(
        String(24),
        CheckConstraint("type IN ('in', 'out', 'transfer', 'adjustment')", name="ck_stock_movement_type"),
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    before_stock: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    after_stock: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    reason: Mapped[str] = mapped_column(String(255), default="")
    reference_type: Mapped[str] = mapped_column(String(40), default="")
    reference_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )


# ---------------------------------------------------------------------------
# Notifications & Audit
# ---------------------------------------------------------------------------


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    type: Mapped[str] = mapped_column(String(40), default="")
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(String(500), default="")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notif_meta: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )


class TenantAuditEvent(Base):
    __tablename__ = "tenant_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tenants.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    actor_name: Mapped[str] = mapped_column(String(160), default="")
    action: Mapped[str] = mapped_column(String(80))
    module: Mapped[str] = mapped_column(String(40), default="")
    object_type: Mapped[str] = mapped_column(String(80))
    object_id: Mapped[str] = mapped_column(String(80), default="")
    before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    request_id: Mapped[str] = mapped_column(String(80), default="")
    correlation_id: Mapped[str] = mapped_column(String(80), default="")
    integrity_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)


# ---------------------------------------------------------------------------
# Documents & Jobs
# ---------------------------------------------------------------------------


class DocumentCounter(Base):
    __tablename__ = "document_counters"
    __table_args__ = (
        PrimaryKeyConstraint("tenant_id", "document_type", "period_key", name="pk_document_counters"),
        ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_document_counters_tenant"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    document_type: Mapped[str] = mapped_column(String(40))
    period_key: Mapped[str] = mapped_column(String(24))
    next_value: Mapped[int] = mapped_column(Integer, default=1)


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("tenants.id"), nullable=True)
    report_type: Mapped[str] = mapped_column(String(40))
    format: Mapped[str] = mapped_column(String(16), default="xlsx")
    status: Mapped[str] = mapped_column(String(24), default="pending")
    filters: Mapped[dict] = mapped_column(JSONB, default={})
    progress: Mapped[int] = mapped_column(Integer, default=0)
    storage_key: Mapped[str] = mapped_column(String(500), default="")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
