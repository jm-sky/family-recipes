"""Business logic for the ingredients module (search + ingredient matching)."""

import logging
from decimal import Decimal

from app.modules.ingredients.conversion import IngredientMatch, build_match_terms, name_matches
from app.modules.ingredients.db_models import IngredientDB, IngredientUnitDB
from app.modules.ingredients.repository import IngredientRepository
from app.modules.ingredients.schemas import (
    IngredientResponse,
    IngredientsResponse,
    IngredientUnitResponse,
)

logger = logging.getLogger(__name__)


class IngredientService:
    """Service layer for ingredient search and matching."""

    def __init__(self, repository: IngredientRepository):
        self.repository = repository

    async def search(self, query: str | None) -> IngredientsResponse:
        ingredients = await self.repository.search(query) if query else await self.repository.list_all()
        units_by_ingredient = self._group_units(await self.repository.list_units())
        return IngredientsResponse(
            ingredients=[self._to_response(ingredient, units_by_ingredient.get(ingredient.id, [])) for ingredient in ingredients],
        )

    async def match(self, name: str) -> IngredientMatch | None:
        """Match a free-text item name to a known ingredient.

        Prefers a whole-name match, then a standalone-word match. Returns the
        conversion data needed to sum quantities, or None when unmatched.
        """
        ingredients = await self.repository.list_all()
        units_by_ingredient = self._group_units(await self.repository.list_units())

        exact: IngredientDB | None = None
        partial: IngredientDB | None = None
        for ingredient in ingredients:
            terms = build_match_terms(ingredient.name, ingredient.aliases)
            if name.strip().lower() in {t.lower() for t in terms} and exact is None:
                exact = ingredient
            elif name_matches(name, terms) and partial is None:
                partial = ingredient

        matched = exact or partial
        if matched is None:
            return None
        unit_to_base = {u.unit.lower(): u.amount_in_base for u in units_by_ingredient.get(matched.id, [])}
        return IngredientMatch(ingredient_id=matched.id, base_unit=matched.base_unit, unit_to_base=unit_to_base)

    def _group_units(self, units: list[IngredientUnitDB]) -> dict[str, list[IngredientUnitDB]]:
        grouped: dict[str, list[IngredientUnitDB]] = {}
        for unit in units:
            grouped.setdefault(unit.ingredient_id, []).append(unit)
        return grouped

    def _to_response(self, ingredient: IngredientDB, units: list[IngredientUnitDB]) -> IngredientResponse:
        return IngredientResponse(
            id=ingredient.id,
            name=ingredient.name,
            aliases=list(ingredient.aliases),
            baseUnit=ingredient.base_unit,
            units=[IngredientUnitResponse(unit=u.unit, amountInBase=float(Decimal(u.amount_in_base))) for u in units],
        )


def get_ingredient_service(repository: IngredientRepository) -> IngredientService:
    """Build an ingredient service (used by DI and cross-module callers)."""
    return IngredientService(repository=repository)
