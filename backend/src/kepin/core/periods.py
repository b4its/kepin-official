from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.core.ids import new_uuid
from kepin.db.models import AccountingPeriod, FiscalYear


async def build_fiscal_year(
    session: AsyncSession,
    tenant_id: str,
    start_date: date,
    end_date: date,
    name: str | None = None,
) -> tuple[FiscalYear, list[AccountingPeriod]]:
    """Buat fiscal year baru secara eksplisit beserta 12 periode bulanannya.

    Tidak melakukan validasi tumpang-tindih; pemanggil bertanggung jawab
    memastikan rentang belum pernah digunakan.
    """
    if start_date > end_date:
        raise ValueError("start_date must be before end_date")

    fy = FiscalYear(
        id=new_uuid(),
        tenant_id=tenant_id,
        name=name or f"Tahun Buku {start_date.year}",
        start_date=start_date,
        end_date=end_date,
        status="open",
    )
    session.add(fy)
    await session.flush()

    periods: list[AccountingPeriod] = []
    cursor = start_date
    while cursor <= end_date:
        if cursor.month == 12:
            period_end = date(cursor.year, 12, 31)
        else:
            period_end = date(cursor.year, cursor.month + 1, 1) - timedelta(days=1)
        period_end = min(period_end, end_date)

        period = AccountingPeriod(
            id=new_uuid(),
            tenant_id=tenant_id,
            fiscal_year_id=fy.id,
            name=f"Periode {cursor.strftime('%Y-%m')}",
            start_date=cursor,
            end_date=period_end,
            status="open",
        )
        session.add(period)
        periods.append(period)

        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)

    await session.flush()
    return fy, periods


async def ensure_fiscal_year(
    session: AsyncSession,
    tenant_id: str,
    ref_date: date | None = None,
) -> tuple[FiscalYear, list[AccountingPeriod]]:
    """Buat fiscal year + 12 periode bulanan untuk tenant jika belum ada.

    Mengikuti OrganizationSetting.fiscal_year_start_month bila tersedia,
    fallback ke Januari.
    """
    ref = ref_date or date.today()

    existing = (
        await session.execute(
            select(FiscalYear).where(
                FiscalYear.tenant_id == tenant_id,
                FiscalYear.start_date <= ref,
                FiscalYear.end_date >= ref,
            )
        )
    ).scalar_one_or_none()

    if existing:
        periods = (
            (
                await session.execute(
                    select(AccountingPeriod).where(
                        AccountingPeriod.tenant_id == tenant_id,
                        AccountingPeriod.fiscal_year_id == existing.id,
                    )
                )
            )
            .scalars()
            .all()
        )
        return existing, list(periods)

    from kepin.db.models import OrganizationSetting

    org = (
        await session.execute(
            select(OrganizationSetting).where(OrganizationSetting.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()

    start_month = org.fiscal_year_start_month if org else 1
    start_month = max(1, min(12, start_month))

    year = ref.year
    if start_month > ref.month:
        year -= 1

    start_date = date(year, start_month, 1)
    if start_month == 1:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year + 1, start_month - 1, 1) - __import__("datetime").timedelta(days=1)

    fy = FiscalYear(
        id=new_uuid(),
        tenant_id=tenant_id,
        name=f"Tahun Buku {start_date.year}",
        start_date=start_date,
        end_date=end_date,
        status="open",
    )
    session.add(fy)
    await session.flush()

    periods: list[AccountingPeriod] = []
    cursor = start_date
    month_index = 1
    while cursor <= end_date:
        if cursor.month == 12:
            period_end = date(cursor.year, 12, 31)
        else:
            period_end = date(cursor.year, cursor.month + 1, 1) - __import__("datetime").timedelta(days=1)

        period = AccountingPeriod(
            id=new_uuid(),
            tenant_id=tenant_id,
            fiscal_year_id=fy.id,
            name=f"Periode {cursor.strftime('%Y-%m')}",
            start_date=cursor,
            end_date=period_end,
            status="open",
        )
        session.add(period)
        periods.append(period)

        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
        month_index += 1

    await session.flush()
    return fy, periods


async def ensure_periods_for_all_tenants(session: AsyncSession) -> int:
    """Backfill fiscal years + periods untuk semua tenant."""
    from kepin.db.models import Tenant

    tenants = (await session.execute(select(Tenant))).scalars().all()
    created = 0
    for tenant in tenants:
        fy, periods = await ensure_fiscal_year(session, str(tenant.id))
        if periods:
            created += 1
    return created
