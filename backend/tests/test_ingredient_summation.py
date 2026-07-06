"""Tests for ingredient matching, unit conversion and shopping summation.

Covers the phase-3 acceptance criterion: adding "szklanka mąki" + "130 g mąki"
yields a single summed item, while "szklanka cukru" stays separate from
"szklanka mąki".
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.modules.ingredients.conversion import (
    IngredientMatch,
    build_match_terms,
    name_matches,
    normalize,
)
from app.modules.shopping.db_models import ShoppingListDB, ShoppingListItemDB
from app.modules.shopping.repository import ShoppingRepository
from app.modules.shopping.schemas import ShoppingItemCreateRequest
from app.modules.shopping.service import ShoppingService

# Ingredient conversion data used across tests.
FLOUR = IngredientMatch(ingredient_id="flour", base_unit="g", unit_to_base={"szklanka": Decimal("130"), "łyżka": Decimal("10")})
SUGAR = IngredientMatch(ingredient_id="sugar", base_unit="g", unit_to_base={"szklanka": Decimal("200")})


class TestConversion:
    def test_base_unit_passthrough(self) -> None:
        assert FLOUR.to_base(Decimal("130"), "g") == Decimal("130")

    def test_none_unit_defaults_to_base(self) -> None:
        assert FLOUR.to_base(Decimal("50"), None) == Decimal("50")

    def test_mapped_unit(self) -> None:
        assert FLOUR.to_base(Decimal("1"), "szklanka") == Decimal("130")
        assert FLOUR.to_base(Decimal("2"), "łyżka") == Decimal("20")

    def test_kg_to_grams(self) -> None:
        assert FLOUR.to_base(Decimal("1"), "kg") == Decimal("1000")

    def test_unmapped_unit_returns_none(self) -> None:
        assert FLOUR.to_base(Decimal("1"), "puszka") is None

    def test_none_quantity_returns_none(self) -> None:
        assert FLOUR.to_base(None, "szklanka") is None


class TestMatching:
    def test_normalize(self) -> None:
        assert normalize("  Mąka   Pszenna! ") == "mąka pszenna"

    def test_alias_word_match(self) -> None:
        terms = build_match_terms("mąka pszenna", ["mąka", "mąki"])
        assert name_matches("mąki", terms)
        assert name_matches("szklanka mąki", terms)

    def test_no_false_match(self) -> None:
        terms = build_match_terms("cukier", ["cukru"])
        assert not name_matches("mąki", terms)


class _FakeMatcher:
    """Matches item names to a fixed set of ingredient matches (by substring)."""

    def __init__(self, mapping: dict[str, IngredientMatch]):
        self.mapping = mapping

    async def match(self, name: str) -> IngredientMatch | None:
        lowered = name.lower()
        for key, value in self.mapping.items():
            if key in lowered:
                return value
        return None


def make_list() -> ShoppingListDB:
    now = datetime.now(UTC)
    return ShoppingListDB(id="list1", family_id="fam1", name="Dom", created_by="user1", created_at=now, updated_at=now)


def make_item(**overrides: object) -> ShoppingListItemDB:
    now = datetime.now(UTC)
    defaults: dict = {
        "id": "item1",
        "list_id": "list1",
        "name": "mąki",
        "category_id": None,
        "ingredient_id": "flour",
        "quantity": Decimal("1"),
        "unit": "szklanka",
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


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=ShoppingRepository)


class TestSummation:
    @pytest.mark.asyncio
    async def test_cup_of_flour_plus_grams_merge_into_base_unit(self, mock_repository: AsyncMock) -> None:
        """ "szklanka mąki" (1 * 130 g) + "130 g mąki" = one item of 260 g."""
        matcher = _FakeMatcher({"mąk": FLOUR})
        service = ShoppingService(repository=mock_repository, matcher=matcher)

        mock_repository.get_list.return_value = make_list()
        existing = make_item(quantity=Decimal("1"), unit="szklanka")
        mock_repository.find_active_items_by_ingredient.return_value = [existing]

        response = await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="mąki", quantity=130, unit="g"))

        assert existing.quantity == Decimal("260")
        assert existing.unit == "g"
        assert response.quantity == 260.0
        assert response.unit == "g"
        mock_repository.create_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_kg_plus_grams_merge(self, mock_repository: AsyncMock) -> None:
        matcher = _FakeMatcher({"mąk": FLOUR})
        service = ShoppingService(repository=mock_repository, matcher=matcher)

        mock_repository.get_list.return_value = make_list()
        existing = make_item(quantity=Decimal("500"), unit="g")
        mock_repository.find_active_items_by_ingredient.return_value = [existing]

        response = await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="mąki", quantity=1, unit="kg"))

        assert existing.quantity == Decimal("1500")
        assert existing.unit == "g"
        assert response.quantity == 1500.0

    @pytest.mark.asyncio
    async def test_cup_of_sugar_stays_separate_from_flour(self, mock_repository: AsyncMock) -> None:
        """Different ingredient => no matching active item => separate item."""
        matcher = _FakeMatcher({"mąk": FLOUR, "cukr": SUGAR})
        service = ShoppingService(repository=mock_repository, matcher=matcher)

        mock_repository.get_list.return_value = make_list()
        mock_repository.find_active_items_by_ingredient.return_value = []  # no sugar item yet
        mock_repository.max_position.return_value = 0
        mock_repository.create_item.return_value = make_item(id="item2", name="cukru", ingredient_id="sugar", quantity=Decimal("1"), unit="szklanka")

        await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="cukru", quantity=1, unit="szklanka"))

        mock_repository.create_item.assert_called_once()
        _, kwargs = mock_repository.create_item.call_args
        assert kwargs["ingredient_id"] == "sugar"
        mock_repository.find_active_items_by_ingredient.assert_awaited_once_with("list1", "sugar")

    @pytest.mark.asyncio
    async def test_unmapped_unit_keeps_items_separate(self, mock_repository: AsyncMock) -> None:
        """A unit with no conversion mapping cannot be summed => new item."""
        matcher = _FakeMatcher({"mąk": FLOUR})
        service = ShoppingService(repository=mock_repository, matcher=matcher)

        mock_repository.get_list.return_value = make_list()
        mock_repository.find_active_items_by_ingredient.return_value = [make_item()]
        mock_repository.max_position.return_value = 0
        mock_repository.create_item.return_value = make_item(id="item2", quantity=Decimal("1"), unit="puszka")

        # "puszka" is a valid unit but has no flour conversion -> stays separate
        await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="mąki", quantity=1, unit="puszka"))

        mock_repository.create_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_first_item_inserted_with_ingredient_id(self, mock_repository: AsyncMock) -> None:
        """First matching item is stored as entered, tagged with the ingredient."""
        matcher = _FakeMatcher({"mąk": FLOUR})
        service = ShoppingService(repository=mock_repository, matcher=matcher)

        mock_repository.get_list.return_value = make_list()
        mock_repository.find_active_items_by_ingredient.return_value = []
        mock_repository.max_position.return_value = -1
        mock_repository.create_item.return_value = make_item(quantity=Decimal("1"), unit="szklanka")

        await service.add_item("fam1", "list1", "user1", ShoppingItemCreateRequest(name="mąki", quantity=1, unit="szklanka"))

        _, kwargs = mock_repository.create_item.call_args
        assert kwargs["ingredient_id"] == "flour"
        assert kwargs["unit"] == "szklanka"
