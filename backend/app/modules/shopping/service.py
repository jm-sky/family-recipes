"""Business logic for the shopping module (lists, categories, items).

Phase 2 scope: full CRUD for lists, editable categories, items, checking,
quick-add from free text and reordering. Ingredient matching and unit
summation are layered on top in the ingredients phase.
"""

import logging
import re
from decimal import Decimal, InvalidOperation

from app.modules.shopping.constants import DEFAULT_CATEGORIES, UNITS_SET
from app.modules.shopping.db_models import CategoryDB, ShoppingListDB, ShoppingListItemDB
from app.modules.shopping.exceptions import (
    CategoryNotFoundError,
    InvalidUnitError,
    ShoppingItemNotFoundError,
    ShoppingListNotFoundError,
)
from app.modules.shopping.repository import ShoppingRepository
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

logger = logging.getLogger(__name__)

_QUICK_ADD_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)?\s*([^\d\s]+)?\s*(.*)$")


def parse_quick_add(text: str) -> tuple[str, Decimal | None, str | None]:
    """Parse a free-text quick-add entry into (name, quantity, unit).

    Examples:
        "2 kg mąki"    -> ("mąki", Decimal("2"), "kg")
        "0,5 l mleka"  -> ("mleka", Decimal("0.5"), "l")
        "3 jabłka"     -> ("jabłka", Decimal("3"), None)
        "masło"        -> ("masło", None, None)

    A leading number is read as the quantity. The token right after it is
    treated as a unit only when it belongs to the predefined unit list;
    otherwise it is part of the name. Unknown input degrades to name-only.
    """
    stripped = text.strip()
    match = _QUICK_ADD_RE.match(stripped)
    if not match:
        return stripped, None, None

    raw_qty, maybe_unit, rest = match.group(1), match.group(2), match.group(3)

    quantity: Decimal | None = None
    if raw_qty:
        try:
            quantity = Decimal(raw_qty.replace(",", "."))
        except InvalidOperation:
            quantity = None

    unit: str | None = None
    name_parts: list[str] = []
    if maybe_unit and maybe_unit.lower() in UNITS_SET:
        unit = maybe_unit.lower()
    elif maybe_unit:
        name_parts.append(maybe_unit)

    if rest:
        name_parts.append(rest)
    name = " ".join(part.strip() for part in name_parts if part.strip()).strip()

    # No quantity was detected and the first token was not a unit: the whole
    # string is the name.
    if quantity is None and unit is None:
        name = stripped

    if not name:
        name = stripped
    return name, quantity, unit


