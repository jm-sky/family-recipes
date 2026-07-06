"""Constants for the shopping module."""

# Predefined list of units (README section 2). Kept in code + validated;
# no dedicated table. Includes metric base units and common Polish cooking
# measures that the ingredients dataset can map to a base unit later.
UNITS: list[str] = [
    "szt",
    "g",
    "dag",
    "kg",
    "ml",
    "l",
    "szklanka",
    "łyżka",
    "łyżeczka",
    "opakowanie",
    "puszka",
    "butelka",
    "pęczek",
    "ząbek",
    "plaster",
    "garść",
    "szczypta",
]

UNITS_SET: frozenset[str] = frozenset(UNITS)

# Default categories seeded when a family creates its first shopping list.
# (name, icon) — icons are lucide keys used by the frontend.
DEFAULT_CATEGORIES: list[tuple[str, str]] = [
    ("Warzywa i owoce", "carrot"),
    ("Nabiał", "milk"),
    ("Pieczywo", "croissant"),
    ("Mięso i wędliny", "beef"),
    ("Sypkie", "wheat"),
    ("Napoje", "cup-soda"),
    ("Mrożonki", "snowflake"),
    ("Chemia", "spray-can"),
    ("Inne", "shopping-basket"),
]
