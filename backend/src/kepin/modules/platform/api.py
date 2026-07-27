from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from kepin.api.dependencies import get_session, TenantContext, get_tenant_context, ListParams, PeriodParams
from kepin.api.errors import NotFoundError, ConflictError, ValidationError
from kepin.core.pagination import ApiSchema, PaginatedResponse, make_paginated
from kepin.core.ids import new_uuid
from kepin.core.money import to_money, money_str
from kepin.core.time import resolve_period
from kepin.db.models import (
    Tenant,
    User,
    Subscription,
    SubscriptionEvent,
    Incident,
    PlatformAuditEvent,
    OrganizationSetting,
    Branch,
)


router = APIRouter(tags=["Platform"])


# ── Schemas ──────────────────────────────────────────────────────────


class DashboardResponse(ApiSchema):
    period: dict
    metrics: dict
    tenant_growth: list[dict] = []
    plan_distribution: list[dict] = []
    recent_activity: list[dict] = []


class TenantResponse(ApiSchema):
    id: str
    name: str
    slug: str
    status: str
    plan_code: str | None = None
    timezone: str | None = None
    currency: str | None = None
    sector: str | None = None
    legal_name: str | None = None
    onboarding_status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TenantCreate(ApiSchema):
    name: str
    slug: str
    plan_code: str | None = None
    timezone: str | None = None
    currency: str | None = None
    sector: str | None = None
    legal_name: str | None = None


class TenantUpdate(ApiSchema):
    name: str | None = None
    legal_name: str | None = None
    sector: str | None = None
    timezone: str | None = None
    currency: str | None = None
    onboarding_status: str | None = None


class UserResponse(ApiSchema):
    id: str
    name: str
    email: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserCreate(ApiSchema):
    name: str
    email: str
    password_hash: str | None = None


class UserUpdate(ApiSchema):
    name: str | None = None
    email: str | None = None
    status: str | None = None


class SubscriptionResponse(ApiSchema):
    id: str
    tenant_id: str
    plan_code: str
    status: str
    start_date: date | None = None
    end_date: date | None = None
    created_at: datetime | None = None


class SubscriptionEventResponse(ApiSchema):
    id: str
    tenant_id: str
    event_type: str
    payload: dict | None = None
    created_at: datetime | None = None


class IncidentResponse(ApiSchema):
    id: str
    tenant_id: str | None = None
    title: str
    description: str | None = None
    severity: str = "info"
    status: str = "open"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IncidentCreate(ApiSchema):
    title: str
    description: str | None = None
    severity: str = "info"
    tenant_id: str | None = None


class IncidentUpdate(ApiSchema):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None


class PlatformAuditEventResponse(ApiSchema):
    id: str
    tenant_id: str | None = None
    actor_name: str | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    detail: dict | None = None
    created_at: datetime | None = None


class HealthSummaryResponse(ApiSchema):
    status: str
    database: str
    version: str
    uptime: str | None = None


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    params: PeriodParams = Depends(),
):
    start, end = resolve_period(params.preset, params.start_date, params.end_date)

    # ── metrics: count tenants by status ──
    status_counts = {}
    stmt = select(Tenant.status, func.count(Tenant.id)).group_by(Tenant.status)
    rows = (await session.execute(stmt)).all()
    for status, cnt in rows:
        status_counts[status] = cnt
    metrics = {
        "activeTenants": status_counts.get("active", 0),
        "trialTenants": status_counts.get("trial", 0),
        "suspendedTenants": status_counts.get("suspended", 0),
        "mrr": money_str(Decimal("0")),
    }

    # ── tenantGrowth: count tenants created per day ──
    tenant_growth = []
    t_stmt = text(
        """
        SELECT d::date AS dt, COALESCE(COUNT(t.id), 0) AS cnt
        FROM generate_series(:start, :end, '1 day'::interval) d
        LEFT JOIN tenants t ON t.created_at::date = d::date
        GROUP BY d::date
        ORDER BY d::date
        """
    )
    t_rows = (await session.execute(t_stmt, {"start": start, "end": end})).all()
    for dt, cnt in t_rows:
        tenant_growth.append({"date": str(dt), "count": cnt})

    # ── planDistribution: count tenants by plan ──
    plan_distribution = []
    total_tenants = sum(c for c in status_counts.values()) or 1
    p_stmt = select(Tenant.plan_code, func.count(Tenant.id)).group_by(Tenant.plan_code)
    p_rows = (await session.execute(p_stmt)).all()
    for plan_code, cnt in p_rows:
        plan_distribution.append({
            "plan": plan_code or "unknown",
            "count": cnt,
            "percentage": round(cnt / total_tenants * 100, 1),
        })

    # ── recentActivity: last 20 audit events ──
    recent_activity = []
    a_stmt = (
        select(PlatformAuditEvent)
        .order_by(PlatformAuditEvent.created_at.desc())
        .limit(20)
    )
    a_rows = (await session.execute(a_stmt)).scalars().all()
    for ev in a_rows:
        recent_activity.append({
            "id": str(ev.id),
            "timestamp": ev.created_at.isoformat() if ev.created_at else None,
            "action": ev.action,
            "tenantName": ev.actor_name or "",
            "actorName": ev.actor_name or "",
        })

    return DashboardResponse(
        period={
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "timezone": "UTC",
        },
        metrics=metrics,
        tenant_growth=tenant_growth,
        plan_distribution=plan_distribution,
        recent_activity=recent_activity,
    )


