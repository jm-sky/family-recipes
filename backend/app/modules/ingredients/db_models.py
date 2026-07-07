"""Database models for the canonical ingredient dataset and unit conversions."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, JSONBType


class IngredientDB(Base):
    """A canonical ingredient shared across families (read-only for users).

    Used to match free-text shopping items to a known ingredient so that
    quantities can be summed via unit conversions.
    """

    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSONBType, default=list, nullable=False)
    base_unit: Mapped[str] = mapped_column(String(8), nullable=False)  # "g" or "ml"
    # Lucide icon key of the default shopping category (see shopping.constants.DEFAULT_CATEGORIES).
    shopping_category_key: Mapped[str | None] = mapped_column(String(64), nullable=True)


class IngredientUnitDB(Base):
    """Per-ingredient conversion from a unit to the ingredient's base unit.

    ``amount_in_base`` is how many base units one ``unit`` represents, e.g. one
    "szklanka" of flour = 130 g. This makes conversions ingredient-dependent
    (a cup of flour differs from a cup of sugar).
    """

    __tablename__ = "ingredient_units"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ingredient_id: Mapped[str] = mapped_column(String(36), ForeignKey("ingredients.id"), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    amount_in_base: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
