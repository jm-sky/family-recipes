"""Main API router aggregating all module routers."""

from fastapi import APIRouter, Depends

from app.core.health_details import build_health_details, verify_health_details_token

# Module routers registration
# When you add modules using 'fastapi-registry add <module>', the CLI will automatically
# add the necessary imports and include_router calls here.
from app.modules.admin.router import router as admin_router
from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.family.router import invitations_router
from app.modules.family.router import router as families_router
from app.modules.feature_limits.router import router as feature_limits_router
from app.modules.ingredients.router import router as ingredients_router
from app.modules.logs.router import router as logs_router
from app.modules.recipes.router import recipes_router, tags_router
from app.modules.shopping.router import categories_router, shopping_lists_router
from app.modules.settings.router import router as settings_router
from app.modules.stats.router import router as stats_router
from app.modules.users.router import router as users_router

# Main API router
api_router = APIRouter()


# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status message
    """
    return {"status": "healthy"}


# Detailed health endpoint for Ops Monitor (bearer-token protected)
@api_router.get(
    "/health/details",
    tags=["Health"],
    dependencies=[Depends(verify_health_details_token)],
)
async def health_check_details() -> dict:
    """
    Detailed health check for Ops Monitor.

    Reports per-component status (database, cache, storage, frontend) per the
    ops-monitor health schema contract. Requires ``Authorization: Bearer
    <HEALTH_DETAILS_TOKEN>``.

    Returns:
        Health details response (schema_version, status, components, ...)
    """
    return await build_health_details()


# Register module routers
api_router.include_router(admin_router)
api_router.include_router(ai_router)
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(billing_router)
api_router.include_router(feature_limits_router)
api_router.include_router(logs_router, prefix="/logs", tags=["Logs", "Monitoring"])
api_router.include_router(stats_router, prefix="/stats", tags=["Statistics"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(settings_router, prefix="/me/settings", tags=["Settings"])
api_router.include_router(families_router)
api_router.include_router(invitations_router)
api_router.include_router(categories_router)
api_router.include_router(shopping_lists_router)
api_router.include_router(ingredients_router)
api_router.include_router(recipes_router)
api_router.include_router(tags_router)

# Register Two-Factor module (optional, added during development)
try:
    from app.modules.two_factor.router import router as two_factor_router

    api_router.include_router(
        two_factor_router,
        prefix="/two-factor",
        tags=["Two-Factor Authentication", "Security", "WebAuthn", "TOTP"],
    )
except ImportError:
    # Module may be absent in some builds; ignore if not present
    pass
