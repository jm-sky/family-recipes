"""API router for ingredient search."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import CurrentUser
from app.modules.ingredients.repository import IngredientRepository, get_ingredient_repository
from app.modules.ingredients.schemas import IngredientsResponse
from app.modules.ingredients.service import IngredientService

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


def get_ingredient_service_dep(repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)]) -> IngredientService:
    """FastAPI dependency to obtain the ingredient service."""
    return IngredientService(repository=repo)


IngredientServiceDep = Annotated[IngredientService, Depends(get_ingredient_service_dep)]


@router.get("", response_model=IngredientsResponse)
async def search_ingredients(current_user: CurrentUser, service: IngredientServiceDep, q: str | None = None) -> IngredientsResponse:
    """Search the canonical ingredient dataset (or list all when no query)."""
    return await service.search(q)
