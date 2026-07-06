"""Business logic for recipes, tags and add-to-list."""

import logging
from decimal import Decimal

from fastapi import UploadFile

from app.modules.ingredients.conversion import normalize
from app.modules.ingredients.service import IngredientService
from app.modules.recipes.constants import ADD_TO_LIST_MODES, RECIPE_CATEGORIES
from app.modules.recipes.db_models import RecipeDB, RecipeIngredientDB
from app.modules.recipes.exceptions import (
    DuplicateTagNameError,
    InvalidRecipeCategoryError,
    RecipeNotFoundError,
    RecipeValidationError,
    ShoppingListNotFoundError,
    TagNotFoundError,
)
from app.modules.recipes.image_service import RecipeImageService
from app.modules.recipes.repository import RecipeRepository
from app.modules.recipes.schemas import (
    AddToListResponse,
    RecipeCreateRequest,
    RecipeDetailResponse,
    RecipeIngredientInput,
    RecipeIngredientResponse,
    RecipeSummaryResponse,
    RecipesResponse,
    RecipeUpdateRequest,
    TagCreateRequest,
    TagResponse,
    TagsResponse,
)
from app.modules.shopping.exceptions import InvalidUnitError
from app.modules.shopping.repository import ShoppingRepository
from app.modules.shopping.schemas import ShoppingItemCreateRequest
from app.modules.shopping.service import ShoppingService

logger = logging.getLogger(__name__)