@router.get("/tenants", response_model=PaginatedResponse[TenantResponse])
async def list_tenants(
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
    status: str | None = Query(None),
):
    conditions = []
    if params.search:
        like = f"%{params.search}%"
        conditions.append(or_(Tenant.name.ilike(like), Tenant.slug.ilike(like)))
    if status:
        conditions.append(Tenant.status == status)

    where = and_(*conditions) if conditions else True

    total_q = select(func.count(Tenant.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Tenant)
        .where(where)
        .order_by(Tenant.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [TenantResponse.model_validate(t) for t in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(
    body: TenantCreate,
    session: AsyncSession = Depends(get_session),
):
    dup = (await session.execute(select(Tenant).where(Tenant.slug == body.slug))).scalar_one_or_none()
    if dup:
        raise ConflictError(message=f"Slug '{body.slug}' sudah digunakan")

    now = datetime.now(timezone.utc)
    tenant = Tenant(
        id=new_uuid(),
        name=body.name,
        slug=body.slug,
        plan_code=body.plan_code or "free",
        timezone=body.timezone or "Asia/Jakarta",
        currency=body.currency or "IDR",
        sector=body.sector,
        legal_name=body.legal_name or body.name,
        status="active",
        onboarding_status="pending",
        created_at=now,
        updated_at=now,
    )
    session.add(tenant)

    org = OrganizationSetting(
        id=new_uuid(),
        tenant_id=tenant.id,
        tenant_name=tenant.name,
        legal_name=tenant.legal_name,
        timezone=tenant.timezone,
        currency=tenant.currency,
        created_at=now,
        updated_at=now,
    )
    session.add(org)

    branch = Branch(
        id=new_uuid(),
        tenant_id=tenant.id,
        code="main",
        name="Kantor Pusat",
        is_main=True,
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(branch)

    sub = Subscription(
        id=new_uuid(),
        tenant_id=tenant.id,
        plan_code=tenant.plan_code,
        status="active",
        start_date=now.date(),
        created_at=now,
        updated_at=now,
    )
    session.add(sub)

    await session.commit()
    await session.refresh(tenant)
    return TenantResponse.model_validate(tenant)


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
    if not t:
        raise NotFoundError(message="Tenant tidak ditemukan")
    return TenantResponse.model_validate(t)


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    body: TenantUpdate,
    tenant_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
    if not t:
        raise NotFoundError(message="Tenant tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(t, field, value)
    t.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(t)
    return TenantResponse.model_validate(t)


@router.delete("/tenants/{tenant_id}", status_code=204)
async def delete_tenant(
    tenant_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
    if not t:
        raise NotFoundError(message="Tenant tidak ditemukan")
    await session.delete(t)
    await session.commit()


@router.post("/tenants/{tenant_id}/suspend", response_model=TenantResponse)
async def suspend_tenant(
    tenant_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
    if not t:
        raise NotFoundError(message="Tenant tidak ditemukan")
    t.status = "suspended"
    t.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(t)
    return TenantResponse.model_validate(t)


@router.post("/tenants/{tenant_id}/reactivate", response_model=TenantResponse)
async def reactivate_tenant(
    tenant_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
    if not t:
        raise NotFoundError(message="Tenant tidak ditemukan")
    t.status = "active"
    t.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(t)
    return TenantResponse.model_validate(t)


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
):
    conditions = []
    if params.search:
        like = f"%{params.search}%"
        conditions.append(or_(User.name.ilike(like), User.email.ilike(like)))

    where = and_(*conditions) if conditions else True

    total_q = select(func.count(User.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(User)
        .where(where)
        .order_by(User.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [UserResponse.model_validate(u) for u in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    body: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    dup = (await session.execute(select(User).where(User.email == body.email))).scalar_one_or_none()
    if dup:
        raise ConflictError(message=f"Email '{body.email}' sudah terdaftar")

    now = datetime.now(timezone.utc)
    user = User(
        id=new_uuid(),
        name=body.name,
        email=body.email,
        password_hash=body.password_hash or "",
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not u:
        raise NotFoundError(message="User tidak ditemukan")
    return UserResponse.model_validate(u)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    body: UserUpdate,
    user_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not u:
        raise NotFoundError(message="User tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(u, field, value)
    u.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(u)
    return UserResponse.model_validate(u)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not u:
        raise NotFoundError(message="User tidak ditemukan")
    await session.delete(u)
    await session.commit()


@router.get("/subscriptions", response_model=PaginatedResponse[SubscriptionResponse])
async def list_subscriptions(
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
):
    total_q = select(func.count(Subscription.id))
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Subscription)
        .order_by(Subscription.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [SubscriptionResponse.model_validate(s) for s in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.get("/subscription-events", response_model=PaginatedResponse[SubscriptionEventResponse])
async def list_subscription_events(
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
    period: PeriodParams = Depends(),
    search: str | None = Query(None),
):
    conditions = []

    if search:
        like = f"%{search}%"
        conditions.append(
            or_(
                SubscriptionEvent.tenant_id.ilike(like),
                text("EXISTS (SELECT 1 FROM tenants t WHERE t.id = subscription_events.tenant_id AND (t.name ILIKE :s OR t.slug ILIKE :s))").bindparams(s=like),
            )
        )

    where = and_(*conditions) if conditions else True

    total_q = select(func.count(SubscriptionEvent.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(SubscriptionEvent)
        .where(where)
        .order_by(SubscriptionEvent.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [SubscriptionEventResponse.model_validate(e) for e in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.get("/incidents", response_model=PaginatedResponse[IncidentResponse])
async def list_incidents(
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
    status: str | None = Query(None),
    severity: str | None = Query(None),
):
    conditions = []
    if status:
        conditions.append(Incident.status == status)
    if severity:
        conditions.append(Incident.severity == severity)

    where = and_(*conditions) if conditions else True

    total_q = select(func.count(Incident.id)).where(where)
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(Incident)
        .where(where)
        .order_by(Incident.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [IncidentResponse.model_validate(i) for i in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(
    body: IncidentCreate,
    session: AsyncSession = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    incident = Incident(
        id=new_uuid(),
        tenant_id=body.tenant_id,
        title=body.title,
        description=body.description,
        severity=body.severity,
        status="open",
        created_at=now,
        updated_at=now,
    )
    session.add(incident)
    await session.commit()
    await session.refresh(incident)
    return IncidentResponse.model_validate(incident)


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    body: IncidentUpdate,
    incident_id: str = Path(...),
    session: AsyncSession = Depends(get_session),
):
    inc = (await session.execute(select(Incident).where(Incident.id == incident_id))).scalar_one_or_none()
    if not inc:
        raise NotFoundError(message="Incident tidak ditemukan")

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(inc, field, value)
    inc.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(inc)
    return IncidentResponse.model_validate(inc)


@router.get("/audit-events", response_model=PaginatedResponse[PlatformAuditEventResponse])
async def list_audit_events(
    session: AsyncSession = Depends(get_session),
    params: ListParams = Depends(),
):
    total_q = select(func.count(PlatformAuditEvent.id))
    total = (await session.execute(total_q)).scalar() or 0

    stmt = (
        select(PlatformAuditEvent)
        .order_by(PlatformAuditEvent.created_at.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )
    rows = (await session.execute(stmt)).scalars().all()

    items = [PlatformAuditEventResponse.model_validate(e) for e in rows]
    return make_paginated(items, params.page, params.page_size, total)


@router.get("/health-summary", response_model=HealthSummaryResponse)
async def get_health_summary(
    session: AsyncSession = Depends(get_session),
):
    db_status = "healthy"
    try:
        await session.execute(select(func.now()))
    except Exception:
        db_status = "unhealthy"

    return HealthSummaryResponse(
        status="operational",
        database=db_status,
        version="1.0.0",
        uptime=None,
    )
