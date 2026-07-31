"""add mfa fields to users

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-07-31 16:00:00.000000

Columns may already exist when the baseline created the full schema, so
creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("users")}
    if "mfa_secret" not in cols:
        op.add_column('users', sa.Column('mfa_secret', sa.String(length=64), nullable=True))
    if "mfa_enabled" not in cols:
        op.add_column('users', sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    if "mfa_recovery_codes" not in cols:
        op.add_column('users', sa.Column('mfa_recovery_codes', sa.Text(), nullable=True))
    if "mfa_created_at" not in cols:
        op.add_column('users', sa.Column('mfa_created_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'mfa_created_at')
    op.drop_column('users', 'mfa_recovery_codes')
    op.drop_column('users', 'mfa_enabled')
    op.drop_column('users', 'mfa_secret')
