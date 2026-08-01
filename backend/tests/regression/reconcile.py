import asyncio
from sqlalchemy import select, func
from kepin.db.session import get_session
from kepin.db.models import (
    Account, GoodsReceiptLine, JournalEntry, JournalLine, Invoice, CustomerPayment,
    SupplierPayment, GoodsReceipt, StockBalance, StockMovement, Tenant,
)

async def main():
    async for s in get_session():
        t = (await s.execute(select(Tenant).where(Tenant.slug == "toko-maju"))).scalar_one()
        tid = str(t.id)
        print(f"Tenant: {t.slug} ({tid})")
        print()

        # ---- GL side: posted journal line totals per account code ----
        rows = (await s.execute(
            select(Account.code, Account.name, func.sum(JournalLine.debit), func.sum(JournalLine.credit))
            .join(JournalLine, JournalLine.account_id == Account.id)
            .join(JournalEntry, JournalEntry.id == JournalLine.journal_entry_id)
            .where(
                JournalLine.tenant_id == tid,
                JournalEntry.status == "posted",
                Account.code.in_(["1-2001", "1-3001", "1-1002", "2-1001", "2-2005", "4-1001", "6-1001", "3-4001"]),
            )
            .group_by(Account.code, Account.name)
        )).all()

        print("=== GL balances (posted journals, all-time) ===")
        gl = {}
        for code, name, d, c in rows:
            bal = (d or 0) - (c or 0)
            gl[code] = bal
            nb = "D" if bal >= 0 else "C"
            print(f"  {code} {name}: {abs(bal):,.2f} {nb}")
        print()

        # ---- Subledger side (only engine-created records, i.e. with journal link) ----
        ar_sub = (await s.execute(
            select(func.coalesce(func.sum(Invoice.balance_due), 0)).where(
                Invoice.tenant_id == tid, Invoice.status.in_(["sent", "partial", "posted"]),
                Invoice.journal_entry_id.is_not(None))
        )).scalar()
        print(f"Subledger: AR (sum balance_due, GL-linked)    = {ar_sub:,.2f}")

        ap_sub = (await s.execute(
            select(func.coalesce(func.sum(GoodsReceiptLine.quantity * GoodsReceiptLine.unit_cost), 0))
            .join(GoodsReceipt, GoodsReceipt.id == GoodsReceiptLine.goods_receipt_id)
            .where(GoodsReceipt.tenant_id == tid, GoodsReceipt.journal_entry_id.is_not(None))
        )).scalar()
        sp_total = (await s.execute(
            select(func.coalesce(func.sum(SupplierPayment.amount), 0)).where(
                SupplierPayment.tenant_id == tid, SupplierPayment.status == "posted",
                SupplierPayment.journal_entry_id.is_not(None))
        )).scalar()
        print(f"Subledger: AP (received goods) - paid         = {ap_sub - sp_total:,.2f}  (received={ap_sub:,.2f}, paid={sp_total:,.2f})")

        inv_val = (await s.execute(
            select(func.coalesce(func.sum(StockBalance.quantity * StockBalance.average_cost), 0))
            .where(
                StockBalance.tenant_id == tid,
                StockBalance.product_id.in_(
                    select(StockMovement.product_id).where(
                        StockMovement.tenant_id == tid,
                        StockMovement.journal_entry_id.is_not(None))),
            )
        )).scalar()
        print(f"Subledger: Inventory value (qty*avg, GL-touched products) = {inv_val:,.2f}")

        cash_sub = (await s.execute(
            select(func.coalesce(func.sum(CustomerPayment.amount), 0)).where(
                CustomerPayment.tenant_id == tid, CustomerPayment.status == "posted",
                CustomerPayment.journal_entry_id.is_not(None))
        )).scalar()
        print(f"Subledger: Cash in (customer payments)        = {cash_sub:,.2f}")
        print()

        print("=== RECONCILIATION ===")
        checks = [
            ("AR", gl.get("1-2001", 0), ar_sub),
            ("AP", gl.get("2-1001", 0), -(ap_sub - sp_total)),
            ("Inventory", gl.get("1-3001", 0), inv_val),
        ]
        ok = True
        for name, gl_val, sub_val in checks:
            match = abs(gl_val - sub_val) < 1.00
            ok = ok and match
            print(f"  {name:10s} GL={gl_val:>15,.2f}  subledger={sub_val:>15,.2f}  {'MATCH' if match else 'MISMATCH'}")

        # check overall journal balance (debits == credits)
        db_total, cr_total = (await s.execute(
            select(func.sum(JournalLine.debit), func.sum(JournalLine.credit))
            .join(JournalEntry, JournalEntry.id == JournalLine.journal_entry_id)
            .where(JournalLine.tenant_id == tid, JournalEntry.status == "posted")
        )).one()
        balanced = abs((db_total or 0) - (cr_total or 0)) < 0.01
        ok = ok and balanced
        print(f"  {'Books balanced':10s} debit={db_total:,.2f} credit={cr_total:,.2f}  {'MATCH' if balanced else 'MISMATCH'}")
        print()
        print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")

asyncio.run(main())