class ShoppingService:
    """Service layer for shopping lists, categories and items."""

    def __init__(self, repository: ShoppingRepository):
        self.repository = repository

    # ==================== Categories ====================

    async def list_categories(self, family_id: str) -> CategoriesResponse:
        categories = await self.repository.list_categories(family_id)
        return CategoriesResponse(categories=[self._to_category_response(c) for c in categories])

    async def create_category(self, family_id: str, payload: CategoryCreateRequest) -> CategoryResponse:
        sort_order = payload.sortOrder if payload.sortOrder is not None else await self.repository.count_categories(family_id)
        category = await self.repository.create_category(family_id=family_id, name=payload.name, icon=payload.icon, sort_order=sort_order)
        return self._to_category_response(category)

    async def update_category(self, family_id: str, category_id: str, payload: CategoryUpdateRequest) -> CategoryResponse:
        category = await self.repository.get_category(category_id, family_id)
        if category is None:
            raise CategoryNotFoundError("Category not found")
        if payload.name is not None:
            category.name = payload.name
        if payload.icon is not None:
            category.icon = payload.icon
        if payload.sortOrder is not None:
            category.sort_order = payload.sortOrder
        await self.repository.save()
        return self._to_category_response(category)

    async def delete_category(self, family_id: str, category_id: str) -> None:
        category = await self.repository.get_category(category_id, family_id)
        if category is None:
            raise CategoryNotFoundError("Category not found")
        await self.repository.delete_category(category)

    # ==================== Shopping lists ====================

    async def list_lists(self, family_id: str) -> ShoppingListsResponse:
        rows = await self.repository.list_lists(family_id)
        return ShoppingListsResponse(lists=[self._to_list_response(lst, total, checked) for lst, total, checked in rows])

    async def create_list(self, family_id: str, user_id: str, payload: ShoppingListCreateRequest) -> ShoppingListResponse:
        # Seed default categories the first time a family creates a list.
        if await self.repository.count_categories(family_id) == 0:
            await self.repository.bulk_create_categories(family_id=family_id, categories=[(name, icon) for name, icon in DEFAULT_CATEGORIES])
        shopping_list = await self.repository.create_list(family_id=family_id, name=payload.name, created_by=user_id)
        return self._to_list_response(shopping_list, 0, 0)

    async def get_list_detail(self, family_id: str, list_id: str) -> ShoppingListDetailResponse:
        shopping_list = await self._require_list(family_id, list_id)
        items = await self.repository.list_items(list_id)
        checked = sum(1 for i in items if i.is_checked)
        return ShoppingListDetailResponse(
            id=shopping_list.id,
            name=shopping_list.name,
            itemCount=len(items),
            checkedCount=checked,
            createdAt=shopping_list.created_at,
            updatedAt=shopping_list.updated_at,
            items=[self._to_item_response(i) for i in items],
        )

    async def update_list(self, family_id: str, list_id: str, payload: ShoppingListUpdateRequest) -> ShoppingListResponse:
        shopping_list = await self._require_list(family_id, list_id)
        shopping_list.name = payload.name
        await self.repository.save()
        total, checked = await self.repository.count_items(list_id)
        return self._to_list_response(shopping_list, total, checked)

    async def delete_list(self, family_id: str, list_id: str) -> None:
        shopping_list = await self._require_list(family_id, list_id)
        await self.repository.soft_delete_list(shopping_list)

    # ==================== Items ====================

    async def add_item(self, family_id: str, list_id: str, user_id: str, payload: ShoppingItemCreateRequest) -> ShoppingItemResponse:
        shopping_list = await self._require_list(family_id, list_id)
        unit = self._validate_unit(payload.unit)
        category_id = await self._validate_category(family_id, payload.categoryId)
        quantity = Decimal(str(payload.quantity)) if payload.quantity is not None else None
        item = await self._insert_item(shopping_list, name=payload.name.strip(), category_id=category_id, quantity=quantity, unit=unit, user_id=user_id)
        return self._to_item_response(item)

    async def quick_add(self, family_id: str, list_id: str, user_id: str, payload: QuickAddRequest) -> ShoppingItemResponse:
        shopping_list = await self._require_list(family_id, list_id)
        name, quantity, unit = parse_quick_add(payload.text)
        item = await self._insert_item(shopping_list, name=name, category_id=None, quantity=quantity, unit=unit, user_id=user_id)
        return self._to_item_response(item)

    async def update_item(self, family_id: str, list_id: str, item_id: str, payload: ShoppingItemUpdateRequest) -> ShoppingItemResponse:
        await self._require_list(family_id, list_id)
        item = await self.repository.get_item(item_id, list_id)
        if item is None:
            raise ShoppingItemNotFoundError("Item not found")
        if payload.name is not None:
            item.name = payload.name.strip()
        if payload.categoryId is not None:
            item.category_id = await self._validate_category(family_id, payload.categoryId)
        if payload.quantity is not None:
            item.quantity = Decimal(str(payload.quantity))
        if payload.unit is not None:
            item.unit = self._validate_unit(payload.unit)
        if payload.isChecked is not None:
            item.is_checked = payload.isChecked
        if payload.position is not None:
            item.position = payload.position
        await self.repository.save()
        return self._to_item_response(item)

    async def delete_item(self, family_id: str, list_id: str, item_id: str) -> None:
        await self._require_list(family_id, list_id)
        item = await self.repository.get_item(item_id, list_id)
        if item is None:
            raise ShoppingItemNotFoundError("Item not found")
        await self.repository.soft_delete_item(item)

    async def reorder(self, family_id: str, list_id: str, payload: ReorderRequest) -> None:
        await self._require_list(family_id, list_id)
        by_id = {entry.id: entry.position for entry in payload.items}
        items = await self.repository.list_items(list_id)
        for item in items:
            if item.id in by_id:
                item.position = by_id[item.id]
        await self.repository.save()

    # ==================== Helpers ====================

    async def _insert_item(
        self,
        shopping_list: ShoppingListDB,
        *,
        name: str,
        category_id: str | None,
        quantity: Decimal | None,
        unit: str | None,
        user_id: str,
    ) -> ShoppingListItemDB:
        position = await self.repository.max_position(shopping_list.id) + 1
        item = await self.repository.create_item(
            list_id=shopping_list.id,
            name=name,
            category_id=category_id,
            ingredient_id=None,
            quantity=quantity,
            unit=unit,
            position=position,
            created_by=user_id,
        )
        await self.repository.touch_list(shopping_list)
        return item

    async def _require_list(self, family_id: str, list_id: str) -> ShoppingListDB:
        shopping_list = await self.repository.get_list(list_id, family_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError("Shopping list not found")
        return shopping_list

    def _validate_unit(self, unit: str | None) -> str | None:
        if unit is None or unit == "":
            return None
        normalized = unit.strip().lower()
        if normalized not in UNITS_SET:
            raise InvalidUnitError(f"Unknown unit '{unit}'")
        return normalized

    async def _validate_category(self, family_id: str, category_id: str | None) -> str | None:
        if category_id is None or category_id == "":
            return None
        category = await self.repository.get_category(category_id, family_id)
        if category is None:
            raise CategoryNotFoundError("Category not found")
        return category.id

    def _to_category_response(self, category: CategoryDB) -> CategoryResponse:
        return CategoryResponse(id=category.id, name=category.name, icon=category.icon, sortOrder=category.sort_order)

    def _to_list_response(self, shopping_list: ShoppingListDB, total: int, checked: int) -> ShoppingListResponse:
        return ShoppingListResponse(
            id=shopping_list.id,
            name=shopping_list.name,
            itemCount=total,
            checkedCount=checked,
            createdAt=shopping_list.created_at,
            updatedAt=shopping_list.updated_at,
        )

    def _to_item_response(self, item: ShoppingListItemDB) -> ShoppingItemResponse:
        return ShoppingItemResponse(
            id=item.id,
            listId=item.list_id,
            name=item.name,
            categoryId=item.category_id,
            ingredientId=item.ingredient_id,
            quantity=float(item.quantity) if item.quantity is not None else None,
            unit=item.unit,
            isChecked=item.is_checked,
            position=item.position,
            createdAt=item.created_at,
            updatedAt=item.updated_at,
        )
