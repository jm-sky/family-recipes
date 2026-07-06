"""Repository for the canonical ingredient dataset."""

import logging
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.ingredients.db_models import IngredientDB, IngredientUnitDB
from app.modules.ingredients.seed_data import IngredientSeed

logger = logging.getLogger(__name__)


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

    async def get_units_for(self, ingredient_id: str) -> list[IngredientUnitDB]:
        result = await self.db.execute(select(IngredientUnitDB).where(IngredientUnitDB.ingredient_id == ingredient_id))
        return list(result.scalars().all())

    async def search(self, query: str, limit: int = 20) -> list[IngredientDB]:
        pattern = f"%{query.lower()}%"
        stmt = select(IngredientDB).where(or_(func.lower(IngredientDB.name).like(pattern))).order_by(IngredientDB.name).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

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
