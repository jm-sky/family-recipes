"""FastAPI dependencies for AI module."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ai.repositories import SettingsRepository
from app.modules.auth.dependencies import PremiumOrHigherUser, get_current_user
from app.modules.auth.models import User


async def require_ai_access(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require AI feature access.

    AI features are available for:
    - Premium users, administrators, and owners (may use the system OpenRouter token)
    - Regular users who have configured their own OpenRouter API token

    Raises:
        HTTPException: If the user does not have access to AI features.
    """
    if current_user.isPremium or current_user.isAdmin or current_user.isOwner:
        return current_user

    settings_repo = SettingsRepository(db)
    settings = await settings_repo.get_by_user_id(current_user.id)

    if settings and settings.use_own_token and settings.encrypted_api_token:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="AI features require Premium access or your own OpenRouter API token. Please upgrade to Premium or configure your own API token in settings.",
    )


AiAccessUser = Annotated[User, Depends(require_ai_access)]

# Backwards-compatible alias (misnamed; prefer AiAccessUser)
AdminUser = AiAccessUser

PremiumOrHigherUserAlias = PremiumOrHigherUser
