"""Unit tests for the shopping service (quick-add parsing, validation, CRUD)."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.modules.shopping.db_models import CategoryDB, ShoppingListDB, ShoppingListItemDB
from app.modules.shopping.exceptions import (
    CategoryNotFoundError,
    InvalidUnitError,
    ShoppingItemNotFoundError,
    ShoppingListNotFoundError,
)
from app.modules.shopping.repository import ShoppingRepository
from app.modules.shopping.schemas import (
    QuickAddRequest,
    ReorderEntry,
    ReorderRequest,
    ShoppingItemCreateRequest,
    ShoppingItemUpdateRequest,
    ShoppingListCreateRequest,
)
from app.modules.shopping.service import ShoppingService, parse_quick_add


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=ShoppingRepository)


@pytest.fixture
def service(mock_repository: AsyncMock) -> ShoppingService:
    return ShoppingService(repository=mock_repository)


def make_list(list_id: str = "list1", family_id: str = "fam1") -> ShoppingListDB:
    now = datetime.now(UTC)
    return ShoppingListDB(id=list_id, family_id=family_id, name="Dom", created_by="user1", created_at=now, updated_at=now)


def make_item(item_id: str = "item1", **overrides: object) -> ShoppingListItemDB:
    now = datetime.now(UTC)
    defaults: dict = {
        "id": item_id,
        "list_id": "list1",
        "name": "mleko",
        "category_id": None,
        "ingredient_id": None,
        "quantity": None,
        "unit": None,
        "is_checked": False,
        "source_recipe_id": None,
        "position": 0,
        "created_by": "user1",
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    }
    defaults.update(overrides)
    return ShoppingListItemDB(**defaults)


class TestParseQuickAdd:
    """Free-text quick-add parsing."""

    @pytest.mark.parametrize(
        ("text", "name", "quantity", "unit"),
        [
            ("2 kg mąki", "mąki", Decimal("2"), "kg"),
            ("0,5 l mleka", "mleka", Decimal("0.5"), "l"),
            ("1.5 kg cukru", "cukru", Decimal("1.5"), "kg"),
            ("3 jabłka", "jabłka", Decimal("3"), None),
            ("masło", "masło", None, None),
            ("szklanka mąki", "mąki", None, "szklanka"),
            ("  chleb razowy ", "chleb razowy", None, None),
        ],
    )
    def test_parse(self, text: str, name: str, quantity: Decimal | None, unit: str | None) -> None:
        parsed_name, parsed_qty, parsed_unit = parse_quick_add(text)
        assert parsed_name == name
        assert parsed_qty == quantity
        assert parsed_unit == unit


class TestAddItem:
    @pytest.mark.asyncio
    async def test_add_item_appends_at_next_position(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()
        mock_repository.max_position.return_value = 4
        mock_repository.create_item.return_value = make_item(position=5, name="mleko")

        payload = ShoppingItemCreateRequest(name="mleko", quantity=2, unit="l")
        response = await service.add_item("fam1", "list1", "user1", payload)

        assert response.position == 5
        _, kwargs = mock_repository.create_item.call_args
        assert kwargs["position"] == 5
        assert kwargs["unit"] == "l"
        assert kwargs["quantity"] == Decimal("2")

    @pytest.mark.asyncio
    async def test_add_item_rejects_unknown_unit(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()

        with pytest.raises(InvalidUnitError):
            await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="mleko", unit="wiaderko"))

        mock_repository.create_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_item_rejects_foreign_category(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()
        mock_repository.get_category.return_value = None

        with pytest.raises(CategoryNotFoundError):
            await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="mleko", categoryId="other"))

    @pytest.mark.asyncio
    async def test_add_item_requires_existing_list(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = None

        with pytest.raises(ShoppingListNotFoundError):
            await service.add_item("fam1", "missing", "user1", ShoppingItemCreateRequest(name="mleko"))


class TestQuickAdd:
    @pytest.mark.asyncio
    async def test_quick_add_parses_and_inserts(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()
        mock_repository.max_position.return_value = -1
        mock_repository.create_item.return_value = make_item(name="mąki", quantity=Decimal("2"), unit="kg", position=0)

        await service.quick_add("fam1", "list1", "user1", QuickAddRequest(text="2 kg mąki"))

        _, kwargs = mock_repository.create_item.call_args
        assert kwargs["name"] == "mąki"
        assert kwargs["unit"] == "kg"
        assert kwargs["quantity"] == Decimal("2")
        assert kwargs["position"] == 0


class TestUpdateItem:
    @pytest.mark.asyncio
    async def test_toggle_checked(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()
        item = make_item(is_checked=False)
        mock_repository.get_item.return_value = item

        response = await service.update_item("fam1", "list1", "item1", ShoppingItemUpdateRequest(isChecked=True))

        assert response.isChecked is True
        assert item.is_checked is True
        mock_repository.save.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_missing_item(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()
        mock_repository.get_item.return_value = None

        with pytest.raises(ShoppingItemNotFoundError):
            await service.update_item("fam1", "list1", "missing", ShoppingItemUpdateRequest(name="x"))


class TestReorder:
    @pytest.mark.asyncio
    async def test_reorder_updates_positions(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_list.return_value = make_list()
        item_a = make_item("a", position=0)
        item_b = make_item("b", position=1)
        mock_repository.list_items.return_value = [item_a, item_b]

        await service.reorder("fam1", "list1", ReorderRequest(items=[ReorderEntry(id="a", position=1), ReorderEntry(id="b", position=0)]))

        assert item_a.position == 1
        assert item_b.position == 0
        mock_repository.save.assert_awaited()


class TestCreateListSeedsCategories:
    @pytest.mark.asyncio
    async def test_first_list_seeds_default_categories(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.count_categories.return_value = 0
        mock_repository.create_list.return_value = make_list()

        await service.create_list("fam1", "user1", ShoppingListCreateRequest(name="Dom"))

        mock_repository.bulk_create_categories.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_second_list_does_not_reseed(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.count_categories.return_value = 9
        mock_repository.create_list.return_value = make_list()

        await service.create_list("fam1", "user1", ShoppingListCreateRequest(name="Weekend"))

        mock_repository.bulk_create_categories.assert_not_called()


class TestDeleteCategory:
    @pytest.mark.asyncio
    async def test_delete_missing_category(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        mock_repository.get_category.return_value = None

        with pytest.raises(CategoryNotFoundError):
            await service.delete_category("fam1", "missing")

    @pytest.mark.asyncio
    async def test_delete_category(self, service: ShoppingService, mock_repository: AsyncMock) -> None:
        category = CategoryDB(id="cat1", family_id="fam1", name="Nabiał", icon=None, sort_order=0)
        mock_repository.get_category.return_value = category

        await service.delete_category("fam1", "cat1")

        mock_repository.delete_category.assert_awaited_once_with(category)
