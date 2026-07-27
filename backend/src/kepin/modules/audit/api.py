from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from kepin.api.dependencies import (
    TenantContext,
    get_session,
    get_tenant_context,
)
from kepin.api.errors import NotFoundError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.db.models import TenantAuditEvent

router = APIRouter(prefix="/audit-events", tags=["Audit"])


class AuditEventResponse(ApiSchema):
    id: str
    actor_name: str | None = None
    action: str
    module: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    detail: dict | None = None
    timestamp: str | None = None
    created_at: str | None = None


@router.get("", response_model=PaginatedResponse[AuditEventResponse])
async def list_audit_events(
    ctx: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
):
    total_q = select(func.count(TenantAuditEvent.id)).where(TenantAuditEvent.tenant_id == ctx.id)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(TenantAuditEvent)
        .where(TenantAuditEvent.tenant_id == ctx.id)
        .order_by(TenantAuditEvent.timestamp.desc(), TenantAuditEvent.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()
    items = [AuditEventResponse.model_validate(e) for e in rows]
    return make_paginated(items, page, page_size, total)


@router.get("/{event_id}", response_model=AuditEventResponse)
async def get_audit_event(
    event_id: str = Path(...),
    ctx: TenantContext = Depends(get_tenant_context),
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
    return AuditEventResponse.model_validate(e)
