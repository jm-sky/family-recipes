"""Repository for shopping lists, categories and list items."""

import logging
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.shopping.db_models import CategoryDB, ShoppingListDB, ShoppingListItemDB

logger = logging.getLogger(__name__)


class ShoppingRepository:
    """Data access layer for the shopping module."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Categories ====================

    async def list_categories(self, family_id: str) -> list[CategoryDB]:
        stmt = select(CategoryDB).where(CategoryDB.family_id == family_id).order_by(CategoryDB.sort_order, CategoryDB.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_categories(self, family_id: str) -> int:
        result = await self.db.execute(select(func.count()).select_from(CategoryDB).where(CategoryDB.family_id == family_id))
        return int(result.scalar_one())

    async def get_category(self, category_id: str, family_id: str) -> CategoryDB | None:
        stmt = select(CategoryDB).where(CategoryDB.id == category_id, CategoryDB.family_id == family_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_category(self, *, family_id: str, name: str, icon: str | None, sort_order: int) -> CategoryDB:
        category = CategoryDB(id=generate_id(), family_id=family_id, name=name, icon=icon, sort_order=sort_order)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def bulk_create_categories(self, *, family_id: str, categories: list[tuple[str, str | None]]) -> None:
        for index, (name, icon) in enumerate(categories):
            self.db.add(CategoryDB(id=generate_id(), family_id=family_id, name=name, icon=icon, sort_order=index))
        await self.db.commit()

    async def save(self) -> None:
        await self.db.commit()

    async def delete_category(self, category: CategoryDB) -> None:
        # Detach the category from any items still referencing it, then delete it.
        await self.db.execute(update(ShoppingListItemDB).where(ShoppingListItemDB.category_id == category.id).values(category_id=None))
        await self.db.delete(category)
        await self.db.commit()

    # ==================== Shopping lists ====================

    async def list_lists(self, family_id: str) -> list[tuple[ShoppingListDB, int, int]]:
        checked_expr = func.coalesce(func.sum(case((ShoppingListItemDB.is_checked, 1), else_=0)), 0)
        total_expr = func.count(ShoppingListItemDB.id)
        stmt = (
            select(ShoppingListDB, total_expr, checked_expr)
            .outerjoin(
                ShoppingListItemDB,
                (ShoppingListItemDB.list_id == ShoppingListDB.id) & (ShoppingListItemDB.deleted_at.is_(None)),
            )
            .where(ShoppingListDB.family_id == family_id, ShoppingListDB.deleted_at.is_(None))
            .group_by(ShoppingListDB.id)
            .order_by(ShoppingListDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return [(row[0], int(row[1]), int(row[2])) for row in result.all()]

    async def get_list(self, list_id: str, family_id: str) -> ShoppingListDB | None:
        stmt = select(ShoppingListDB).where(
            ShoppingListDB.id == list_id,
            ShoppingListDB.family_id == family_id,
            ShoppingListDB.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_list(self, *, family_id: str, name: str, created_by: str) -> ShoppingListDB:
        shopping_list = ShoppingListDB(id=generate_id(), family_id=family_id, name=name, created_by=created_by)
        self.db.add(shopping_list)
        await self.db.commit()
        await self.db.refresh(shopping_list)
        return shopping_list

    async def soft_delete_list(self, shopping_list: ShoppingListDB) -> None:
        shopping_list.deleted_at = datetime.now(UTC)
        await self.db.commit()

    # ==================== Items ====================

    async def list_items(self, list_id: str) -> list[ShoppingListItemDB]:
        stmt = select(ShoppingListItemDB).where(ShoppingListItemDB.list_id == list_id, ShoppingListItemDB.deleted_at.is_(None)).order_by(ShoppingListItemDB.position, ShoppingListItemDB.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_items(self, list_id: str) -> tuple[int, int]:
        checked_expr = func.coalesce(func.sum(case((ShoppingListItemDB.is_checked, 1), else_=0)), 0)
        stmt = select(func.count(ShoppingListItemDB.id), checked_expr).where(
            ShoppingListItemDB.list_id == list_id,
            ShoppingListItemDB.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        row = result.one()
        return int(row[0]), int(row[1])

    async def get_item(self, item_id: str, list_id: str) -> ShoppingListItemDB | None:
        stmt = select(ShoppingListItemDB).where(
            ShoppingListItemDB.id == item_id,
            ShoppingListItemDB.list_id == list_id,
            ShoppingListItemDB.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_item_by_id(self, item_id: str) -> ShoppingListItemDB | None:
        stmt = select(ShoppingListItemDB).where(ShoppingListItemDB.id == item_id, ShoppingListItemDB.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def max_position(self, list_id: str) -> int:
        stmt = select(func.coalesce(func.max(ShoppingListItemDB.position), -1)).where(
            ShoppingListItemDB.list_id == list_id,
            ShoppingListItemDB.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def find_active_items_by_ingredient(self, list_id: str, ingredient_id: str) -> list[ShoppingListItemDB]:
        """Unchecked, non-deleted items of a given ingredient — merge candidates."""
        stmt = (
            select(ShoppingListItemDB)
            .where(
                ShoppingListItemDB.list_id == list_id,
                ShoppingListItemDB.deleted_at.is_(None),
                ShoppingListItemDB.is_checked.is_(False),
                ShoppingListItemDB.ingredient_id == ingredient_id,
            )
            .order_by(ShoppingListItemDB.position, ShoppingListItemDB.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_item(
        self,
        *,
        list_id: str,
        name: str,
        category_id: str | None,
        ingredient_id: str | None,
        quantity: Decimal | None,
        unit: str | None,
        position: int,
        created_by: str,
    ) -> ShoppingListItemDB:
        item = ShoppingListItemDB(
            id=generate_id(),
            list_id=list_id,
            name=name,
            category_id=category_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
            position=position,
            created_by=created_by,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def soft_delete_item(self, item: ShoppingListItemDB) -> None:
        item.deleted_at = datetime.now(UTC)
        await self.db.commit()

    async def touch_list(self, shopping_list: ShoppingListDB) -> None:
        shopping_list.updated_at = datetime.now(UTC)
        await self.db.commit()


def get_shopping_repository(db: AsyncSession = Depends(get_db)) -> ShoppingRepository:
    """FastAPI dependency to obtain a shopping repository."""
    return ShoppingRepository(db)
