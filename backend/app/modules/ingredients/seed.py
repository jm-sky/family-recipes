"""Ingredient dataset seeding helpers."""

import logging

from app.modules.ingredients.repository import IngredientRepository
from app.modules.ingredients.seed_data import INGREDIENTS

logger = logging.getLogger(__name__)


async def seed_ingredients_if_empty(repository: IngredientRepository) -> int:
    """Populate the canonical ingredient dataset when the table is empty.

    Returns:
        Number of ingredients created (0 when already seeded).
    """
    if await repository.count() > 0:
        return 0
    created = await repository.bulk_create(INGREDIENTS)
    logger.info("Seeded %s ingredients", created)
    return created
