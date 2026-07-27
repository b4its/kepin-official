from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, Path, Query, Request
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.errors import NotFoundError
from kepin.core.auth import decode_token
from kepin.core.time import resolve_period as resolve_period_range
from kepin.db.models import Membership, Tenant, User
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


async def get_optional_user(
    authorization: str | None = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    payload = decode_token(authorization.removeprefix("Bearer "))
    if not payload:
        return None
    result = await session.execute(select(User).where(User.id == payload.get("sub")))
    return result.scalar_one_or_none()


async def get_current_user(
    authorization: str | None = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Belum login")
    payload = decode_token(authorization.removeprefix("Bearer "))
    if not payload:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User tidak ditemukan")
    return user


async def get_tenant_membership(
    tenant: TenantContext = Depends(get_tenant_context),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Membership:
    result = await session.execute(
        select(Membership).where(
            Membership.tenant_id == tenant.id,
            Membership.user_id == user.id,
            Membership.status == "active",
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="Anda bukan anggota organisasi ini")
    return membership


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
