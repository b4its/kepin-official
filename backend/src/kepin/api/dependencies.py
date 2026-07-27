from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Path, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.errors import NotFoundError
from kepin.core.time import resolve_period as resolve_period_range
from kepin.db.models import Tenant
from kepin.db.session import get_session


@dataclass(frozen=True)
class TenantContext:
    id: str
    slug: str
    timezone: str


async def get_tenant_context(
    tenant_slug: str = Path(..., alias="tenantSlug"),
    session: AsyncSession = Depends(get_session),
) -> TenantContext:
    t = (
        await session.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    ).scalar_one_or_none()
    if not t:
        raise NotFoundError(code="TENANT_NOT_FOUND", message="Tenant tidak ditemukan")
    return TenantContext(id=t.id, slug=t.slug, timezone=t.timezone)


class ListParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(5, ge=1, le=100, alias="pageSize"),
        search: str | None = Query(None),
        sort: str | None = Query(None),
    ):
        self.page = page
        self.page_size = page_size
        self.search = search
        self.sort = sort


class PeriodParams:
    def __init__(
        self,
        preset: str | None = Query(None),
        start_date: date | None = Query(None, alias="startDate"),
        end_date: date | None = Query(None, alias="endDate"),
    ):
        self.preset = preset
        self.start_date = start_date
        self.end_date = end_date

    def resolve(self) -> tuple[date, date]:
        return resolve_period_range(self.preset, self.start_date, self.end_date)
