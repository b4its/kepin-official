"""backfill default branch + inventory location for existing tenants

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-10-11 08:30:00.000000

Tenant yang dibuat sebelum perbaikan provisioning tidak memiliki cabang dan
lokasi inventaris default, sehingga alur inventori (POS, penerimaan stok,
pembelian) gagal dengan "Tidak ada lokasi inventaris aktif". Migration ini
melengkapi setiap tenant yang belum punya lokasi inventaris. Bersifat
idempotent sehingga aman dijalankan ulang.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Buat cabang utama + lokasi 'Gudang Utama' untuk tenant yang belum punya."""
    bind = op.get_bind()

    tenant_ids = [
        row[0]
        for row in bind.execute(
            sa.text(
                "SELECT t.id FROM tenants t "
                "WHERE NOT EXISTS ("
                "  SELECT 1 FROM inventory_locations l WHERE l.tenant_id = t.id"
                ")"
            )
        )
    ]

    for tenant_id in tenant_ids:
        branch_id = bind.execute(
            sa.text(
                "SELECT id FROM branches WHERE tenant_id = :tid "
                "ORDER BY is_main DESC, created_at LIMIT 1"
            ),
            {"tid": tenant_id},
        ).scalar()

        if branch_id is None:
            branch_id = bind.execute(
                sa.text(
                    "INSERT INTO branches "
                    "(id, tenant_id, code, name, address, is_main, status, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :tid, 'main', 'Kantor Pusat', '', true, "
                    "'active', now(), now()) RETURNING id"
                ),
                {"tid": tenant_id},
            ).scalar()

        bind.execute(
            sa.text(
                "INSERT INTO inventory_locations "
                "(id, tenant_id, branch_id, code, name, status, created_at, updated_at) "
                "VALUES (gen_random_uuid(), :tid, :bid, 'WH', 'Gudang Utama', "
                "'active', now(), now())"
            ),
            {"tid": tenant_id, "bid": branch_id},
        )


def downgrade() -> None:
    """Tidak ada operasi downgrade: data provisioning bersifat aditif."""
    pass
