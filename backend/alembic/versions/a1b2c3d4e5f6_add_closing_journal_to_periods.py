"""add closing journal to accounting periods

Revision ID: a1b2c3d4e5f6
Revises: 9f3b1a7c2d4e
Create Date: 2026-07-31 14:00:00.000000

Column may already exist when the baseline created the full schema, so
creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9f3b1a7c2d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("accounting_periods")}
    if "closing_journal_id" not in cols:
        op.add_column('accounting_periods', sa.Column('closing_journal_id', sa.Uuid(), nullable=True))
        op.create_foreign_key(
            'fk_accounting_periods_closing_journal_id_journal_entries', 'accounting_periods', 'journal_entries',
            ['closing_journal_id'], ['id'],
        )


def downgrade() -> None:
    op.drop_constraint('fk_accounting_periods_closing_journal_id_journal_entries', 'accounting_periods', type_='foreignkey')
    op.drop_column('accounting_periods', 'closing_journal_id')
