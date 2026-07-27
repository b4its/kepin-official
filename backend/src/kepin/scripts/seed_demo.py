from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from kepin.core.config import get_settings
from kepin.db.base import Base
from kepin.db.models import (
    Account,
    Branch,
    Customer,
    CustomerPayment,
    CustomerPaymentAllocation,
    GoodsReceipt,
    GoodsReceiptLine,
    Incident,
    InventoryLocation,
    Invoice,
    InvoiceLine,
    JournalEntry,
    JournalLine,
    Membership,
    Notification,
    OrganizationSetting,
    OutboxEvent,
    Plan,
    PlatformAuditEvent,
    Product,
    PurchaseOrder,
    PurchaseOrderLine,
    StockBalance,
    StockMovement,
    Subscription,
    SubscriptionEvent,
    Supplier,
    Tenant,
    TenantAuditEvent,
    Transaction,
    User,
)

IDR = "IDR"
WIB = "Asia/Jakarta"
TODAY = date.today()
NOW = datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


UID_ADMIN = new_id()
UID_BUDI = new_id()

TENANTS_DATA = [
    {
        "slug": "toko-maju",
        "name": "Toko Maju Jaya",
        "legal_name": "CV Toko Maju Jaya",
        "sector": "retail",
        "plan_code": "pro",
        "status": "active",
        "members": [UID_BUDI],
    },
    {
        "slug": "bengkel-maju",
        "name": "Bengkel Maju Motor",
        "legal_name": "Bengkel Maju Motor",
        "sector": "automotive",
        "plan_code": "trial",
        "status": "active",
        "members": [],
    },
    {
        "slug": "warung-segar",
        "name": "Warung Segar",
        "legal_name": "Warung Segar",
        "sector": "food",
        "plan_code": "pro",
        "status": "active",
        "members": [],
    },
    {
        "slug": "fashion-baru",
        "name": "Fashion Baru",
        "legal_name": "Fashion Baru",
        "sector": "fashion",
        "plan_code": "trial",
        "status": "suspended",
        "members": [],
    },
]

ACCOUNTS_TEMPLATE = [
    {"code": "1-1000", "name": "Kas", "type": "asset", "normal_balance": "debit"},
    {"code": "1-1100", "name": "Bank BCA", "type": "asset", "normal_balance": "debit"},
    {"code": "1-2000", "name": "Piutang Usaha", "type": "asset", "normal_balance": "debit"},
    {"code": "1-3000", "name": "Persediaan Barang", "type": "asset", "normal_balance": "debit"},
    {"code": "2-1000", "name": "Hutang Usaha", "type": "liability", "normal_balance": "credit"},
    {"code": "3-1000", "name": "Modal", "type": "equity", "normal_balance": "credit"},
    {"code": "4-1000", "name": "Pendapatan", "type": "income", "normal_balance": "credit"},
    {"code": "5-1000", "name": "Beban Operasional", "type": "expense", "normal_balance": "debit"},
]


def _utc(y: int, m: int, d: int) -> datetime:
    return datetime(y, m, d, tzinfo=timezone.utc)


