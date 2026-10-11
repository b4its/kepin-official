"""backfill default GL accounts for existing tenants

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-10-11 08:45:00.000000

Tenant yang dibuat sebelum perbaikan provisioning tidak memiliki akun GL
default, sehingga posting jurnal subledger (inventori, penjualan, pembelian)
gagal dengan "Akun default '...' tidak ditemukan". Migration ini membuat
seluruh akun default yang belum ada untuk setiap tenant. Idempotent.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, Sequence[str], None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# name, type, normal_balance — harus sinkron dengan
# kepin.core.gl_mapping.DEFAULT_ACCOUNT_DEFS.
DEFAULT_ACCOUNT_DEFS = {
    "1-1002": ("Kas", "asset", "debit"),
    "1-1003": ("Bank", "asset", "debit"),
    "1-2001": ("Piutang Usaha", "asset", "debit"),
    "1-3001": ("Persediaan Barang Dagang", "asset", "debit"),
    "1-4006": ("PPN Masukan", "asset", "debit"),
    "2-1001": ("Hutang Usaha", "liability", "credit"),
    "2-2005": ("PPN Keluaran", "liability", "credit"),
    "3-4001": ("Selisih Persediaan", "equity", "credit"),
    "3-4002": ("Laba Ditahan", "equity", "credit"),
    "4-1001": ("Pendapatan Penjualan", "income", "credit"),
    "6-1001": ("Harga Pokok Penjualan", "expense", "debit"),
}


def upgrade() -> None:
    """Buat akun GL default yang belum ada untuk setiap tenant."""
    bind = op.get_bind()

    tenant_ids = [row[0] for row in bind.execute(sa.text("SELECT id FROM tenants"))]

    for tenant_id in tenant_ids:
        existing_codes = {
            row[0]
            for row in bind.execute(
                sa.text(
                    "SELECT code FROM accounts WHERE tenant_id = :tid AND code IN :codes"
                ).bindparams(sa.bindparam("codes", expanding=True)),
                {"tid": tenant_id, "codes": list(DEFAULT_ACCOUNT_DEFS.keys())},
            )
        }

        for code, (name, atype, normal_balance) in DEFAULT_ACCOUNT_DEFS.items():
            if code in existing_codes:
                continue
            bind.execute(
                sa.text(
                    "INSERT INTO accounts "
                    "(id, tenant_id, code, name, type, normal_balance, is_system, "
                    "allow_posting, status, version, created_at, updated_at) "
                    "VALUES (gen_random_uuid(), :tid, :code, :name, :type, :nb, "
                    "true, true, 'active', 1, now(), now())"
                ),
                {
                    "tid": tenant_id,
                    "code": code,
                    "name": name,
                    "type": atype,
                    "nb": normal_balance,
                },
            )


def downgrade() -> None:
    """Tidak ada operasi downgrade: data provisioning bersifat aditif."""
    pass
