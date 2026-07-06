"""Repository for recipes, ingredients and tags."""

import logging
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.recipes.db_models import RecipeDB, RecipeIngredientDB, RecipeTagLinkDB, TagDB

logger = logging.getLogger(__name__)


class RecipeRepository:
    """Data access layer for recipes and tags."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Tags ====================

    async def list_tags(self, family_id: str) -> list[TagDB]:
        result = await self.db.execute(select(TagDB).where(TagDB.family_id == family_id).order_by(TagDB.name))
        return list(result.scalars().all())

    async def get_tag(self, tag_id: str, family_id: str) -> TagDB | None:
        result = await self.db.execute(select(TagDB).where(TagDB.id == tag_id, TagDB.family_id == family_id))
        return result.scalar_one_or_none()

    async def get_tag_by_name(self, family_id: str, name: str) -> TagDB | None:
        result = await self.db.execute(select(TagDB).where(TagDB.family_id == family_id, func.lower(TagDB.name) == name.lower()))
        return result.scalar_one_or_none()

    async def create_tag(self, *, family_id: str, name: str) -> TagDB:
        tag = TagDB(id=generate_id(), family_id=family_id, name=name.strip())
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    # ==================== Recipes ====================

    async def list_recipes(self, family_id: str, *, category: str | None, tag_id: str | None, query: str | None) -> list[RecipeDB]:
        stmt = select(RecipeDB).where(RecipeDB.family_id == family_id, RecipeDB.deleted_at.is_(None))
        if category:
            stmt = stmt.where(RecipeDB.category == category)
        if query:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(func.lower(RecipeDB.title).like(pattern))
        if tag_id:
            stmt = stmt.join(RecipeTagLinkDB, RecipeTagLinkDB.recipe_id == RecipeDB.id).where(RecipeTagLinkDB.tag_id == tag_id)
        stmt = stmt.order_by(RecipeDB.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recipe(self, recipe_id: str, family_id: str) -> RecipeDB | None:
        result = await self.db.execute(
            select(RecipeDB).where(
                RecipeDB.id == recipe_id,
                RecipeDB.family_id == family_id,
                RecipeDB.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_ingredients(self, recipe_id: str) -> list[RecipeIngredientDB]:
        result = await self.db.execute(select(RecipeIngredientDB).where(RecipeIngredientDB.recipe_id == recipe_id).order_by(RecipeIngredientDB.sort_order, RecipeIngredientDB.name))
        return list(result.scalars().all())

    async def list_tag_ids_for_recipe(self, recipe_id: str) -> list[str]:
        result = await self.db.execute(select(RecipeTagLinkDB.tag_id).where(RecipeTagLinkDB.recipe_id == recipe_id))
        return [row[0] for row in result.all()]

    async def list_tag_ids_for_recipes(self, recipe_ids: list[str]) -> dict[str, list[str]]:
        if not recipe_ids:
            return {}
        result = await self.db.execute(select(RecipeTagLinkDB).where(RecipeTagLinkDB.recipe_id.in_(recipe_ids)))
        grouped: dict[str, list[str]] = {}
        for link in result.scalars().all():
            grouped.setdefault(link.recipe_id, []).append(link.tag_id)
        return grouped

    async def create_recipe(
        self,
        *,
        family_id: str,
        title: str,
        source_url: str | None,
        category: str,
        servings: int | None,
        created_by: str,
        ingredients: list[tuple[str, str | None, Decimal | None, str | None, int]],
        tag_ids: list[str],
    ) -> RecipeDB:
        recipe = RecipeDB(
            id=generate_id(),
            family_id=family_id,
            title=title,
            source_url=source_url,
            category=category,
            servings=servings,
            created_by=created_by,
        )
        self.db.add(recipe)
        for name, ingredient_id, quantity, unit, sort_order in ingredients:
            self.db.add(
                RecipeIngredientDB(
                    id=generate_id(),
                    recipe_id=recipe.id,
                    name=name,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    unit=unit,
                    sort_order=sort_order,
                )
            )
        for tag_id in tag_ids:
            self.db.add(RecipeTagLinkDB(recipe_id=recipe.id, tag_id=tag_id))
        await self.db.commit()
        await self.db.refresh(recipe)
        return recipe

    async def update_recipe(self, recipe: RecipeDB) -> RecipeDB:
        recipe.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(recipe)
        return recipe

    async def replace_ingredients(self, recipe_id: str, ingredients: list[tuple[str, str | None, Decimal | None, str | None, int]]) -> None:
        await self.db.execute(delete(RecipeIngredientDB).where(RecipeIngredientDB.recipe_id == recipe_id))
        for name, ingredient_id, quantity, unit, sort_order in ingredients:
            self.db.add(
                RecipeIngredientDB(
                    id=generate_id(),
                    recipe_id=recipe_id,
                    name=name,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    unit=unit,
                    sort_order=sort_order,
                )
            )
        await self.db.commit()

    async def replace_tags(self, recipe_id: str, tag_ids: list[str]) -> None:
        await self.db.execute(delete(RecipeTagLinkDB).where(RecipeTagLinkDB.recipe_id == recipe_id))
        for tag_id in tag_ids:
            self.db.add(RecipeTagLinkDB(recipe_id=recipe_id, tag_id=tag_id))
        await self.db.commit()

    async def set_image_path(self, recipe: RecipeDB, image_path: str | None) -> RecipeDB:
        recipe.image_path = image_path
        recipe.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(recipe)
        return recipe

    async def soft_delete_recipe(self, recipe: RecipeDB) -> None:
        recipe.deleted_at = datetime.now(UTC)
        await self.db.commit()

    async def validate_tag_ids(self, family_id: str, tag_ids: list[str]) -> bool:
        if not tag_ids:
            return True
        result = await self.db.execute(select(func.count()).select_from(TagDB).where(TagDB.family_id == family_id, TagDB.id.in_(tag_ids)))
        return int(result.scalar_one()) == len(set(tag_ids))


def get_recipe_repository(db: AsyncSession = Depends(get_db)) -> RecipeRepository:
    """FastAPI dependency to obtain a recipe repository."""
    return RecipeRepository(db)
