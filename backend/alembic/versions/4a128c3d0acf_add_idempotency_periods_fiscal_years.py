"""add_idempotency_periods_fiscal_years

Revision ID: 4a128c3d0acf
Revises: ab1607c9eb00
Create Date: 2026-07-30 23:44:53.119496

Tables may already exist when the baseline created the full schema, so
every object creation is guarded with an existence check.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a128c3d0acf'
down_revision: Union[str, Sequence[str], None] = 'ab1607c9eb00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('fiscal_years'):
        op.create_table('fiscal_years',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('tenant_id', sa.Uuid(), nullable=False),
            sa.Column('name', sa.String(length=80), nullable=False),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=False),
            sa.Column('status', sa.String(length=24), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_fiscal_years_tenant_id_tenants')),
            sa.PrimaryKeyConstraint('id', name=op.f('pk_fiscal_years')),
            sa.UniqueConstraint('tenant_id', 'id', name='uq_fiscal_year_tenant_id'),
            sa.UniqueConstraint('tenant_id', 'name', name='uq_fiscal_year_name_tenant')
        )
    if not inspector.has_table('idempotency_keys'):
        op.create_table('idempotency_keys',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('tenant_id', sa.Uuid(), nullable=False),
            sa.Column('idempotency_key', sa.String(length=128), nullable=False),
            sa.Column('operation', sa.String(length=40), nullable=False),
            sa.Column('source_type', sa.String(length=40), nullable=False),
            sa.Column('source_id', sa.String(length=80), nullable=False),
            sa.Column('request_hash', sa.String(length=128), nullable=False),
            sa.Column('status', sa.String(length=24), nullable=False),
            sa.Column('result_id', sa.Uuid(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_idempotency_keys_tenant_id_tenants')),
            sa.PrimaryKeyConstraint('id', name=op.f('pk_idempotency_keys')),
            sa.UniqueConstraint('tenant_id', 'id', name='uq_idempotency_key_tenant_id'),
            sa.UniqueConstraint('tenant_id', 'idempotency_key', name='uq_idempotency_key_tenant')
        )
    if not inspector.has_table('accounting_periods'):
        op.create_table('accounting_periods',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('tenant_id', sa.Uuid(), nullable=False),
            sa.Column('fiscal_year_id', sa.Uuid(), nullable=False),
            sa.Column('name', sa.String(length=40), nullable=False),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=False),
            sa.Column('status', sa.String(length=24), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['fiscal_year_id'], ['fiscal_years.id'], name=op.f('fk_accounting_periods_fiscal_year_id_fiscal_years')),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name=op.f('fk_accounting_periods_tenant_id_tenants')),
            sa.PrimaryKeyConstraint('id', name=op.f('pk_accounting_periods')),
            sa.UniqueConstraint('tenant_id', 'fiscal_year_id', 'name', name='uq_period_name_fiscal_year'),
            sa.UniqueConstraint('tenant_id', 'id', name='uq_accounting_period_tenant_id')
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('accounting_periods')
    op.drop_table('idempotency_keys')
    op.drop_table('fiscal_years')
