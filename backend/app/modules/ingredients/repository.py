"""Repository for the canonical ingredient dataset."""

import logging
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.ingredients.conversion import _fold
from app.modules.ingredients.db_models import IngredientDB, IngredientUnitDB
from app.modules.ingredients.seed_data import IngredientSeed

logger = logging.getLogger(__name__)


def _search_score(query: str, ingredient: IngredientDB) -> int:
    """Rank how well an ingredient matches a query (higher is better)."""
    folded_query = _fold(query)
    if not folded_query:
        return 0

    folded_name = _fold(ingredient.name)
    if folded_name == folded_query:
        return 100
    if folded_name.startswith(folded_query):
        return 80
    if folded_query in folded_name:
        return 60

    best_alias = 0
    for alias in ingredient.aliases:
        folded_alias = _fold(alias)
        if not folded_alias:
            continue
        if folded_alias == folded_query:
            best_alias = max(best_alias, 90)
        elif folded_alias.startswith(folded_query):
            best_alias = max(best_alias, 70)
        elif folded_query in folded_alias:
            best_alias = max(best_alias, 50)
    return best_alias


class IngredientRepository:
    """Data access layer for ingredients and their unit conversions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(IngredientDB))
        return int(result.scalar_one())

    async def list_all(self) -> list[IngredientDB]:
        result = await self.db.execute(select(IngredientDB).order_by(IngredientDB.name))
        return list(result.scalars().all())

    async def list_units(self) -> list[IngredientUnitDB]:
        result = await self.db.execute(select(IngredientUnitDB))
        return list(result.scalars().all())

    async def get(self, ingredient_id: str) -> IngredientDB | None:
        result = await self.db.execute(select(IngredientDB).where(IngredientDB.id == ingredient_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> IngredientDB | None:
        result = await self.db.execute(select(IngredientDB).where(IngredientDB.name == name))
        return result.scalar_one_or_none()

    async def get_units_for(self, ingredient_id: str) -> list[IngredientUnitDB]:
        result = await self.db.execute(select(IngredientUnitDB).where(IngredientUnitDB.ingredient_id == ingredient_id))
        return list(result.scalars().all())

    async def search(self, query: str, limit: int = 20) -> list[IngredientDB]:
        """Search by canonical name and aliases with relevance ranking."""
        normalized = query.strip()
        if not normalized:
            return (await self.list_all())[:limit]

        scored = [(score, ingredient) for ingredient in await self.list_all() if (score := _search_score(normalized, ingredient)) > 0]
        scored.sort(key=lambda entry: (-entry[0], entry[1].name))
        return [ingredient for _, ingredient in scored[:limit]]

    async def bulk_create(self, seeds: list[IngredientSeed]) -> int:
        created = 0
        for seed in seeds:
            ingredient_id = generate_id()
            self.db.add(
                IngredientDB(
                    id=ingredient_id,
                    name=seed["name"],
                    aliases=list(seed["aliases"]),
                    base_unit=seed["base_unit"],
                    shopping_category_key=seed["shopping_category_key"],
                )
            )
            for unit, amount in seed["units"].items():
                self.db.add(
                    IngredientUnitDB(
                        id=generate_id(),
                        ingredient_id=ingredient_id,
                        unit=unit,
                        amount_in_base=Decimal(str(amount)),
                    )
                )
            created += 1
        await self.db.commit()
        return created


def get_ingredient_repository(db: AsyncSession = Depends(get_db)) -> IngredientRepository:
    """FastAPI dependency to obtain an ingredient repository."""
    return IngredientRepository(db)