async def _exists(session: AsyncSession, stmt) -> bool:
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def seed_demo(drop_first: bool = False) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=settings.sql_echo)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        if drop_first:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async with factory() as session:
        if await _exists(session, select(Plan).where(Plan.code == "trial")):
            print("Data already seeded, skipping.")
            return

        # ── Plans ──
        plans = [
            Plan(code="trial", name="Trial", billing_period="monthly", price=Decimal("0"), active=True),
            Plan(code="pro", name="Pro", billing_period="monthly", price=Decimal("150000"), active=True),
            Plan(code="enterprise", name="Enterprise", billing_period="yearly", price=Decimal("12000000"), active=True),
        ]
        session.add_all(plans)

        # ── Users ──
        admin = User(
            id=UID_ADMIN, name="Admin KePin", email="admin@kepin.io",
            password_hash="", status="active", created_at=NOW, updated_at=NOW,
        )
        budi = User(
            id=UID_BUDI, name="Budi Santoso", email="budi@tokomaju.com",
            password_hash="", status="active", created_at=NOW, updated_at=NOW,
        )
        session.add_all([admin, budi])

        # ── Tenants ──
        for td in TENANTS_DATA:
            tid = new_id()
            td["id"] = tid
            tenant = Tenant(
                id=tid, slug=td["slug"], name=td["name"], legal_name=td["legal_name"],
                sector=td["sector"], timezone=WIB, currency=IDR,
                plan_code=td["plan_code"], status=td["status"],
                onboarding_status="completed", created_at=NOW, updated_at=NOW,
            )
            session.add(tenant)

            org = OrganizationSetting(
                tenant_id=tid, tenant_name=td["name"], legal_name=td["legal_name"],
                timezone=WIB, currency=IDR, created_at=NOW, updated_at=NOW,
            )
            session.add(org)

            branch = Branch(
                id=new_id(), tenant_id=tid, code="main", name="Utama",
                is_main=True, status="active", created_at=NOW, updated_at=NOW,
            )
            session.add(branch)

            sub = Subscription(
                id=new_id(), tenant_id=tid, plan_code=td["plan_code"],
                status="active" if td["status"] == "active" else "suspended",
                start_date=TODAY - timedelta(days=30), end_date=TODAY + timedelta(days=335),
                created_at=NOW, updated_at=NOW,
            )
            session.add(sub)

            sub_event = SubscriptionEvent(
                id=new_id(), tenant_id=tid, subscription_id=sub.id,
                event_type="subscription.started", plan_code=td["plan_code"],
                amount=Decimal("150000") if td["plan_code"] == "pro" else Decimal("0"),
                occurred_at=NOW, created_at=NOW,
            )
            session.add(sub_event)

            # ── Memberships ──
            for uid in td["members"]:
                m = Membership(
                    id=new_id(), tenant_id=tid, user_id=uid,
                    role_name="owner", status="active", joined_at=NOW,
                    created_at=NOW, updated_at=NOW,
                )
                session.add(m)

            # ── Accounts ──
            acct_ids = {}
            for at in ACCOUNTS_TEMPLATE:
                aid = new_id()
                acct_ids[at["code"]] = aid
                a = Account(
                    id=aid, tenant_id=tid, code=at["code"], name=at["name"],
                    type=at["type"], normal_balance=at["normal_balance"],
                    is_system=True, allow_posting=True, status="active",
                    created_at=NOW, updated_at=NOW,
                )
                session.add(a)

            # ── Customers ──
            cids = []
            customers_data = [
                {"code": "C001", "name": "Pelanggan A", "email": "a@mail.com"},
                {"code": "C002", "name": "Pelanggan B", "email": "b@mail.com"},
                {"code": "C003", "name": "Pelanggan C", "email": "c@mail.com"},
            ]
            if td["slug"] == "toko-maju":
                customers_data += [
                    {"code": "C004", "name": "Pelanggan D", "email": "d@mail.com"},
                    {"code": "C005", "name": "Pelanggan E", "email": "e@mail.com"},
                ]
            for cd in customers_data:
                cid = new_id()
                cids.append(cid)
                c = Customer(
                    id=cid, tenant_id=tid, code=cd["code"], name=cd["name"],
                    email=cd["email"], status="active", created_at=NOW, updated_at=NOW,
                )
                session.add(c)

            # ── Suppliers ──
            sids = []
            suppliers_data = [
                {"code": "S001", "name": "Supplier X", "email": "x@supplier.com"},
                {"code": "S002", "name": "Supplier Y", "email": "y@supplier.com"},
                {"code": "S003", "name": "Supplier Z", "email": "z@supplier.com"},
            ]
            if td["slug"] == "toko-maju":
                suppliers_data += [
                    {"code": "S004", "name": "Supplier W", "email": "w@supplier.com"},
                ]
            for sd in suppliers_data:
                sid = new_id()
                sids.append(sid)
                s = Supplier(
                    id=sid, tenant_id=tid, code=sd["code"], name=sd["name"],
                    email=sd["email"], status="active", created_at=NOW, updated_at=NOW,
                )
                session.add(s)

            # ── Products & Stock Balances ──
            pids = []
            location_id = new_id()
            loc = InventoryLocation(
                id=location_id, tenant_id=tid, branch_id=branch.id,
                code="WH", name="Gudang Utama", status="active",
                created_at=NOW, updated_at=NOW,
            )
            session.add(loc)

            products_data = [
                {"sku": "PRD-001", "name": "Produk A", "category": "Umum", "unit": "pcs", "sale_price": "50000", "cost_price": "35000", "qty": "50"},
                {"sku": "PRD-002", "name": "Produk B", "category": "Umum", "unit": "pcs", "sale_price": "75000", "cost_price": "50000", "qty": "30"},
                {"sku": "PRD-003", "name": "Produk C", "category": "Umum", "unit": "pcs", "sale_price": "100000", "cost_price": "70000", "qty": "20"},
            ]
            if td["slug"] == "toko-maju":
                products_data += [
                    {"sku": "PRD-004", "name": "Produk D", "category": "Umum", "unit": "pcs", "sale_price": "150000", "cost_price": "100000", "qty": "15"},
                    {"sku": "PRD-005", "name": "Produk E", "category": "Umum", "unit": "pcs", "sale_price": "200000", "cost_price": "140000", "qty": "10"},
                ]

            for pd_data in products_data:
                pid = new_id()
                pids.append(pid)
                qty = Decimal(pd_data["qty"])
                avg_cost = Decimal(pd_data["cost_price"])
                p = Product(
                    id=pid, tenant_id=tid, sku=pd_data["sku"], name=pd_data["name"],
                    category=pd_data["category"], unit=pd_data["unit"],
                    sale_price=Decimal(pd_data["sale_price"]),
                    cost_price=avg_cost, minimum_stock=Decimal("5"),
                    status="active", created_at=NOW, updated_at=NOW,
                )
                session.add(p)

                sb = StockBalance(
                    tenant_id=tid, product_id=pid, location_id=location_id,
                    quantity=qty, average_cost=avg_cost, version=1,
                )
                session.add(sb)

                sm = StockMovement(
                    id=new_id(), tenant_id=tid, product_id=pid, location_id=location_id,
                    movement_number=f"SM-{pd_data['sku']}-001",
                    movement_date=TODAY - timedelta(days=25),
                    type="in", quantity=qty, before_stock=Decimal("0"),
                    after_stock=qty, unit_cost=avg_cost,
                    reason="Initial stock", reference_type="manual",
                    created_by=UID_ADMIN, created_at=NOW,
                )
                session.add(sm)

            # ── Transactions & Journal Entries ──
            for i in range(5):
                txn_date = TODAY - timedelta(days=5 * i + 1)
                txn = Transaction(
                    id=new_id(), tenant_id=tid, branch_id=branch.id,
                    transaction_number=f"TRX-{i + 1:04d}",
                    transaction_date=txn_date,
                    type="income" if i % 2 == 0 else "expense",
                    description=f"Transaksi demo #{i + 1}",
                    amount=Decimal("500000"),
                    account_id=acct_ids["1-1000"],
                    status="posted" if i < 3 else "draft",
                    created_at=NOW, updated_at=NOW,
                )
                session.add(txn)

                if i < 3:
                    je = JournalEntry(
                        id=new_id(), tenant_id=tid, branch_id=branch.id,
                        journal_number=f"JR-{i + 1:04d}",
                        journal_date=txn_date,
                        reference=txn.transaction_number,
                        description=f"Jurnal untuk transaksi #{i + 1}",
                        status="posted",
                        posted_at=NOW, posted_by=UID_ADMIN,
                        created_at=NOW, updated_at=NOW,
                    )
                    session.add(je)

                    if i % 2 == 0:
                        income_line = JournalLine(
                            id=new_id(), tenant_id=tid, journal_entry_id=je.id,
                            account_id=acct_ids["4-1000"], line_number=1,
                            description="Pendapatan", debit=Decimal("0"), credit=Decimal("500000"),
                        )
                        cash_line = JournalLine(
                            id=new_id(), tenant_id=tid, journal_entry_id=je.id,
                            account_id=acct_ids["1-1000"], line_number=2,
                            description="Kas (debit)", debit=Decimal("500000"), credit=Decimal("0"),
                        )
                        session.add_all([income_line, cash_line])
                    else:
                        expense_line = JournalLine(
                            id=new_id(), tenant_id=tid, journal_entry_id=je.id,
                            account_id=acct_ids["5-1000"], line_number=1,
                            description="Beban operasional", debit=Decimal("250000"), credit=Decimal("0"),
                        )
                        cash_out = JournalLine(
                            id=new_id(), tenant_id=tid, journal_entry_id=je.id,
                            account_id=acct_ids["1-1000"], line_number=2,
                            description="Kas (credit)", debit=Decimal("0"), credit=Decimal("250000"),
                        )
                        session.add_all([expense_line, cash_out])

            # ── Invoices ──
            for i in range(3):
                inv_date = TODAY - timedelta(days=10 * i + 2)
                due = inv_date + timedelta(days=30)
                paid = Decimal("0")
                balance = Decimal("1000000")
                inv_status = "posted"
                if i == 0:
                    paid = Decimal("500000")
                    balance = Decimal("500000")
                elif i == 1:
                    paid = Decimal("1000000")
                    balance = Decimal("0")
                    inv_status = "paid"

                inv = Invoice(
                    id=new_id(), tenant_id=tid, branch_id=branch.id,
                    invoice_number=f"INV-{i + 1:04d}",
                    customer_id=cids[i % len(cids)],
                    invoice_date=inv_date, due_date=due,
                    status=inv_status,
                    subtotal=Decimal("900000"), tax_total=Decimal("100000"),
                    discount_total=Decimal("0"),
                    total=Decimal("1000000"),
                    paid_amount=paid, balance_due=balance,
                    created_at=NOW, updated_at=NOW,
                )
                session.add(inv)

                line = InvoiceLine(
                    id=new_id(), tenant_id=tid, invoice_id=inv.id,
                    line_number=1, product_id=pids[i % len(pids)],
                    item_name=f"Item Invoice {i + 1}",
                    quantity=Decimal("2"), unit="pcs",
                    unit_price=Decimal("500000"),
                    tax_rate=Decimal("11"), discount_amount=Decimal("0"),
                    line_total=Decimal("1000000"),
                )
                session.add(line)

            # ── Customer Payments ──
            for i in range(2):
                pmt = CustomerPayment(
                    id=new_id(), tenant_id=tid, branch_id=branch.id,
                    payment_number=f"PYT-{i + 1:04d}",
                    customer_id=cids[i % len(cids)],
                    payment_date=TODAY - timedelta(days=5),
                    amount=Decimal("500000"), method="transfer",
                    status="posted", created_at=NOW, updated_at=NOW,
                )
                session.add(pmt)

            # ── Purchase Orders ──
            for i in range(2):
                po = PurchaseOrder(
                    id=new_id(), tenant_id=tid, branch_id=branch.id,
                    po_number=f"PO-{i + 1:04d}",
                    supplier_id=sids[i % len(sids)],
                    order_date=TODAY - timedelta(days=15),
                    expected_date=TODAY + timedelta(days=15),
                    status="received" if i == 0 else "sent",
                    subtotal=Decimal("2000000"),
                    tax_total=Decimal("200000"),
                    total=Decimal("2200000"),
                    created_at=NOW, updated_at=NOW,
                )
                session.add(po)

                pol = PurchaseOrderLine(
                    id=new_id(), tenant_id=tid, purchase_order_id=po.id,
                    product_id=pids[i % len(pids)], line_number=1,
                    item_name=f"PO Item {i + 1}",
                    quantity=Decimal("10"), received_quantity=Decimal("10") if i == 0 else Decimal("0"),
                    unit_price=Decimal("200000"), line_total=Decimal("2000000"),
                )
                session.add(pol)

                if i == 0:
                    gr = GoodsReceipt(
                        id=new_id(), tenant_id=tid, branch_id=branch.id,
                        purchase_order_id=po.id,
                        receipt_number=f"GR-{i + 1:04d}",
                        received_at=NOW, status="completed",
                        created_at=NOW, updated_at=NOW,
                    )
                    session.add(gr)
                    grl = GoodsReceiptLine(
                        id=new_id(), tenant_id=tid, goods_receipt_id=gr.id,
                        purchase_order_line_id=pol.id,
                        product_id=pids[i % len(pids)],
                        quantity=Decimal("10"), unit_cost=Decimal("200000"),
                    )
                    session.add(grl)

            # ── Notifications (8) ──
            notif_types = [
                ("info", "Selamat datang", "Akun tenant berhasil dibuat"),
                ("info", "Invoice baru", "Invoice INV-0001 telah diterbitkan"),
                ("warning", "Pembayaran jatuh tempo", "Invoice INV-0002 akan jatuh tempo dalam 3 hari"),
                ("success", "Pembayaran diterima", "Pembayaran Rp500.000 dari Pelanggan A diterima"),
                ("info", "Laporan tersedia", "Laporan bulanan siap diunduh"),
                ("warning", "Stok menipis", "Produk A hampir habis (sisa 5)"),
                ("success", "Langganan diperbarui", "Langganan Pro akan diperpanjang otomatis"),
                ("info", "Sistem upgrade", "Pemeliharaan sistem dijadwalkan malam ini"),
            ]
            for j, (ntype, title, msg) in enumerate(notif_types):
                notif = Notification(
                    id=new_id(), tenant_id=tid,
                    type=ntype, title=title, message=msg,
                    read_at=NOW if j < 2 else None,
                    created_at=NOW - timedelta(hours=j),
                )
                session.add(notif)

            # ── Tenant Audit Events (5) ──
            audit_actions = [
                "user.login",
                "invoice.created",
                "invoice.paid",
                "journal.posted",
                "settings.updated",
            ]
            for j, action in enumerate(audit_actions):
                ae = TenantAuditEvent(
                    id=new_id(), tenant_id=tid,
                    timestamp=NOW - timedelta(hours=j),
                    actor_name="Budi Santoso",
                    action=action,
                    module="sales" if "invoice" in action else "system",
                    resource_type="invoice" if "invoice" in action else "journal" if "journal" in action else "user",
                    created_at=NOW - timedelta(hours=j),
                )
                session.add(ae)

        # ── Platform Incidents (2) ──
        incidents = [
            Incident(
                id=new_id(), title="Gangguan Database",
                description="Latensi database meningkat 2x lipat selama 5 menit",
                severity="warning", status="resolved",
                started_at=NOW - timedelta(days=7), resolved_at=NOW - timedelta(days=6, hours=12),
                created_at=NOW - timedelta(days=7), updated_at=NOW - timedelta(days=6, hours=12),
            ),
            Incident(
                id=new_id(), title="Pemeliharaan Terjadwal",
                description="Upgrade server pada pukul 02:00-04:00 WIB",
                severity="info", status="open",
                started_at=NOW + timedelta(days=3),
                created_at=NOW, updated_at=NOW,
            ),
        ]
        session.add_all(incidents)

        # ── Platform Audit Events (3) ──
        platform_audits = [
            PlatformAuditEvent(
                id=new_id(), action="tenant.created",
                actor_name="System", resource_type="tenant",
                detail={"slug": "toko-maju", "name": "Toko Maju Jaya"},
                created_at=NOW - timedelta(days=30),
            ),
            PlatformAuditEvent(
                id=new_id(), action="system.deploy",
                actor_name="DevOps", resource_type="deployment",
                detail={"version": "1.0.0", "environment": "production"},
                created_at=NOW - timedelta(days=1),
            ),
            PlatformAuditEvent(
                id=new_id(), action="backup.completed",
                actor_name="System", resource_type="backup",
                detail={"size": "256MB", "status": "success"},
                created_at=NOW - timedelta(hours=6),
            ),
        ]
        session.add_all(platform_audits)

        await session.commit()
        print(f"Seed complete: {len(TENANTS_DATA)} tenants, {len(ACCOUNTS_TEMPLATE)} accounts each.")


async def main() -> None:
    import sys
    drop = "--drop" in sys.argv
    await seed_demo(drop_first=drop)


if __name__ == "__main__":
    asyncio.run(main())
