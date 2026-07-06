"""API routers for shopping lists, categories and items."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.family.dependencies import CurrentFamilyId
from app.modules.ingredients.repository import IngredientRepository, get_ingredient_repository
from app.modules.ingredients.service import IngredientService
from app.modules.shopping.exceptions import (
    CategoryNotFoundError,
    InvalidUnitError,
    ShoppingItemNotFoundError,
    ShoppingListNotFoundError,
)
from app.modules.shopping.repository import ShoppingRepository, get_shopping_repository
from app.modules.shopping.schemas import (
    CategoriesResponse,
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    QuickAddRequest,
    ReorderRequest,
    ShoppingItemCreateRequest,
    ShoppingItemResponse,
    ShoppingItemUpdateRequest,
    ShoppingListCreateRequest,
    ShoppingListDetailResponse,
    ShoppingListResponse,
    ShoppingListsResponse,
    ShoppingListUpdateRequest,
)
from app.modules.shopping.service import ShoppingService

categories_router = APIRouter(prefix="/categories", tags=["Shopping"])
shopping_lists_router = APIRouter(prefix="/shopping-lists", tags=["Shopping"])


def get_shopping_service(
    repo: Annotated[ShoppingRepository, Depends(get_shopping_repository)],
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
) -> ShoppingService:
    """FastAPI dependency to obtain the shopping service (with ingredient matching)."""
    return ShoppingService(repository=repo, matcher=IngredientService(repository=ingredient_repo))


ShoppingServiceDep = Annotated[ShoppingService, Depends(get_shopping_service)]


def _not_found(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _bad_request(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ==================== Categories ====================


@categories_router.get("", response_model=CategoriesResponse)
async def list_categories(family_id: CurrentFamilyId, service: ShoppingServiceDep) -> CategoriesResponse:
    """List the categories of the current user's family."""
    return await service.list_categories(family_id)


@categories_router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
async def create_category(payload: CategoryCreateRequest, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> CategoryResponse:
    """Create a new category."""
    return await service.create_category(family_id, payload)


@categories_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, payload: CategoryUpdateRequest, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> CategoryResponse:
    """Update a category (name, icon, sort order)."""
    try:
        return await service.update_category(family_id, category_id, payload)
    except CategoryNotFoundError as e:
        raise _not_found(e)


@categories_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> None:
    """Delete a category (items keep their name, lose the category)."""
    try:
        await service.delete_category(family_id, category_id)
    except CategoryNotFoundError as e:
        raise _not_found(e)


# ==================== Shopping lists ====================


@shopping_lists_router.get("", response_model=ShoppingListsResponse)
async def list_shopping_lists(family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingListsResponse:
    """List the shopping lists of the current user's family."""
    return await service.list_lists(family_id)


@shopping_lists_router.post("", status_code=status.HTTP_201_CREATED, response_model=ShoppingListResponse)
async def create_shopping_list(payload: ShoppingListCreateRequest, current_user: CurrentUser, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingListResponse:
    """Create a shopping list (seeds default categories on first list)."""
    return await service.create_list(family_id, current_user.id, payload)


@shopping_lists_router.get("/{list_id}", response_model=ShoppingListDetailResponse)
async def get_shopping_list(list_id: str, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingListDetailResponse:
    """Get a shopping list with its items."""
    try:
        return await service.get_list_detail(family_id, list_id)
    except ShoppingListNotFoundError as e:
        raise _not_found(e)


@shopping_lists_router.patch("/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(list_id: str, payload: ShoppingListUpdateRequest, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingListResponse:
    """Rename a shopping list."""
    try:
        return await service.update_list(family_id, list_id, payload)
    except ShoppingListNotFoundError as e:
        raise _not_found(e)


@shopping_lists_router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(list_id: str, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> None:
    """Soft-delete a shopping list (tombstone for sync)."""
    try:
        await service.delete_list(family_id, list_id)
    except ShoppingListNotFoundError as e:
        raise _not_found(e)


# ==================== Items ====================


@shopping_lists_router.post("/{list_id}/items", status_code=status.HTTP_201_CREATED, response_model=ShoppingItemResponse)
async def add_item(list_id: str, payload: ShoppingItemCreateRequest, current_user: CurrentUser, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingItemResponse:
    """Add an item to a shopping list."""
    try:
        return await service.add_item(family_id, list_id, current_user.id, payload)
    except ShoppingListNotFoundError as e:
        raise _not_found(e)
    except (CategoryNotFoundError, InvalidUnitError) as e:
        raise _bad_request(e)


@shopping_lists_router.post("/{list_id}/items/quick-add", status_code=status.HTTP_201_CREATED, response_model=ShoppingItemResponse)
async def quick_add_item(list_id: str, payload: QuickAddRequest, current_user: CurrentUser, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingItemResponse:
    """Quick-add an item from free text (parses quantity/unit)."""
    try:
        return await service.quick_add(family_id, list_id, current_user.id, payload)
    except ShoppingListNotFoundError as e:
        raise _not_found(e)


@shopping_lists_router.patch("/{list_id}/items/{item_id}", response_model=ShoppingItemResponse)
async def update_item(list_id: str, item_id: str, payload: ShoppingItemUpdateRequest, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> ShoppingItemResponse:
    """Update an item or toggle its checked state."""
    try:
        return await service.update_item(family_id, list_id, item_id, payload)
    except (ShoppingListNotFoundError, ShoppingItemNotFoundError) as e:
        raise _not_found(e)
    except (CategoryNotFoundError, InvalidUnitError) as e:
        raise _bad_request(e)


@shopping_lists_router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(list_id: str, item_id: str, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> None:
    """Soft-delete an item."""
    try:
        await service.delete_item(family_id, list_id, item_id)
    except (ShoppingListNotFoundError, ShoppingItemNotFoundError) as e:
        raise _not_found(e)


@shopping_lists_router.post("/{list_id}/items/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_items(list_id: str, payload: ReorderRequest, family_id: CurrentFamilyId, service: ShoppingServiceDep) -> None:
    """Batch-update item positions."""
    try:
        await service.reorder(family_id, list_id, payload)
    except ShoppingListNotFoundError as e:
        raise _not_found(e)
