"""add pos transactions

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-13 20:00:00.000000

Tables may already exist when the baseline created the full schema, so
every object creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('pos_transactions'):
        op.create_table(
            'pos_transactions',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('tenant_id', sa.Uuid(), nullable=False),
            sa.Column('checkout_number', sa.String(length=40), nullable=False),
            sa.Column('transaction_date', sa.Date(), nullable=False),
            sa.Column('total_amount', sa.Numeric(20, 2), nullable=False),
            sa.Column('amount_paid', sa.Numeric(20, 2), nullable=False),
            sa.Column('change_amount', sa.Numeric(20, 2), nullable=False),
            sa.Column('items_count', sa.Numeric(20, 4), nullable=False),
            sa.Column('status', sa.String(length=24), nullable=False),
            sa.Column('created_by', sa.Uuid(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('tenant_id', 'checkout_number', name='uq_pos_transaction_checkout_tenant'),
        )

    if not inspector.has_table('pos_transaction_lines'):
        op.create_table(
            'pos_transaction_lines',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('pos_transaction_id', sa.Uuid(), nullable=False),
            sa.Column('product_id', sa.Uuid(), nullable=False),
            sa.Column('product_name', sa.String(length=255), nullable=False),
            sa.Column('quantity', sa.Numeric(20, 4), nullable=False),
            sa.Column('unit_price', sa.Numeric(20, 2), nullable=False),
            sa.Column('line_total', sa.Numeric(20, 2), nullable=False),
            sa.ForeignKeyConstraint(['pos_transaction_id'], ['pos_transactions.id']),
            sa.ForeignKeyConstraint(['product_id'], ['products.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(
            'ix_pos_transaction_lines_pos_transaction_id',
            'pos_transaction_lines',
            ['pos_transaction_id'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_pos_transaction_lines_pos_transaction_id', table_name='pos_transaction_lines')
    op.drop_table('pos_transaction_lines')
    op.drop_table('pos_transactions')
