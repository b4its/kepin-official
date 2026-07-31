from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from kepin.core.ids import new_uuid
from kepin.db.models import TenantAuditEvent


async def record_audit(
    session: AsyncSession,
    tenant_id: str,
    action: str,
    module: str,
    object_type: str,
    object_id: str,
    actor_id: str | None = None,
    actor_name: str = "",
    before: dict | None = None,
    after: dict | None = None,
    request_id: str = "",
) -> TenantAuditEvent:
    event = TenantAuditEvent(
        id=new_uuid(),
        tenant_id=tenant_id,
        timestamp=datetime.now(timezone.utc),
        actor_id=actor_id,
        actor_name=actor_name,
        action=action,
        module=module,
        object_type=object_type,
        object_id=str(object_id),
        before=before,
        after=after,
        request_id=request_id,
    )
    session.add(event)
    await session.flush()
    return event
