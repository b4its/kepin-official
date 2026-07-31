from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.errors import ValidationError
from kepin.core.gl_mapping import (
    DEFAULT_ACCOUNT_CODES as GL,
    get_account_by_code,
    get_cash_account_for_method,
)
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, ZERO
from kepin.core.posting import PostingResult, post_direct_journal
from kepin.db.models import (
    Account,
    CustomerPayment,
    GoodsReceipt,
    Invoice,
    InvoiceLine,
    JournalEntry,
    JournalLine,
    Product,
    StockBalance,
    StockMovement,
    SupplierPayment,
)


async def _journal_date_for(dt: date | datetime | None) -> date:
    if isinstance(dt, datetime):
        return dt.date()
    if isinstance(dt, date):
        return dt
    return datetime.now(timezone.utc).date()


async def reverse_posted_journal(
    session: AsyncSession,
    tenant_id: str,
    journal_id: str,
    description_prefix: str = "Reverse",
) -> JournalEntry:
    original = (
        await session.execute(
            select(JournalEntry).where(
                JournalEntry.id == journal_id,
                JournalEntry.tenant_id == tenant_id,
            )
        )
    ).scalar_one_or_none()
    if not original:
        raise ValidationError(message="Jurnal tidak ditemukan")
    if original.status != "posted":
        raise ValidationError(message="Hanya jurnal posted yang dapat di-reverse")

    existing = (
        await session.execute(
            select(JournalEntry.id).where(
                JournalEntry.reversed_entry_id == original.id,
                JournalEntry.tenant_id == tenant_id,
            )
        )
    ).first()
    if existing:
        raise ValidationError(message="Jurnal ini sudah memiliki reversal")

    original_lines = (
        (
            await session.execute(
                select(JournalLine).where(
                    JournalLine.journal_entry_id == original.id,
                    JournalLine.tenant_id == tenant_id,
                )
            )
        )
        .scalars()
        .all()
    )

    now = datetime.now(timezone.utc)
    reversal = JournalEntry(
        id=new_uuid(),
        tenant_id=tenant_id,
        branch_id=original.branch_id,
        journal_number=f"REV-{original.journal_number}",
        journal_date=original.journal_date,
        reference=f"Reverse-{original.journal_number}",
        description=f"{description_prefix}: {original.description}",
        status="posted",
        posted_at=now,
        reversed_entry_id=original.id,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(reversal)
    await session.flush()

    for i, line in enumerate(original_lines):
        session.add(
            JournalLine(
                id=new_uuid(),
                tenant_id=tenant_id,
                journal_entry_id=reversal.id,
                account_id=line.account_id,
                line_number=i + 1,
                description=f"Reverse: {line.description}",
                debit=line.credit,
                credit=line.debit,
            )
        )

    original.updated_at = now
    original.version = (original.version or 1) + 1
    return reversal


async def post_invoice_journal(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    invoice: Invoice,
    lines: list[InvoiceLine],
) -> tuple[PostingResult, list[StockMovement]]:
    if invoice.total <= ZERO:
        raise ValidationError(message="Invoice total harus lebih dari nol")

    ar_account = await get_account_by_code(session, tenant_id, GL["ar"])
    revenue_account = await get_account_by_code(session, tenant_id, GL["revenue"])

    journal_lines: list[dict] = [
        {
            "account_id": str(ar_account.id),
            "debit": to_money(invoice.total),
            "credit": ZERO,
            "description": f"Piutang {invoice.invoice_number}",
        },
        {
            "account_id": str(revenue_account.id),
            "debit": ZERO,
            "credit": to_money(invoice.subtotal - invoice.discount_total),
            "description": f"Pendapatan {invoice.invoice_number}",
        },
    ]
    if invoice.tax_total > ZERO:
        vat_account = await get_account_by_code(session, tenant_id, GL["vat_out"])
        journal_lines.append(
            {
                "account_id": str(vat_account.id),
                "debit": ZERO,
                "credit": to_money(invoice.tax_total),
                "description": f"PPN Keluaran {invoice.invoice_number}",
            }
        )

    movements = await _issue_stock_for_invoice(session, tenant_id, invoice, lines)

    total_cogs = sum(m.unit_cost * m.quantity for m in movements)
    if total_cogs > ZERO:
        cogs_account = await get_account_by_code(session, tenant_id, GL["cogs"])
        inventory_account = await get_account_by_code(session, tenant_id, GL["inventory"])
        journal_lines.append(
            {
                "account_id": str(cogs_account.id),
                "debit": to_money(total_cogs),
                "credit": ZERO,
                "description": f"HPP {invoice.invoice_number}",
            }
        )
        journal_lines.append(
            {
                "account_id": str(inventory_account.id),
                "debit": ZERO,
                "credit": to_money(total_cogs),
                "description": f"Persediaan keluar {invoice.invoice_number}",
            }
        )

    result = await post_direct_journal(
        session=session,
        tenant_id=tenant_id,
        user_id=user_id,
        journal_date=await _journal_date_for(invoice.invoice_date),
        description=f"Penjualan {invoice.invoice_number}",
        lines_data=journal_lines,
        journal_number=invoice.invoice_number,
        reference=invoice.invoice_number,
        branch_id=str(invoice.branch_id) if invoice.branch_id else None,
        idempotency_key=f"subledger:invoice:{invoice.id}",
        request_hash=f"invoice:{invoice.id}:total:{invoice.total}",
    )

    invoice.journal_entry_id = result.journal_entry.id
    for mov in movements:
        mov.journal_entry_id = result.journal_entry.id

    return result, movements


async def _issue_stock_for_invoice(
    session: AsyncSession,
    tenant_id: str,
    invoice: Invoice,
    lines: list[InvoiceLine],
) -> list[StockMovement]:
    now = datetime.now(timezone.utc)
    movements: list[StockMovement] = []
    movement_seq = 0

    stock_stmt = (
        select(StockBalance)
        .where(
            StockBalance.tenant_id == tenant_id,
        )
        .order_by(StockBalance.product_id, StockBalance.location_id)
    )
    all_balances = (await session.execute(stock_stmt)).scalars().all()
    balances_by_product: dict[str, list[StockBalance]] = {}
    for sb in all_balances:
        balances_by_product.setdefault(str(sb.product_id), []).append(sb)

    for line in lines:
        if not line.product_id:
            continue
        product_id = str(line.product_id)
        balances = balances_by_product.get(product_id, [])
        available = sum(b.quantity for b in balances)
        if available <= ZERO:
            continue

        issue_qty = min(line.quantity, available)
        remaining = issue_qty
        for sb in balances:
            if remaining <= ZERO:
                break
            take = min(sb.quantity, remaining)
            if take <= ZERO:
                continue
            remaining -= take
            before = sb.quantity
            sb.quantity = before - take
            movement_seq += 1
            mov = StockMovement(
                id=new_uuid(),
                tenant_id=tenant_id,
                product_id=line.product_id,
                location_id=sb.location_id,
                movement_number=f"{invoice.invoice_number}-OUT-{movement_seq:03d}",
                movement_date=await _journal_date_for(invoice.invoice_date),
                type="out",
                quantity=take,
                before_stock=before,
                after_stock=sb.quantity,
                unit_cost=sb.average_cost,
                reason=f"Penjualan {invoice.invoice_number}",
                reference_type="invoice",
                reference_id=invoice.id,
                created_at=now,
            )
            session.add(mov)
            movements.append(mov)
    return movements


async def restore_stock_for_invoice(
    session: AsyncSession,
    tenant_id: str,
    invoice: Invoice,
) -> list[StockMovement]:
    """Restore stock previously issued for an invoice (used on reversal)."""
    now = datetime.now(timezone.utc)
    movements: list[StockMovement] = []

    issued = (
        (
            await session.execute(
                select(StockMovement)
                .where(
                    StockMovement.tenant_id == tenant_id,
                    StockMovement.reference_type == "invoice",
                    StockMovement.reference_id == invoice.id,
                    StockMovement.type == "out",
                )
            )
        )
        .scalars()
        .all()
    )

    for i, mov in enumerate(issued, start=1):
        sb = (
            await session.execute(
                select(StockBalance).where(
                    StockBalance.tenant_id == tenant_id,
                    StockBalance.product_id == mov.product_id,
                    StockBalance.location_id == mov.location_id,
                )
            )
        ).scalar_one_or_none()
        if not sb:
            continue
        before = sb.quantity
        sb.quantity = before + mov.quantity
        restore = StockMovement(
            id=new_uuid(),
            tenant_id=tenant_id,
            product_id=mov.product_id,
            location_id=mov.location_id,
            movement_number=f"{invoice.invoice_number}-IN-{i:03d}",
            movement_date=await _journal_date_for(invoice.invoice_date),
            type="in",
            quantity=mov.quantity,
            before_stock=before,
            after_stock=sb.quantity,
            unit_cost=mov.unit_cost,
            reason=f"Retur {invoice.invoice_number}",
            reference_type="invoice_reversal",
            reference_id=invoice.id,
            created_at=now,
        )
        session.add(restore)
        movements.append(restore)

    return movements


async def post_customer_payment_journal(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    payment: CustomerPayment,
) -> PostingResult:
    cash_account = await get_cash_account_for_method(session, tenant_id, payment.method)
    ar_account = await get_account_by_code(session, tenant_id, GL["ar"])
    amount = to_money(payment.amount)

    result = await post_direct_journal(
        session=session,
        tenant_id=tenant_id,
        user_id=user_id,
        journal_date=await _journal_date_for(payment.payment_date),
        description=f"Penerimaan pembayaran {payment.payment_number}",
        lines_data=[
            {
                "account_id": str(cash_account.id),
                "debit": amount,
                "credit": ZERO,
                "description": f"Kas masuk {payment.payment_number}",
            },
            {
                "account_id": str(ar_account.id),
                "debit": ZERO,
                "credit": amount,
                "description": f"Pelunasan piutang {payment.payment_number}",
            },
        ],
        journal_number=payment.payment_number,
        reference=payment.payment_number,
        branch_id=str(payment.branch_id) if payment.branch_id else None,
        idempotency_key=f"subledger:customer_payment:{payment.id}",
        request_hash=f"payment:{payment.id}:amount:{payment.amount}",
    )

    payment.journal_entry_id = result.journal_entry.id
    return result


async def post_supplier_payment_journal(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    payment: SupplierPayment,
) -> PostingResult:
    cash_account = await get_cash_account_for_method(session, tenant_id, payment.method)
    ap_account = await get_account_by_code(session, tenant_id, GL["ap"])
    amount = to_money(payment.amount)

    result = await post_direct_journal(
        session=session,
        tenant_id=tenant_id,
        user_id=user_id,
        journal_date=await _journal_date_for(payment.payment_date),
        description=f"Pembayaran ke supplier {payment.payment_number}",
        lines_data=[
            {
                "account_id": str(ap_account.id),
                "debit": amount,
                "credit": ZERO,
                "description": f"Pelunasan hutang {payment.payment_number}",
            },
            {
                "account_id": str(cash_account.id),
                "debit": ZERO,
                "credit": amount,
                "description": f"Kas keluar {payment.payment_number}",
            },
        ],
        journal_number=payment.payment_number,
        reference=payment.payment_number,
        branch_id=str(payment.branch_id) if payment.branch_id else None,
        idempotency_key=f"subledger:supplier_payment:{payment.id}",
        request_hash=f"spayment:{payment.id}:amount:{payment.amount}",
    )

    payment.journal_entry_id = result.journal_entry.id
    return result


async def post_goods_receipt_journal(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    receipt: GoodsReceipt,
    received_lines: list[tuple[object, Decimal]],
) -> PostingResult:
    inventory_account = await get_account_by_code(session, tenant_id, GL["inventory"])
    ap_account = await get_account_by_code(session, tenant_id, GL["ap"])

    total_value = sum((to_money(line.unit_cost) * qty) for line, qty in received_lines)
    if total_value <= ZERO:
        raise ValidationError(message="Nilai barang diterima harus lebih dari nol")

    result = await post_direct_journal(
        session=session,
        tenant_id=tenant_id,
        user_id=user_id,
        journal_date=await _journal_date_for(receipt.received_at),
        description=f"Penerimaan barang {receipt.receipt_number}",
        lines_data=[
            {
                "account_id": str(inventory_account.id),
                "debit": to_money(total_value),
                "credit": ZERO,
                "description": f"Persediaan masuk {receipt.receipt_number}",
            },
            {
                "account_id": str(ap_account.id),
                "debit": ZERO,
                "credit": to_money(total_value),
                "description": f"Hutang usaha {receipt.receipt_number}",
            },
        ],
        journal_number=receipt.receipt_number,
        reference=receipt.receipt_number,
        branch_id=str(receipt.branch_id) if receipt.branch_id else None,
        idempotency_key=f"subledger:goods_receipt:{receipt.id}",
        request_hash=f"receipt:{receipt.id}:value:{total_value}",
    )

    receipt.journal_entry_id = result.journal_entry.id
    return result


async def post_stock_movement_journal(
    session: AsyncSession,
    tenant_id: str,
    user_id: str,
    movement: StockMovement,
    counterpart_account: Account,
    description: str,
    effective_type: str | None = None,
) -> PostingResult:
    inventory_account = await get_account_by_code(session, tenant_id, GL["inventory"])
    value = to_money(movement.unit_cost) * movement.quantity
    direction = effective_type or movement.type

    if direction == "in":
        lines_data = [
            {
                "account_id": str(inventory_account.id),
                "debit": value,
                "credit": ZERO,
                "description": description,
            },
            {
                "account_id": str(counterpart_account.id),
                "debit": ZERO,
                "credit": value,
                "description": description,
            },
        ]
    else:
        lines_data = [
            {
                "account_id": str(counterpart_account.id),
                "debit": value,
                "credit": ZERO,
                "description": description,
            },
            {
                "account_id": str(inventory_account.id),
                "debit": ZERO,
                "credit": value,
                "description": description,
            },
        ]

    result = await post_direct_journal(
        session=session,
        tenant_id=tenant_id,
        user_id=user_id,
        journal_date=await _journal_date_for(movement.movement_date),
        description=description,
        lines_data=lines_data,
        journal_number=movement.movement_number,
        reference=movement.movement_number,
        idempotency_key=f"subledger:stock_movement:{movement.id}",
        request_hash=f"stock:{movement.id}:type:{movement.type}:value:{value}",
    )

    movement.journal_entry_id = result.journal_entry.id
    return result


async def stock_value(
    session: AsyncSession,
    tenant_id: str,
    product_id: str | None = None,
) -> Decimal:
    stmt = select(StockBalance).where(StockBalance.tenant_id == tenant_id)
    if product_id:
        stmt = stmt.where(StockBalance.product_id == product_id)
    balances = (await session.execute(stmt)).scalars().all()
    return sum(b.quantity * b.average_cost for b in balances)
