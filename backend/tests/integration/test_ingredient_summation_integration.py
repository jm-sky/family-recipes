"""Integration tests for ingredient matching and shopping-list summation (Phase 3)."""

import pytest

from app.common.id_utils import generate_id
from app.modules.auth.db_models import UserDB
from app.modules.family.db_models import FamilyDB, FamilyMembershipDB
from app.modules.ingredients.repository import IngredientRepository
from app.modules.ingredients.service import IngredientService
from app.modules.shopping.repository import ShoppingRepository
from app.modules.shopping.schemas import QuickAddRequest, ShoppingItemCreateRequest, ShoppingListCreateRequest
from app.modules.shopping.service import ShoppingService


async def _bootstrap_list(db_session) -> tuple[ShoppingService, str, str, str]:
    """Create user, family and shopping list; return service, user_id, family_id, list_id."""
    user_id = generate_id()
    family_id = generate_id()
    db_session.add(
        UserDB(
            id=user_id,
            email=f"{user_id}@example.com",
            name="Test User",
            hashed_password="hash",
        )
    )
    db_session.add(FamilyDB(id=family_id, name="Test Family", owner_id=user_id, plan="free"))
    db_session.add(FamilyMembershipDB(family_id=family_id, user_id=user_id, role="owner"))
    await db_session.commit()

    shopping_repo = ShoppingRepository(db_session)
    ingredient_service = IngredientService(IngredientRepository(db_session))
    service = ShoppingService(repository=shopping_repo, matcher=ingredient_service)

    created = await service.create_list(family_id, user_id, ShoppingListCreateRequest(name="Dom"))
    return service, user_id, family_id, created.id


@pytest.mark.asyncio
async def test_flour_cup_plus_grams_merge_on_real_dataset(db_session, seeded_ingredients) -> None:
    """Phase-3 acceptance: szklanka mąki + 130 g mąki => one item of 260 g."""
    service, user_id, family_id, list_id = await _bootstrap_list(db_session)

    await service.add_item(family_id, list_id, user_id, ShoppingItemCreateRequest(name="mąki", quantity=1, unit="szklanka"))
    response = await service.add_item(family_id, list_id, user_id, ShoppingItemCreateRequest(name="mąki", quantity=130, unit="g"))

    detail = await service.get_list_detail(family_id, list_id)
    assert len(detail.items) == 1
    assert detail.items[0].quantity == 260.0
    assert detail.items[0].unit == "g"
    assert detail.items[0].ingredientId is not None
    assert response.quantity == 260.0


@pytest.mark.asyncio
async def test_sugar_cup_stays_separate_from_flour(db_session, seeded_ingredients) -> None:
    """Phase-3 acceptance: szklanka cukru is separate from szklanka mąki."""
    service, user_id, family_id, list_id = await _bootstrap_list(db_session)

    await service.add_item(family_id, list_id, user_id, ShoppingItemCreateRequest(name="mąki", quantity=1, unit="szklanka"))
    await service.add_item(family_id, list_id, user_id, ShoppingItemCreateRequest(name="cukru", quantity=1, unit="szklanka"))

    detail = await service.get_list_detail(family_id, list_id)
    assert len(detail.items) == 2
    units_by_name = {item.name: (item.quantity, item.unit) for item in detail.items}
    assert units_by_name["mąki"] == (1.0, "szklanka")
    assert units_by_name["cukru"] == (1.0, "szklanka")
    assert detail.items[0].ingredientId != detail.items[1].ingredientId


@pytest.mark.asyncio
async def test_quick_add_parses_and_sums(db_session, seeded_ingredients) -> None:
    """Quick-add free text participates in the same summation pipeline."""
    service, user_id, family_id, list_id = await _bootstrap_list(db_session)

    await service.quick_add(family_id, list_id, user_id, QuickAddRequest(text="szklanka mąki"))
    response = await service.quick_add(family_id, list_id, user_id, QuickAddRequest(text="130 g mąki"))

    assert response.quantity == 260.0
    assert response.unit == "g"
