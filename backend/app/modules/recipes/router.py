"""API routers for recipes and tags."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.family.dependencies import CurrentFamilyId
from app.modules.ingredients.repository import IngredientRepository, get_ingredient_repository
from app.modules.ingredients.service import IngredientService
from app.modules.recipes.exceptions import (
    DuplicateTagNameError,
    InvalidRecipeCategoryError,
    RecipeNotFoundError,
    RecipeValidationError,
    ShoppingListNotFoundError,
    TagNotFoundError,
)
from app.modules.recipes.image_service import RecipeImageService
from app.modules.recipes.repository import RecipeRepository, get_recipe_repository
from app.modules.recipes.schemas import (
    AddToListRequest,
    AddToListResponse,
    RecipeCreateRequest,
    RecipeDetailResponse,
    RecipeImageResponse,
    RecipesResponse,
    RecipeUpdateRequest,
    TagCreateRequest,
    TagResponse,
    TagsResponse,
)
from app.modules.recipes.service import RecipeService
from app.modules.shopping.exceptions import InvalidUnitError
from app.modules.shopping.repository import ShoppingRepository, get_shopping_repository
from app.modules.shopping.service import ShoppingService

recipes_router = APIRouter(prefix="/recipes", tags=["Recipes"])
tags_router = APIRouter(prefix="/tags", tags=["Recipes"])


def get_recipe_service(
    repo: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    shopping_repo: Annotated[ShoppingRepository, Depends(get_shopping_repository)],
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
) -> RecipeService:
    """FastAPI dependency to obtain the recipe service."""
    ingredient_service = IngredientService(repository=ingredient_repo)
    shopping_service = ShoppingService(repository=shopping_repo, matcher=ingredient_service)
    return RecipeService(
        repository=repo,
        shopping_repository=shopping_repo,
        shopping_service=shopping_service,
        ingredient_service=ingredient_service,
        image_service=RecipeImageService(repository=repo),
    )


RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]


# ==================== Tags ====================


@tags_router.get("", response_model=TagsResponse)
async def list_tags(family_id: CurrentFamilyId, service: RecipeServiceDep) -> TagsResponse:
    """List tags for the current family."""
    return await service.list_tags(family_id)


@tags_router.post("", status_code=status.HTTP_201_CREATED, response_model=TagResponse)
async def create_tag(payload: TagCreateRequest, family_id: CurrentFamilyId, service: RecipeServiceDep) -> TagResponse:
    """Create a new tag."""
    try:
        return await service.create_tag(family_id, payload)
    except DuplicateTagNameError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ==================== Recipes ====================


@recipes_router.get("", response_model=RecipesResponse)
async def list_recipes(
    family_id: CurrentFamilyId,
    service: RecipeServiceDep,
    category: str | None = None,
    tag: str | None = None,
    q: str | None = None,
) -> RecipesResponse:
    """List family recipes with optional filters."""
    return await service.list_recipes(family_id, category=category, tag_id=tag, query=q)


@recipes_router.post("", status_code=status.HTTP_201_CREATED, response_model=RecipeDetailResponse)
async def create_recipe(
    payload: RecipeCreateRequest,
    current_user: CurrentUser,
    family_id: CurrentFamilyId,
    service: RecipeServiceDep,
) -> RecipeDetailResponse:
    """Create a recipe with ingredients and optional tags."""
    try:
        return await service.create_recipe(family_id, current_user.id, payload)
    except (InvalidRecipeCategoryError, TagNotFoundError, RecipeValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@recipes_router.get("/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe(recipe_id: str, family_id: CurrentFamilyId, service: RecipeServiceDep) -> RecipeDetailResponse:
    """Get a recipe with ingredients and tags."""
    try:
        return await service.get_recipe(family_id, recipe_id)
    except RecipeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@recipes_router.patch("/{recipe_id}", response_model=RecipeDetailResponse)
async def update_recipe(
    recipe_id: str,
    payload: RecipeUpdateRequest,
    family_id: CurrentFamilyId,
    service: RecipeServiceDep,
) -> RecipeDetailResponse:
    """Update a recipe."""
    try:
        return await service.update_recipe(family_id, recipe_id, payload)
    except RecipeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidRecipeCategoryError, TagNotFoundError, RecipeValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@recipes_router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: str, family_id: CurrentFamilyId, service: RecipeServiceDep) -> None:
    """Soft-delete a recipe."""
    try:
        await service.delete_recipe(family_id, recipe_id)
    except RecipeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@recipes_router.post("/{recipe_id}/image", response_model=RecipeImageResponse)
async def upload_recipe_image(
    recipe_id: str,
    family_id: CurrentFamilyId,
    service: RecipeServiceDep,
    file: UploadFile = File(...),
) -> RecipeImageResponse:
    """Upload or replace the recipe cover image."""
    try:
        image_url = await service.upload_image(family_id, recipe_id, file)
        return RecipeImageResponse(imageUrl=image_url)
    except RecipeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@recipes_router.post("/{recipe_id}/add-to-list", response_model=AddToListResponse)
async def add_recipe_to_list(
    recipe_id: str,
    payload: AddToListRequest,
    current_user: CurrentUser,
    family_id: CurrentFamilyId,
    service: RecipeServiceDep,
    mode: Literal["all", "missing"] = "all",
) -> AddToListResponse:
    """Add recipe ingredients to a shopping list (all or missing only)."""
    try:
        return await service.add_to_list(family_id, current_user.id, recipe_id, payload.listId, mode)
    except RecipeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ShoppingListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidRecipeCategoryError, InvalidUnitError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
