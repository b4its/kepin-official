from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import (
    TenantContext,
    get_session,
    get_tenant_context,
    get_tenant_membership,
)
from kepin.api.errors import NotFoundError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.db.models import Membership, TenantAuditEvent

router = APIRouter(prefix="/audit-events", tags=["Audit"])


class AuditEventResponse(ApiSchema):
    id: str
    actor_id: str | None = None
    actor_name: str | None = None
    action: str
    module: str | None = None
    object_type: str | None = None
    object_id: str | None = None
    before: dict | None = None
    after: dict | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    integrity_hash: str | None = None
    timestamp: str | None = None


def _serialize_event(event: TenantAuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=str(event.id),
        actor_id=str(event.actor_id) if event.actor_id else None,
        actor_name=event.actor_name,
        action=event.action,
        module=event.module,
        object_type=event.object_type,
        object_id=event.object_id,
        before=event.before,
        after=event.after,
        request_id=event.request_id,
        correlation_id=event.correlation_id,
        integrity_hash=event.integrity_hash,
        timestamp=event.timestamp.isoformat() if event.timestamp else None,
    )


@router.get("", response_model=PaginatedResponse[AuditEventResponse])
async def list_audit_events(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    object_type: str | None = Query(None, alias="objectType"),
    action: str | None = Query(None),
):
    conditions = [TenantAuditEvent.tenant_id == ctx.id]
    if object_type:
        conditions.append(TenantAuditEvent.object_type == object_type)
    if action:
        conditions.append(TenantAuditEvent.action == action)

    total_q = select(func.count(TenantAuditEvent.id)).where(*conditions)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(TenantAuditEvent)
        .where(*conditions)
        .order_by(TenantAuditEvent.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()
    items = [_serialize_event(e) for e in rows]
    return make_paginated(items, page, page_size, total)


@router.get("/types", response_model=list[str])
async def list_audit_event_types(
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    """Daftar distinct object_type yang pernah tercatat untuk filter audit."""
    rows = (
        await session.execute(
            select(TenantAuditEvent.object_type)
            .where(
                TenantAuditEvent.tenant_id == ctx.id,
                TenantAuditEvent.object_type.is_not(None),
            )
            .distinct()
            .order_by(TenantAuditEvent.object_type)
        )
    ).all()
    return [row[0] for row in rows if row[0]]


@router.get("/{event_id}", response_model=AuditEventResponse)
async def get_audit_event(
    event_id: str = Path(...),
    ctx: TenantContext = Depends(get_tenant_context),
    _m: Membership = Depends(get_tenant_membership),
    session: AsyncSession = Depends(get_session),
):
    e = (
        await session.execute(
            select(TenantAuditEvent).where(
                TenantAuditEvent.id == event_id,
                TenantAuditEvent.tenant_id == ctx.id,
            )
        )
    ).scalar_one_or_none()
    if not e:
        raise NotFoundError(message="Audit event tidak ditemukan")
    return _serialize_event(e)
