"""add initial_capital to organization_settings

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-14 09:00:00.000000

Kolom baru menyimpan nilai modal awal per tenant sebagai acuan keuangan.
Guarded dengan pengecekan kolom agar aman bila baseline sudah membuatnya.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {c['name'] for c in inspector.get_columns('organization_settings')}
    if 'initial_capital' not in columns:
        op.add_column(
            'organization_settings',
            sa.Column(
                'initial_capital',
                sa.Numeric(20, 2),
                nullable=False,
                server_default='0',
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {c['name'] for c in inspector.get_columns('organization_settings')}
    if 'initial_capital' in columns:
        op.drop_column('organization_settings', 'initial_capital')
