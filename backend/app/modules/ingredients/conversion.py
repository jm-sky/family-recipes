"""Pure helpers for ingredient matching and unit conversion.

Kept free of I/O so the summation rules can be unit-tested directly.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal

_WORD_RE = re.compile(r"[a-ząćęłńóśźż0-9]+", re.IGNORECASE)

# Universal metric conversions when ingredient base_unit is g or ml.
_WEIGHT_TO_G: dict[str, Decimal] = {"g": Decimal("1"), "dag": Decimal("10"), "kg": Decimal("1000")}
_VOLUME_TO_ML: dict[str, Decimal] = {"ml": Decimal("1"), "l": Decimal("1000")}


def normalize(text: str) -> str:
    """Lowercase, trim and collapse whitespace for matching."""
    return " ".join(_WORD_RE.findall(text.lower()))


def _fold(text: str) -> str:
    """Normalize and strip diacritics, for accent-insensitive matching."""
    folded = unicodedata.normalize("NFKD", normalize(text))
    return "".join(c for c in folded if not unicodedata.combining(c))


@dataclass
class IngredientMatch:
    """Everything needed to sum an item into a known ingredient."""

    ingredient_id: str
    base_unit: str
    # unit -> how many base units one of that unit represents (base_unit -> 1)
    unit_to_base: dict[str, Decimal] = field(default_factory=dict)
    shopping_category_key: str | None = None

    def to_base(self, quantity: Decimal | None, unit: str | None) -> Decimal | None:
        """Convert (quantity, unit) into the base unit, or None if impossible."""
        if quantity is None:
            return None
        resolved_unit = (unit or self.base_unit).lower()
        if resolved_unit == self.base_unit:
            return quantity
        factor = self.unit_to_base.get(resolved_unit)
        if factor is not None:
            return quantity * factor
        if self.base_unit == "g" and resolved_unit in _WEIGHT_TO_G:
            return quantity * _WEIGHT_TO_G[resolved_unit]
        if self.base_unit == "ml" and resolved_unit in _VOLUME_TO_ML:
            return quantity * _VOLUME_TO_ML[resolved_unit]
        return None


def build_match_terms(name: str, aliases: list[str]) -> set[str]:
    """Build the set of folded terms that identify an ingredient."""
    terms = {_fold(name)}
    for alias in aliases:
        folded = _fold(alias)
        if folded:
            terms.add(folded)
    return {term for term in terms if term}


def name_matches(item_name: str, terms: set[str]) -> bool:
    """Return True when a shopping item name refers to an ingredient.

    Matches when the whole folded name equals a term, or any term appears as a
    standalone word within the name.
    """
    folded = _fold(item_name)
    if not folded:
        return False
    if folded in terms:
        return True
    words = set(folded.split())
    return any(term in words for term in terms)
