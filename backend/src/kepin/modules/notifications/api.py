from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import (
    TenantContext,
    get_session,
    get_tenant_context,
)
from kepin.api.errors import NotFoundError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.db.models import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationResponse(ApiSchema):
    id: str
    type: str
    title: str
    message: str | None = None
    link: str | None = None
    read_at: str | None = None
    created_at: str | None = None
    metadata: dict | None = None


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    ctx: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
):
    total_q = select(func.count(Notification.id)).where(Notification.tenant_id == ctx.id)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Notification)
        .where(Notification.tenant_id == ctx.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()
    items = [NotificationResponse.model_validate(n) for n in rows]
    return make_paginated(items, page, page_size, total)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str = Path(...),
    ctx: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    n = (
        await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.tenant_id == ctx.id,
            )
        )
    ).scalar_one_or_none()
    if not n:
        raise NotFoundError(message="Notifikasi tidak ditemukan")
    return NotificationResponse.model_validate(n)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str = Path(...),
    ctx: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    n = (
        await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.tenant_id == ctx.id,
            )
        )
    ).scalar_one_or_none()
    if not n:
        raise NotFoundError(message="Notifikasi tidak ditemukan")
    n.read_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(n)
    return NotificationResponse.model_validate(n)


@router.post("/read-all")
async def mark_all_notifications_read(
    ctx: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    await session.execute(
        select(Notification)
        .where(
            Notification.tenant_id == ctx.id,
            Notification.read_at.is_(None),
        )
    )
    stmt = (
        select(Notification)
        .where(
            Notification.tenant_id == ctx.id,
            Notification.read_at.is_(None),
        )
    )
    rows = (await session.execute(stmt)).scalars().all()
    for n in rows:
        n.read_at = now
    await session.commit()
    return {"status": "ok", "count": len(rows)}


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: str = Path(...),
    ctx: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    n = (
        await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.tenant_id == ctx.id,
            )
        )
    ).scalar_one_or_none()
    if not n:
        raise NotFoundError(message="Notifikasi tidak ditemukan")
    await session.delete(n)
    await session.commit()
