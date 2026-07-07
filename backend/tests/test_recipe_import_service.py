"""Unit tests for AI recipe import."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.modules.ai.exceptions import RecipeImportError, StructuredOutputParsingError
from app.modules.ai.providers.base import ChatResponse
from app.modules.ai.services.recipe_import_service import RecipeImportService
from app.modules.ai.utils.page_fetcher import html_to_text
from app.modules.ai.utils.recipe_import_prompt import parse_recipe_import_json
from app.modules.ingredients.conversion import IngredientMatch


@pytest.fixture
def mock_settings_service() -> AsyncMock:
    service = AsyncMock()
    service.get_settings.return_value = AsyncMock(
        selected_model="openai/gpt-4o-mini",
        max_tokens=2000,
        temperature=0.2,
        use_own_token=False,
    )
    return service


@pytest.fixture
def mock_history_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_ingredient_service() -> AsyncMock:
    service = AsyncMock()
    service.match.return_value = None
    service.repository = AsyncMock()
    service.repository.get.return_value = None
    return service


@pytest.fixture
def recipe_import_service(
    mock_settings_service: AsyncMock,
    mock_history_repo: AsyncMock,
    mock_ingredient_service: AsyncMock,
) -> RecipeImportService:
    return RecipeImportService(
        settings_service=mock_settings_service,
        history_repo=mock_history_repo,
        ingredient_service=mock_ingredient_service,
        cache_service=None,
    )


class TestRecipeImportPrompt:
    def test_parse_json_codeblock(self) -> None:
        message = """Here is the recipe:
```json
{"title": "Naleśniki", "category": "breakfast", "servings": 4, "ingredients": [{"name": "mąka", "quantity": 2, "unit": "szklanka"}]}
```"""
        data = parse_recipe_import_json(message)
        assert data["title"] == "Naleśniki"
        assert len(data["ingredients"]) == 1

    def test_parse_raw_json(self) -> None:
        payload = {"title": "Zupa", "ingredients": [{"name": "marchew", "quantity": 2, "unit": "szt"}]}
        data = parse_recipe_import_json(json.dumps(payload))
        assert data["title"] == "Zupa"

    def test_parse_invalid_raises(self) -> None:
        with pytest.raises(StructuredOutputParsingError):
            parse_recipe_import_json("no json here")


class TestPageFetcher:
    def test_html_to_text_strips_tags(self) -> None:
        html = "<html><body><h1>Title</h1><p>2 <strong>jajka</strong></p></body></html>"
        text = html_to_text(html)
        assert "Title" in text
        assert "jajka" in text
        assert "<" not in text


class TestRecipeImportService:
    @pytest.mark.asyncio
    async def test_import_from_url_success(
        self,
        recipe_import_service: RecipeImportService,
        mock_ingredient_service: AsyncMock,
    ) -> None:
        mock_ingredient_service.match.return_value = IngredientMatch(
            ingredient_id="ing1",
            base_unit="g",
            unit_to_base={"szklanka": 130},
        )
        mock_ingredient_service.repository.get.return_value = SimpleNamespace(name="mąka pszenna")

        ai_payload = {
            "title": "Placki",
            "category": "breakfast",
            "servings": 2,
            "ingredients": [{"name": "mąka", "quantity": 1, "unit": "szklanka"}],
        }

        with (
            patch("app.modules.ai.services.recipe_import_service.settings") as mock_settings,
            patch("app.modules.ai.services.recipe_import_service.fetch_page_text", new_callable=AsyncMock) as mock_fetch,
            patch("app.modules.ai.services.recipe_import_service.OpenRouterProvider") as mock_provider_cls,
        ):
            mock_settings.ai.enabled = True
            mock_settings.ai.cache_enabled = False
            mock_fetch.return_value = ("https://example.com/placki", "Page with recipe text " * 20)

            provider = mock_provider_cls.return_value
            provider.chat = AsyncMock(
                return_value=ChatResponse(
                    message=json.dumps(ai_payload),
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    model="openai/gpt-4o-mini",
                ),
            )

            result = await recipe_import_service.import_from_url("user1", "https://example.com/placki")

        assert result.title == "Placki"
        assert result.sourceUrl == "https://example.com/placki"
        assert result.category == "breakfast"
        assert result.servings == 2
        assert result.ingredients[0].name == "mąka pszenna"
        assert result.ingredients[0].ingredientId == "ing1"
        assert result.ingredients[0].unit == "szklanka"

    @pytest.mark.asyncio
    async def test_import_disabled_raises(self, recipe_import_service: RecipeImportService) -> None:
        with patch("app.modules.ai.services.recipe_import_service.settings") as mock_settings:
            mock_settings.ai.enabled = False
            with pytest.raises(RecipeImportError, match="disabled"):
                await recipe_import_service.import_from_url("user1", "https://example.com/x")

    def test_normalize_unit_aliases(self, recipe_import_service: RecipeImportService) -> None:
        assert recipe_import_service._normalize_unit("łyżki") == "łyżka"
        assert recipe_import_service._normalize_unit("tbsp") == "łyżka"
        assert recipe_import_service._normalize_unit("unknown") == "unknown"

    def test_normalize_category_fallback(self, recipe_import_service: RecipeImportService) -> None:
        assert recipe_import_service._normalize_category("dessert") == "dessert"
        assert recipe_import_service._normalize_category("invalid") == "dinner"
