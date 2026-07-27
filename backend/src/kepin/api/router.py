from fastapi import APIRouter
from sqlalchemy import text
from kepin.core.config import get_settings
from kepin.db.session import get_session
from kepin.modules.platform.api import router as platform_router
from kepin.modules.tenants.api import router as tenants_router
from kepin.modules.organization.api import router as org_router
from kepin.modules.reporting.api import router as reports_router
from kepin.modules.notifications.api import router as notif_router
from kepin.modules.audit.api import router as audit_router
from kepin.modules.accounting.api import router as accounting_router
from kepin.modules.sales.api import router as sales_router
from kepin.modules.purchasing.api import router as purchasing_router
from kepin.modules.inventory.api import router as inventory_router
from kepin.modules.users.api import router as dev_auth_router

api_router = APIRouter(prefix="/api/v1")

TENANT_PREFIX = "/tenants/{tenantSlug}"

api_router.include_router(platform_router, prefix="/platform")
api_router.include_router(tenants_router, prefix=TENANT_PREFIX)
api_router.include_router(org_router, prefix=TENANT_PREFIX)
api_router.include_router(reports_router, prefix=TENANT_PREFIX)
api_router.include_router(notif_router, prefix=TENANT_PREFIX)
api_router.include_router(audit_router, prefix=TENANT_PREFIX)
api_router.include_router(accounting_router, prefix=TENANT_PREFIX)
api_router.include_router(sales_router, prefix=TENANT_PREFIX)
api_router.include_router(purchasing_router, prefix=TENANT_PREFIX)
api_router.include_router(inventory_router, prefix=TENANT_PREFIX)

settings = get_settings()
if settings.is_development:
    api_router.include_router(dev_auth_router, prefix="/dev-auth")


@api_router.get("/health/live", tags=["health"])
async def health_live():
    return {"status": "ok"}


@api_router.get("/health/ready", tags=["health"])
async def health_ready():
    async for session in get_session():
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}


@api_router.get("/health/startup", tags=["health"])
async def health_startup():
    return {"status": "ok"}
