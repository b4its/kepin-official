"""add tenant_id to incidents

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-31 18:00:00.000000

Column may already exist when the baseline created the full schema, so
creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("incidents")}
    if "tenant_id" not in cols:
        op.add_column('incidents', sa.Column('tenant_id', sa.Uuid(), nullable=True))
        op.create_foreign_key(
            'fk_incidents_tenant_id_tenants', 'incidents', 'tenants',
            ['tenant_id'], ['id'],
        )


def downgrade() -> None:
    op.drop_constraint('fk_incidents_tenant_id_tenants', 'incidents', type_='foreignkey')
    op.drop_column('incidents', 'tenant_id')
