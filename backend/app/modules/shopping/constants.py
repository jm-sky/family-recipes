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

# Polish (and common) unit aliases mapped to canonical UNITS entries.
UNIT_ALIASES: dict[str, str] = {
    "szt.": "szt",
    "sztuk": "szt",
    "sztuki": "szt",
    "gram": "g",
    "gramów": "g",
    "gramy": "g",
    "kilogram": "kg",
    "kilogramów": "kg",
    "kilogramy": "kg",
    "mililitr": "ml",
    "mililitra": "ml",
    "mililitry": "ml",
    "litr": "l",
    "litra": "l",
    "litry": "l",
    "łyżki": "łyżka",
    "lyzka": "łyżka",
    "łyżeczki": "łyżeczka",
    "lyzeczka": "łyżeczka",
    "szklanki": "szklanka",
    "tbsp": "łyżka",
    "tsp": "łyżeczka",
    "cup": "szklanka",
    "cups": "szklanka",
}

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

# Canonical ingredient names shown as quick-add chips when the family has no history.
POPULAR_INGREDIENT_NAMES: list[str] = [
    "mleko",
    "jajko",
    "masło",
    "chleb",
    "mąka pszenna",
    "cukier",
    "pomidor",
    "cebula",
    "ziemniak",
    "olej",
    "ryż",
    "makaron",
    "ser żółty",
    "jogurt naturalny",
    "banan",
]
