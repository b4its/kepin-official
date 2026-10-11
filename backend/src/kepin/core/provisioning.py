from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.core.ids import new_uuid
from kepin.db.models import Branch, InventoryLocation, Tenant

# Default branch/location yang otomatis dibuatkan untuk setiap tenant baru.
# Tanpa ini, alur inventori (POS, penerimaan stok, pembelian) gagal karena
# tidak ada lokasi inventaris aktif yang bisa dipakai.
DEFAULT_BRANCH_CODE = "main"
DEFAULT_BRANCH_NAME = "Kantor Pusat"
DEFAULT_LOCATION_CODE = "WH"
DEFAULT_LOCATION_NAME = "Gudang Utama"


async def ensure_default_branch(
    session: AsyncSession,
    tenant_id: str,
) -> Branch:
    """Pastikan tenant punya minimal satu cabang (Kantor Pusat).

    Mengembalikan cabang utama bila sudah ada, atau membuatnya bila belum.
    Tidak melakukan commit — pemanggil yang mengatur transaksi.
    """
    existing = (
        await session.execute(
            select(Branch)
            .where(Branch.tenant_id == tenant_id)
            .order_by(Branch.is_main.desc(), Branch.created_at)
        )
    ).scalars().first()
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    branch = Branch(
        id=new_uuid(),
        tenant_id=tenant_id,
        code=DEFAULT_BRANCH_CODE,
        name=DEFAULT_BRANCH_NAME,
        is_main=True,
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(branch)
    await session.flush()
    return branch


async def ensure_default_location(
    session: AsyncSession,
    tenant_id: str,
    branch_id: str | None = None,
) -> InventoryLocation:
    """Pastikan tenant punya minimal satu lokasi inventaris aktif.

    Membuat cabang default lebih dulu bila diperlukan agar lokasi dapat
    direferensikan ke cabang tersebut. Tidak melakukan commit — pemanggil
    yang mengatur transaksi.
    """
    existing = (
        await session.execute(
            select(InventoryLocation)
            .where(InventoryLocation.tenant_id == tenant_id)
            .order_by(InventoryLocation.created_at)
        )
    ).scalars().first()
    if existing:
        return existing

    if branch_id is None:
        branch = await ensure_default_branch(session, tenant_id)
        branch_id = str(branch.id)

    now = datetime.now(timezone.utc)
    location = InventoryLocation(
        id=new_uuid(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        code=DEFAULT_LOCATION_CODE,
        name=DEFAULT_LOCATION_NAME,
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(location)
    await session.flush()
    return location


async def ensure_tenant_inventory_defaults(
    session: AsyncSession,
    tenant_id: str,
) -> tuple[Branch, InventoryLocation]:
    """Buat cabang utama + lokasi inventaris default untuk tenant bila belum ada."""
    branch = await ensure_default_branch(session, tenant_id)
    location = await ensure_default_location(session, tenant_id, str(branch.id))
    return branch, location


async def backfill_inventory_defaults(session: AsyncSession) -> int:
    """Backfill cabang + lokasi inventaris default untuk semua tenant.

    Mengembalikan jumlah tenant yang dilengkapi. Aman dijalankan berulang
    kali karena setiap operasi bersifat idempotent.
    """
    tenants = (await session.execute(select(Tenant))).scalars().all()
    fixed = 0
    for tenant in tenants:
        before = (
            await session.execute(
                select(InventoryLocation).where(InventoryLocation.tenant_id == tenant.id)
            )
        ).scalars().first()
        if before:
            continue
        await ensure_tenant_inventory_defaults(session, str(tenant.id))
        fixed += 1
    await session.flush()
    return fixed
