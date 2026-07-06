"""Unit tests for the recipes service."""

from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.modules.recipes.db_models import RecipeDB, RecipeIngredientDB
from app.modules.recipes.exceptions import RecipeNotFoundError
from app.modules.recipes.schemas import RecipeCreateRequest, RecipeIngredientInput
from app.modules.recipes.service import RecipeService
from app.modules.shopping.db_models import ShoppingListDB


@pytest.fixture
def mock_recipe_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_shopping_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_shopping_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_ingredient_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_image_service() -> AsyncMock:
    service = AsyncMock()
    service.resolve_url.return_value = None
    return service


@pytest.fixture
def recipe_service(
    mock_recipe_repo: AsyncMock,
    mock_shopping_repo: AsyncMock,
    mock_shopping_service: AsyncMock,
    mock_ingredient_service: AsyncMock,
    mock_image_service: AsyncMock,
) -> RecipeService:
    return RecipeService(
        repository=mock_recipe_repo,
        shopping_repository=mock_shopping_repo,
        shopping_service=mock_shopping_service,
        ingredient_service=mock_ingredient_service,
        image_service=mock_image_service,
    )


def make_recipe() -> RecipeDB:
    now = datetime.now(UTC)
    return RecipeDB(
        id="recipe1",
        family_id="fam1",
        title="Naleśniki",
        source_url="https://example.com",
        image_path=None,
        category="breakfast",
        servings=4,
        created_by="user1",
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


class TestCreateRecipe:
    @pytest.mark.asyncio
    async def test_create_recipe_matches_ingredients(self, recipe_service: RecipeService, mock_recipe_repo: AsyncMock, mock_ingredient_service: AsyncMock) -> None:
        mock_recipe_repo.validate_tag_ids.return_value = True
        mock_ingredient_service.match.return_value = SimpleNamespace(ingredient_id="flour")
        mock_recipe_repo.create_recipe.return_value = make_recipe()
        mock_recipe_repo.list_ingredients.return_value = [
            RecipeIngredientDB(
                id="ing1",
                recipe_id="recipe1",
                name="mąki",
                ingredient_id="flour",
                quantity=Decimal("200"),
                unit="g",
                sort_order=0,
            )
        ]

        payload = RecipeCreateRequest(
            title="Naleśniki",
            category="breakfast",
            servings=4,
            ingredients=[RecipeIngredientInput(name="mąki", quantity=200, unit="g")],
        )
        response = await recipe_service.create_recipe("fam1", "user1", payload)

        assert response.title == "Naleśniki"
        assert len(response.ingredients) == 1
        mock_recipe_repo.create_recipe.assert_awaited_once()


class TestAddToList:
    @pytest.mark.asyncio
    async def test_add_missing_skips_existing(self, recipe_service: RecipeService, mock_recipe_repo: AsyncMock, mock_shopping_repo: AsyncMock, mock_shopping_service: AsyncMock) -> None:
        recipe = make_recipe()
        mock_recipe_repo.get_recipe.return_value = recipe
        mock_shopping_repo.get_list.return_value = ShoppingListDB(
            id="list1",
            family_id="fam1",
            name="Dom",
            created_by="user1",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_recipe_repo.list_ingredients.return_value = [
            RecipeIngredientDB(id="i1", recipe_id="recipe1", name="mąki", ingredient_id="flour", quantity=Decimal("200"), unit="g", sort_order=0),
            RecipeIngredientDB(id="i2", recipe_id="recipe1", name="mleko", ingredient_id=None, quantity=Decimal("250"), unit="ml", sort_order=1),
        ]
        mock_shopping_repo.list_items.return_value = [
            SimpleNamespace(ingredient_id="flour", name="mąki"),
        ]

        result = await recipe_service.add_to_list("fam1", "user1", "recipe1", "list1", "missing")

        assert result.addedCount == 1
        assert result.skippedCount == 1
        mock_shopping_service.add_item.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_to_list_requires_recipe(self, recipe_service: RecipeService, mock_recipe_repo: AsyncMock) -> None:
        mock_recipe_repo.get_recipe.return_value = None
        with pytest.raises(RecipeNotFoundError):
            await recipe_service.add_to_list("fam1", "user1", "missing", "list1", "all")