class RecipeService:
    """Service layer for family recipes."""

    def __init__(
        self,
        repository: RecipeRepository,
        shopping_repository: ShoppingRepository,
        shopping_service: ShoppingService,
        ingredient_service: IngredientService,
        image_service: RecipeImageService,
    ):
        self.repository = repository
        self.shopping_repository = shopping_repository
        self.shopping_service = shopping_service
        self.ingredient_service = ingredient_service
        self.image_service = image_service

    # ==================== Tags ====================

    async def list_tags(self, family_id: str) -> TagsResponse:
        tags = await self.repository.list_tags(family_id)
        return TagsResponse(tags=[TagResponse(id=tag.id, name=tag.name) for tag in tags])

    async def create_tag(self, family_id: str, payload: TagCreateRequest) -> TagResponse:
        existing = await self.repository.get_tag_by_name(family_id, payload.name)
        if existing is not None:
            raise DuplicateTagNameError("Tag with this name already exists")
        tag = await self.repository.create_tag(family_id=family_id, name=payload.name)
        return TagResponse(id=tag.id, name=tag.name)

    # ==================== Recipes ====================

    async def list_recipes(
        self,
        family_id: str,
        *,
        category: str | None = None,
        tag_id: str | None = None,
        query: str | None = None,
    ) -> RecipesResponse:
        recipes = await self.repository.list_recipes(family_id, category=category, tag_id=tag_id, query=query)
        tag_map = await self.repository.list_tag_ids_for_recipes([recipe.id for recipe in recipes])
        summaries = [await self._to_summary(recipe, tag_map.get(recipe.id, [])) for recipe in recipes]
        return RecipesResponse(recipes=summaries)

    async def create_recipe(self, family_id: str, user_id: str, payload: RecipeCreateRequest) -> RecipeDetailResponse:
        self._validate_category(payload.category)
        if payload.tagIds and not await self.repository.validate_tag_ids(family_id, payload.tagIds):
            raise TagNotFoundError("One or more tags not found")

        ingredient_rows = await self._prepare_ingredient_rows(payload.ingredients)
        recipe = await self.repository.create_recipe(
            family_id=family_id,
            title=payload.title.strip(),
            source_url=payload.sourceUrl,
            category=payload.category,
            servings=payload.servings,
            created_by=user_id,
            ingredients=ingredient_rows,
            tag_ids=payload.tagIds,
        )
        return await self._to_detail(recipe, payload.tagIds)

    async def get_recipe(self, family_id: str, recipe_id: str) -> RecipeDetailResponse:
        recipe = await self._require_recipe(family_id, recipe_id)
        tag_ids = await self.repository.list_tag_ids_for_recipe(recipe.id)
        return await self._to_detail(recipe, tag_ids)

    async def update_recipe(self, family_id: str, recipe_id: str, payload: RecipeUpdateRequest) -> RecipeDetailResponse:
        recipe = await self._require_recipe(family_id, recipe_id)

        if payload.title is not None:
            recipe.title = payload.title.strip()
        if payload.sourceUrl is not None:
            recipe.source_url = payload.sourceUrl or None
        if payload.category is not None:
            self._validate_category(payload.category)
            recipe.category = payload.category
        if payload.servings is not None:
            recipe.servings = payload.servings

        if payload.ingredients is not None:
            if not payload.ingredients:
                raise RecipeValidationError("Recipe must have at least one ingredient")
            rows = await self._prepare_ingredient_rows(payload.ingredients)
            await self.repository.replace_ingredients(recipe.id, rows)

        if payload.tagIds is not None:
            if payload.tagIds and not await self.repository.validate_tag_ids(family_id, payload.tagIds):
                raise TagNotFoundError("One or more tags not found")
            await self.repository.replace_tags(recipe.id, payload.tagIds)

        await self.repository.update_recipe(recipe)
        tag_ids = payload.tagIds if payload.tagIds is not None else await self.repository.list_tag_ids_for_recipe(recipe.id)
        return await self._to_detail(recipe, tag_ids)

    async def delete_recipe(self, family_id: str, recipe_id: str) -> None:
        recipe = await self._require_recipe(family_id, recipe_id)
        await self.repository.soft_delete_recipe(recipe)

    async def upload_image(self, family_id: str, recipe_id: str, file: UploadFile) -> str:
        recipe = await self._require_recipe(family_id, recipe_id)
        return await self.image_service.upload(recipe, file)

    async def add_to_list(
        self,
        family_id: str,
        user_id: str,
        recipe_id: str,
        list_id: str,
        mode: str,
    ) -> AddToListResponse:
        if mode not in ADD_TO_LIST_MODES:
            raise InvalidRecipeCategoryError(f"Invalid mode '{mode}'")

        recipe = await self._require_recipe(family_id, recipe_id)
        shopping_list = await self.shopping_repository.get_list(list_id, family_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError("Shopping list not found")

        ingredients = await self.repository.list_ingredients(recipe.id)
        existing_items = await self.shopping_repository.list_items(list_id)

        added = 0
        skipped = 0
        for ingredient in ingredients:
            if mode == "missing" and self._ingredient_on_list(ingredient, existing_items):
                skipped += 1
                continue
            try:
                await self.shopping_service.add_item(
                    family_id,
                    list_id,
                    user_id,
                    ShoppingItemCreateRequest(
                        name=ingredient.name,
                        quantity=float(ingredient.quantity) if ingredient.quantity is not None else None,
                        unit=ingredient.unit,
                    ),
                )
                added += 1
                existing_items = await self.shopping_repository.list_items(list_id)
            except InvalidUnitError:
                logger.warning("Skipping recipe ingredient with invalid unit: %s", ingredient.name)
                skipped += 1

        return AddToListResponse(addedCount=added, skippedCount=skipped)

    # ==================== Helpers ====================

    async def _require_recipe(self, family_id: str, recipe_id: str) -> RecipeDB:
        recipe = await self.repository.get_recipe(recipe_id, family_id)
        if recipe is None:
            raise RecipeNotFoundError("Recipe not found")
        return recipe

    def _validate_category(self, category: str) -> None:
        if category not in RECIPE_CATEGORIES:
            raise InvalidRecipeCategoryError(f"Invalid category '{category}'")

    async def _prepare_ingredient_rows(self, ingredients: list[RecipeIngredientInput]) -> list[tuple[str, str | None, Decimal | None, str | None, int]]:
        rows: list[tuple[str, str | None, Decimal | None, str | None, int]] = []
        for index, ingredient in enumerate(ingredients):
            match = await self.ingredient_service.match(ingredient.name)
            quantity = Decimal(str(ingredient.quantity)) if ingredient.quantity is not None else None
            rows.append(
                (
                    ingredient.name.strip(),
                    match.ingredient_id if match else None,
                    quantity,
                    ingredient.unit,
                    index,
                )
            )
        return rows

    def _ingredient_on_list(self, ingredient: RecipeIngredientDB, items: list) -> bool:
        normalized = normalize(ingredient.name)
        for item in items:
            if ingredient.ingredient_id and item.ingredient_id == ingredient.ingredient_id:
                return True
            if normalize(item.name) == normalized:
                return True
        return False

    async def _to_summary(self, recipe: RecipeDB, tag_ids: list[str]) -> RecipeSummaryResponse:
        return RecipeSummaryResponse(
            id=recipe.id,
            title=recipe.title,
            sourceUrl=recipe.source_url,
            imageUrl=await self.image_service.resolve_url(recipe.image_path),
            category=recipe.category,
            servings=recipe.servings,
            tagIds=tag_ids,
            createdAt=recipe.created_at,
            updatedAt=recipe.updated_at,
        )

    async def _to_detail(self, recipe: RecipeDB, tag_ids: list[str]) -> RecipeDetailResponse:
        ingredients = await self.repository.list_ingredients(recipe.id)
        summary = await self._to_summary(recipe, tag_ids)
        return RecipeDetailResponse(
            **summary.model_dump(),
            ingredients=[
                RecipeIngredientResponse(
                    id=row.id,
                    name=row.name,
                    ingredientId=row.ingredient_id,
                    quantity=float(row.quantity) if row.quantity is not None else None,
                    unit=row.unit,
                    sortOrder=row.sort_order,
                )
                for row in ingredients
            ],
        )
