"""add password reset fields to users

Revision ID: c3d4e5f6a7b8
Revises: b1c2d3e4f5a6
Create Date: 2026-07-31 17:00:00.000000

Columns may already exist when the baseline created the full schema, so
creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("users")}
    if "password_reset_token" not in cols:
        op.add_column('users', sa.Column('password_reset_token', sa.String(length=64), nullable=True))
    if "password_reset_expires_at" not in cols:
        op.add_column('users', sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'password_reset_expires_at')
    op.drop_column('users', 'password_reset_token')
