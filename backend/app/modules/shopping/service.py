"""Business logic for the shopping module (lists, categories, items).

Phase 2 scope: full CRUD for lists, editable categories, items, checking,
quick-add from free text and reordering. Ingredient matching and unit
summation are layered on top in the ingredients phase.
"""

import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Protocol

from app.modules.ingredients.conversion import IngredientMatch, _fold
from app.modules.shopping.constants import DEFAULT_CATEGORIES, POPULAR_INGREDIENT_NAMES, UNITS_SET
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
    ProductSuggestionResponse,
    ProductSuggestionsResponse,
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

    # A bare unit with no leading number means one of it ("szklanka mąki" = 1 cup).
    if unit is not None and quantity is None:
        quantity = Decimal("1")

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


class IngredientMatcher(Protocol):
    """Minimal interface the shopping service needs from the ingredients module."""

    async def match(self, name: str) -> IngredientMatch | None: ...

    async def search(self, query: str | None): ...


class ShoppingService:
    """Service layer for shopping lists, categories and items."""

    def __init__(self, repository: ShoppingRepository, matcher: IngredientMatcher | None = None):
        self.repository = repository
        self.matcher = matcher

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
        item = await self._add_or_merge(shopping_list, name=payload.name.strip(), category_id=category_id, quantity=quantity, unit=unit, user_id=user_id)
        return self._to_item_response(item)

    async def quick_add(self, family_id: str, list_id: str, user_id: str, payload: QuickAddRequest) -> ShoppingItemResponse:
        shopping_list = await self._require_list(family_id, list_id)
        name, quantity, unit = parse_quick_add(payload.text)
        item = await self._add_or_merge(shopping_list, name=name, category_id=None, quantity=quantity, unit=unit, user_id=user_id)
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

    async def get_suggestions(self, family_id: str, query: str | None = None, limit: int = 15) -> ProductSuggestionsResponse:
        """Unified product suggestions for the add-item UI."""
        suggestions: list[ProductSuggestionResponse] = []
        seen: set[str] = set()

        def add_suggestion(*, name: str, ingredient_id: str | None, category_icon: str | None, source: str) -> None:
            key = _fold(name)
            if not key or key in seen:
                return
            seen.add(key)
            suggestions.append(
                ProductSuggestionResponse(
                    name=name,
                    ingredientId=ingredient_id,
                    categoryId=None,
                    categoryIcon=category_icon,
                    source=source,
                )
            )

        if self.matcher is not None and query:
            response = await self.matcher.search(query)
            for ingredient in response.ingredients:
                add_suggestion(
                    name=ingredient.name,
                    ingredient_id=ingredient.id,
                    category_icon=ingredient.shoppingCategoryKey,
                    source="ingredient",
                )
        else:
            for recent_name in await self.repository.list_recent_item_names(family_id, limit=10):
                match = await self.matcher.match(recent_name) if self.matcher is not None else None
                add_suggestion(
                    name=recent_name,
                    ingredient_id=match.ingredient_id if match is not None else None,
                    category_icon=match.shopping_category_key if match is not None else None,
                    source="recent",
                )

            if self.matcher is not None:
                popular_response = await self.matcher.search(None)
                popular_by_name = {item.name: item for item in popular_response.ingredients}
                for popular_name in POPULAR_INGREDIENT_NAMES:
                    ingredient_response = popular_by_name.get(popular_name)
                    if ingredient_response is not None:
                        add_suggestion(
                            name=ingredient_response.name,
                            ingredient_id=ingredient_response.id,
                            category_icon=ingredient_response.shoppingCategoryKey,
                            source="popular",
                        )
                    else:
                        add_suggestion(name=popular_name, ingredient_id=None, category_icon=None, source="popular")

        resolved: list[ProductSuggestionResponse] = []
        for suggestion in suggestions[:limit]:
            category_id = suggestion.categoryId
            if category_id is None and suggestion.categoryIcon:
                category = await self.repository.get_category_by_icon(family_id, suggestion.categoryIcon)
                if category is not None:
                    category_id = category.id
            resolved.append(suggestion.model_copy(update={"categoryId": category_id}))

        return ProductSuggestionsResponse(suggestions=resolved)

    # ==================== Helpers ====================

    async def _add_or_merge(
        self,
        shopping_list: ShoppingListDB,
        *,
        name: str,
        category_id: str | None,
        quantity: Decimal | None,
        unit: str | None,
        user_id: str,
    ) -> ShoppingListItemDB:
        """Insert an item, merging into an existing one when possible.

        If the name matches a known ingredient and both the new and an existing
        active item convert to the ingredient's base unit, their quantities are
        summed and stored in the base unit (README section 2). When a unit has
        no conversion mapping, the item is kept separate.
        """
        match = await self.matcher.match(name) if self.matcher is not None else None
        resolved_category_id = category_id
        if resolved_category_id is None and match is not None and match.shopping_category_key:
            resolved_category_id = await self._category_id_for_icon(shopping_list.family_id, match.shopping_category_key)

        if match is not None:
            merged = await self._try_merge(shopping_list, match, quantity, unit)
            if merged is not None:
                return merged

        position = await self.repository.max_position(shopping_list.id) + 1
        item = await self.repository.create_item(
            list_id=shopping_list.id,
            name=name,
            category_id=resolved_category_id,
            ingredient_id=match.ingredient_id if match is not None else None,
            quantity=quantity,
            unit=unit,
            position=position,
            created_by=user_id,
        )
        await self.repository.touch_list(shopping_list)
        return item

    async def _try_merge(
        self,
        shopping_list: ShoppingListDB,
        match: IngredientMatch,
        quantity: Decimal | None,
        unit: str | None,
    ) -> ShoppingListItemDB | None:
        added_base = match.to_base(quantity, unit)
        if added_base is None:
            return None  # cannot convert the new quantity -> keep separate
        existing_items = await self.repository.find_active_items_by_ingredient(shopping_list.id, match.ingredient_id)
        for existing in existing_items:
            existing_base = match.to_base(existing.quantity, existing.unit)
            if existing_base is None:
                continue  # existing has an unmappable unit -> don't merge into it
            existing.quantity = existing_base + added_base
            existing.unit = match.base_unit
            await self.repository.save()
            await self.repository.touch_list(shopping_list)
            return existing
        return None

    async def _category_id_for_icon(self, family_id: str, icon: str) -> str | None:
        category = await self.repository.get_category_by_icon(family_id, icon)
        return category.id if category is not None else None

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
