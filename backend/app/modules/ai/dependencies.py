"""FastAPI dependencies for AI module."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ai.db_models import AIHistoryDB
from app.modules.ai.repositories import SettingsRepository
from app.modules.auth.dependencies import PremiumOrHigherUser, get_current_user
from app.modules.auth.models import User
from app.modules.billing.plan_constants import PAID_PLAN_TIERS, PLAN_AI_COST_LIMIT_USD
from app.modules.family.repository import FamilyRepository


async def _family_system_ai_cost_this_month(db: AsyncSession, family_id: str) -> float:
    """Sum system-key AI spend (USD) for all family members in the current calendar month."""
    family_repo = FamilyRepository(db)
    member_ids = await family_repo.list_member_user_ids(family_id)
    if not member_ids:
        return 0.0

    month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(AIHistoryDB.cost_usd, AIHistoryDB.metadata_).where(
            AIHistoryDB.user_id.in_(member_ids),
            AIHistoryDB.created_at >= month_start,
        )
    )
    total = 0.0
    for cost_usd, metadata in result.all():
        if metadata and metadata.get("used_own_token"):
            continue
        if cost_usd is not None:
            total += float(cost_usd)
    return total


async def require_ai_access(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require AI feature access.

    Access is granted when:
    - System admin/owner (ops bypass), or
    - Family plan is basic/pro (system OpenRouter key, within monthly family USD budget), or
    - User has configured their own OpenRouter API token (BYOK)

    Raises:
        HTTPException: If the user does not have access to AI features.
    """
    if current_user.isAdmin or current_user.isOwner:
        return current_user

    settings_repo = SettingsRepository(db)
    settings = await settings_repo.get_by_user_id(current_user.id)
    has_byok = bool(settings and settings.use_own_token and settings.encrypted_api_token)

    family_repo = FamilyRepository(db)
    membership = await family_repo.get_membership_for_user(current_user.id)
    family = await family_repo.get_family(membership.family_id) if membership else None
    family_plan = family.plan if family else "free"

    if family_plan in PAID_PLAN_TIERS:
        if has_byok:
            return current_user
        limit = PLAN_AI_COST_LIMIT_USD.get(family_plan, 0.0)
        used = await _family_system_ai_cost_this_month(db, membership.family_id) if membership else 0.0
        if used >= limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(f"Family AI budget exhausted for this month " f"(${used:.2f} / ${limit:.2f}). Try again next month or add your own OpenRouter key."),
            )
        return current_user

    if has_byok:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=("AI features require a paid family plan (Basic/Pro) or your own OpenRouter API token. " "Upgrade the family plan or configure a token in settings."),
    )


AiAccessUser = Annotated[User, Depends(require_ai_access)]

# Backwards-compatible alias (misnamed; prefer AiAccessUser)
AdminUser = AiAccessUser

PremiumOrHigherUserAlias = PremiumOrHigherUser
