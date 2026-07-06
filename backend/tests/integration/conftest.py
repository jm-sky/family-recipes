"""Fixtures for integration tests (async SQLAlchemy + in-memory SQLite)."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Must be set before app imports that read settings.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-min-32-characters-long-for-testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app.core.database import Base
from app.modules.auth.db_models import UserDB
from app.modules.family.db_models import FamilyDB, FamilyMembershipDB
from app.modules.ingredients.db_models import IngredientDB, IngredientUnitDB
from app.modules.ingredients.repository import IngredientRepository
from app.modules.ingredients.seed_data import INGREDIENTS
from app.modules.shopping.db_models import CategoryDB, ShoppingListDB, ShoppingListItemDB

# Ensure SQLAlchemy registers all domain tables used in integration tests.
_ = (
    UserDB,
    FamilyDB,
    FamilyMembershipDB,
    IngredientDB,
    IngredientUnitDB,
    CategoryDB,
    ShoppingListDB,
    ShoppingListItemDB,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fresh async database session with schema created per test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_ingredients(db_session: AsyncSession) -> IngredientRepository:
    """Ingredient repository with the full MVP seed dataset loaded."""
    repository = IngredientRepository(db_session)
    await repository.bulk_create(INGREDIENTS)
    return repository
