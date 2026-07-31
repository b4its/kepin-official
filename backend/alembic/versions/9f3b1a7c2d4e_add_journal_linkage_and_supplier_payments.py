"""add journal linkage and supplier payments

Revision ID: 9f3b1a7c2d4e
Revises: 4a128c3d0acf
Create Date: 2026-07-31 12:00:00.000000

Columns/tables may already exist when the baseline created the full
schema, so every object creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9f3b1a7c2d4e'
down_revision: Union[str, None] = '4a128c3d0acf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(bind, table: str) -> set[str]:
    return {c["name"] for c in sa.inspect(bind).get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "journal_entry_id" not in _column_names(bind, "goods_receipts"):
        op.add_column('goods_receipts', sa.Column('journal_entry_id', sa.Uuid(), nullable=True))
        op.create_foreign_key(
            'fk_goods_receipts_journal_entry_id_journal_entries', 'goods_receipts', 'journal_entries',
            ['journal_entry_id'], ['id'],
        )
    if "journal_entry_id" not in _column_names(bind, "stock_movements"):
        op.add_column('stock_movements', sa.Column('journal_entry_id', sa.Uuid(), nullable=True))
        op.create_foreign_key(
            'fk_stock_movements_journal_entry_id_journal_entries', 'stock_movements', 'journal_entries',
            ['journal_entry_id'], ['id'],
        )
    if not inspector.has_table('supplier_payments'):
        op.create_table(
            'supplier_payments',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('tenant_id', sa.Uuid(), nullable=False),
            sa.Column('branch_id', sa.Uuid(), nullable=True),
            sa.Column('payment_number', sa.String(length=40), nullable=False),
            sa.Column('supplier_id', sa.Uuid(), nullable=False),
            sa.Column('payment_date', sa.Date(), nullable=False),
            sa.Column('amount', sa.Numeric(20, 2), nullable=False),
            sa.Column('method', sa.String(length=40), nullable=False, server_default=''),
            sa.Column('reference', sa.String(length=80), nullable=False, server_default=''),
            sa.Column('status', sa.String(length=24), nullable=False, server_default='draft'),
            sa.Column('journal_entry_id', sa.Uuid(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], name='fk_supplier_payments_branch_id_branches'),
            sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], name='fk_supplier_payments_journal_entry_id_journal_entries'),
            sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name='fk_supplier_payments_supplier_id_suppliers'),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_supplier_payments_tenant_id_tenants'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_supplier_payments_tenant_id', 'supplier_payments', ['tenant_id'])
        op.create_index('ix_supplier_payments_supplier_id', 'supplier_payments', ['supplier_id'])

    if "journal_entry_id" not in {i["name"] for i in inspector.get_indexes("goods_receipts")}:
        op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_goods_receipts_journal_entry_id ON goods_receipts (journal_entry_id)"))
    if "journal_entry_id" not in {i["name"] for i in inspector.get_indexes("stock_movements")}:
        op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_stock_movements_journal_entry_id ON stock_movements (journal_entry_id)"))
    if "journal_entry_id" not in {i["name"] for i in inspector.get_indexes("supplier_payments")}:
        op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_supplier_payments_journal_entry_id ON supplier_payments (journal_entry_id)"))


def downgrade() -> None:
    op.drop_index('ix_supplier_payments_journal_entry_id', table_name='supplier_payments')
    op.drop_index('ix_goods_receipts_journal_entry_id', table_name='goods_receipts')
    op.drop_index('ix_stock_movements_journal_entry_id', table_name='stock_movements')
    op.drop_index('ix_supplier_payments_supplier_id', table_name='supplier_payments')
    op.drop_index('ix_supplier_payments_tenant_id', table_name='supplier_payments')
    op.drop_table('supplier_payments')
    op.drop_constraint('fk_stock_movements_journal_entry_id_journal_entries', 'stock_movements', type_='foreignkey')
    op.drop_column('stock_movements', 'journal_entry_id')
    op.drop_constraint('fk_goods_receipts_journal_entry_id_journal_entries', 'goods_receipts', type_='foreignkey')
    op.drop_column('goods_receipts', 'journal_entry_id')
