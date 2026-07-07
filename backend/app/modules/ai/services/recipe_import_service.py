"""Business logic for AI-assisted recipe import from URLs."""

from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.config import settings
from app.modules.ai.cache.postgres_cache import PostgresCacheService
from app.modules.ai.exceptions import RecipeImportError, StructuredOutputParsingError
from app.modules.ai.providers.openrouter import OpenRouterProvider
from app.modules.ai.repositories import HistoryRepository
from app.modules.ai.schemas import RecipeImportIngredient, RecipeImportResponse
from app.modules.ai.services.settings_service import SettingsService
from app.modules.ai.utils.models_config import calculate_cost
from app.modules.ai.utils.page_fetcher import fetch_page_text
from app.modules.ai.utils.recipe_import_prompt import build_recipe_import_prompt, parse_recipe_import_json
from app.modules.ingredients.service import IngredientService
from app.modules.recipes.constants import RECIPE_CATEGORIES
from app.modules.shopping.constants import UNITS_SET

logger = logging.getLogger(__name__)

_UNIT_ALIASES: dict[str, str] = {
    "szt.": "szt",
    "sztuk": "szt",
    "sztuki": "szt",
    "gram": "g",
    "gramów": "g",
    "gramy": "g",
    "kilogram": "kg",
    "kilogramów": "kg",
    "kilogramy": "kg",
    "litr": "l",
    "litra": "l",
    "litry": "l",
    "łyżki": "łyżka",
    "lyzka": "łyżka",
    "łyżeczki": "łyżeczka",
    "lyzeczka": "łyżeczka",
    "szklanki": "szklanka",
    "tbsp": "łyżka",
    "tsp": "łyżeczka",
    "cup": "szklanka",
    "cups": "szklanka",
}


class RecipeImportService:
    """Import recipe drafts from external URLs using OpenRouter."""

    def __init__(
        self,
        settings_service: SettingsService,
        history_repo: HistoryRepository,
        ingredient_service: IngredientService,
        cache_service: PostgresCacheService | None = None,
    ):
        self.settings_service = settings_service
        self.history_repo = history_repo
        self.ingredient_service = ingredient_service
        self.cache_service = cache_service

    async def import_from_url(self, user_id: str, url: str) -> RecipeImportResponse:
        """Fetch a recipe page and return a normalized draft for user confirmation."""
        if not settings.ai.enabled:
            raise RecipeImportError("AI features are disabled")

        user_settings = await self.settings_service.get_settings(user_id)
        model = user_settings.selected_model
        max_tokens = user_settings.max_tokens or 2000
        temperature = 0.2

        api_token = None
        if user_settings.use_own_token:
            api_token = await self.settings_service.get_api_token(user_id)

        final_url, page_text = await fetch_page_text(url)

        if settings.ai.cache_enabled and self.cache_service:
            cache_key = PostgresCacheService.generate_cache_key(
                operation_type="recipe_import",
                input_data={"url": final_url},
                model=model,
            )
            cached = await self.cache_service.get(cache_key)
            if cached:
                return RecipeImportResponse(**cached)

        messages = build_recipe_import_prompt(page_text, final_url)
        provider = OpenRouterProvider(api_key=api_token)
        response = await provider.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        try:
            parsed = parse_recipe_import_json(response.message)
        except StructuredOutputParsingError:
            logger.warning("Recipe import JSON parse failed for %s", final_url)
            raise

        draft = await self._build_response(parsed, final_url)

        cost = calculate_cost(model, response.prompt_tokens, response.completion_tokens)
        provider_name = model.split("/")[0] if "/" in model else "unknown"
        await self.history_repo.create(
            user_id=user_id,
            operation_type="recipe_import",
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            cost_usd=cost,
            input_data={"url": final_url},
            output_data=draft.model_dump(by_alias=True),
            metadata={
                "provider": provider_name,
                "used_own_token": user_settings.use_own_token,
            },
        )

        if settings.ai.cache_enabled and self.cache_service:
            await self.cache_service.set(
                cache_key,
                draft.model_dump(by_alias=True),
                ttl_days=settings.ai.cache_ttl_classify,
            )

        return draft

    async def _build_response(self, parsed: dict[str, Any], source_url: str) -> RecipeImportResponse:
        title = str(parsed.get("title", "")).strip()
        if not title:
            raise StructuredOutputParsingError("Recipe title missing in AI response")

        category = self._normalize_category(parsed.get("category"))
        servings = self._normalize_servings(parsed.get("servings"))
        raw_ingredients = parsed.get("ingredients") or []
        if not isinstance(raw_ingredients, list) or not raw_ingredients:
            raise StructuredOutputParsingError("Recipe ingredients missing in AI response")

        ingredients: list[RecipeImportIngredient] = []
        for item in raw_ingredients:
            if not isinstance(item, dict):
                continue
            normalized = await self._normalize_ingredient(item)
            if normalized.name.strip():
                ingredients.append(normalized)

        if not ingredients:
            raise StructuredOutputParsingError("No valid ingredients found in AI response")

        return RecipeImportResponse(
            title=title,
            sourceUrl=source_url,
            category=category,
            servings=servings,
            ingredients=ingredients,
        )

    def _normalize_category(self, value: Any) -> str:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in RECIPE_CATEGORIES:
                return lowered
        return "dinner"

    def _normalize_servings(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            servings = int(Decimal(str(value)))
        except (InvalidOperation, ValueError, TypeError):
            return None
        return servings if servings >= 1 else None

    async def _normalize_ingredient(self, item: dict[str, Any]) -> RecipeImportIngredient:
        name = str(item.get("name", "")).strip()
        quantity = self._normalize_quantity(item.get("quantity"))
        unit = self._normalize_unit(item.get("unit"))

        ingredient_id: str | None = None
        match = await self.ingredient_service.match(name)
        if match is not None:
            ingredient_id = match.ingredient_id
            ingredient = await self.ingredient_service.repository.get(match.ingredient_id)
            if ingredient is not None:
                name = ingredient.name

        return RecipeImportIngredient(
            name=name,
            ingredientId=ingredient_id,
            quantity=quantity,
            unit=unit,
        )

    def _normalize_quantity(self, value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            qty = Decimal(str(value).replace(",", "."))
        except (InvalidOperation, ValueError, TypeError):
            return None
        if qty < 0:
            return None
        return float(qty)

    def _normalize_unit(self, value: Any) -> str | None:
        if value is None:
            return None
        raw = str(value).strip()
        if not raw:
            return None
        lowered = raw.lower()
        lowered = _UNIT_ALIASES.get(lowered, lowered)
        lowered = re.sub(r"\.$", "", lowered)
        if lowered in UNITS_SET:
            return lowered
        return raw
