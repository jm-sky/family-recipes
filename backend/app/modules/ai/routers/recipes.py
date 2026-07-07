"""Router for AI recipe import."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.ai.cache.postgres_cache import PostgresCacheService
from app.modules.ai.dependencies import AdminUser
from app.modules.ai.exceptions import RecipeImportError, StructuredOutputParsingError
from app.modules.ai.repositories import HistoryRepository, SettingsRepository
from app.modules.ai.schemas import RecipeImportRequest, RecipeImportResponse
from app.modules.ai.services import RecipeImportService, SettingsService
from app.modules.ingredients.repository import IngredientRepository, get_ingredient_repository
from app.modules.ingredients.service import IngredientService

router = APIRouter(prefix="/recipes", tags=["ai-recipes"])


def require_ai_enabled() -> None:
    """Reject requests when AI is disabled globally."""
    if not settings.ai.enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI features are disabled")


def get_recipe_import_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
) -> RecipeImportService:
    """Build recipe import service with dependencies."""
    settings_repo = SettingsRepository(db)
    settings_service = SettingsService(settings_repo)
    history_repo = HistoryRepository(db)
    ingredient_service = IngredientService(repository=ingredient_repo)
    cache_service = PostgresCacheService(db)
    return RecipeImportService(
        settings_service=settings_service,
        history_repo=history_repo,
        ingredient_service=ingredient_service,
        cache_service=cache_service,
    )


RecipeImportServiceDep = Annotated[RecipeImportService, Depends(get_recipe_import_service)]


@router.post("/import", response_model=RecipeImportResponse, dependencies=[Depends(require_ai_enabled)])
async def import_recipe(
    payload: RecipeImportRequest,
    current_user: AdminUser,
    service: RecipeImportServiceDep,
) -> RecipeImportResponse:
    """Import a recipe draft from an external URL (does not persist)."""
    try:
        return await service.import_from_url(current_user.id, payload.url)
    except RecipeImportError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StructuredOutputParsingError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
