"""Seed dataset: popular Polish-kitchen ingredients with conversions.

Each entry: name, aliases (incl. common inflections), base_unit (g|ml),
``units`` map and ``shopping_category_key`` (Lucide icon key from
``shopping.constants.DEFAULT_CATEGORIES``).
"""

from typing import TypedDict


class IngredientSeed(TypedDict):
    name: str
    aliases: list[str]
    base_unit: str
    units: dict[str, float]
    shopping_category_key: str


INGREDIENTS: list[IngredientSeed] = [
    # --- Dry / baking (base: g) ---
    {"name": "mąka pszenna", "aliases": ["mąka", "mąki", "maka", "mąkę"], "base_unit": "g", "units": {"szklanka": 130, "łyżka": 10, "łyżeczka": 3}, "shopping_category_key": "wheat"},
    {"name": "mąka żytnia", "aliases": ["mąka razowa"], "base_unit": "g", "units": {"szklanka": 120, "łyżka": 10, "łyżeczka": 3}, "shopping_category_key": "wheat"},
    {"name": "cukier", "aliases": ["cukru", "cukier biały"], "base_unit": "g", "units": {"szklanka": 200, "łyżka": 12, "łyżeczka": 5}, "shopping_category_key": "wheat"},
    {"name": "cukier puder", "aliases": ["puder"], "base_unit": "g", "units": {"szklanka": 130, "łyżka": 10, "łyżeczka": 3}, "shopping_category_key": "wheat"},
    {"name": "cukier wanilinowy", "aliases": [], "base_unit": "g", "units": {"łyżeczka": 4}, "shopping_category_key": "wheat"},
    {"name": "sól", "aliases": ["soli"], "base_unit": "g", "units": {"łyżka": 20, "łyżeczka": 6}, "shopping_category_key": "wheat"},
    {"name": "pieprz czarny", "aliases": ["pieprz"], "base_unit": "g", "units": {"łyżka": 7, "łyżeczka": 2}, "shopping_category_key": "wheat"},
    {"name": "soda oczyszczona", "aliases": ["soda"], "base_unit": "g", "units": {"łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "wheat"},
    {"name": "proszek do pieczenia", "aliases": [], "base_unit": "g", "units": {"łyżka": 12, "łyżeczka": 4}, "shopping_category_key": "wheat"},
    {"name": "kakao", "aliases": ["kakao gorzkie"], "base_unit": "g", "units": {"szklanka": 100, "łyżka": 8, "łyżeczka": 3}, "shopping_category_key": "wheat"},
    {"name": "ryż", "aliases": ["ryżu"], "base_unit": "g", "units": {"szklanka": 225, "łyżka": 20}, "shopping_category_key": "wheat"},
    {"name": "kasza gryczana", "aliases": ["kasza"], "base_unit": "g", "units": {"szklanka": 180, "łyżka": 15}, "shopping_category_key": "wheat"},
    {"name": "kasza jaglana", "aliases": [], "base_unit": "g", "units": {"szklanka": 200, "łyżka": 16}, "shopping_category_key": "wheat"},
    {"name": "płatki owsiane", "aliases": ["owsianka", "płatki"], "base_unit": "g", "units": {"szklanka": 90, "łyżka": 8}, "shopping_category_key": "wheat"},
    {"name": "makaron", "aliases": ["makaronu"], "base_unit": "g", "units": {"szklanka": 100}, "shopping_category_key": "wheat"},
    {"name": "kasza manna", "aliases": ["manna"], "base_unit": "g", "units": {"szklanka": 170, "łyżka": 14}, "shopping_category_key": "wheat"},
    {"name": "bułka tarta", "aliases": ["panierka"], "base_unit": "g", "units": {"szklanka": 130, "łyżka": 10}, "shopping_category_key": "wheat"},
    {"name": "orzechy włoskie", "aliases": ["orzechy"], "base_unit": "g", "units": {"szklanka": 100, "łyżka": 9}, "shopping_category_key": "wheat"},
    {"name": "migdały", "aliases": [], "base_unit": "g", "units": {"szklanka": 140, "łyżka": 11}, "shopping_category_key": "wheat"},
    {"name": "rodzynki", "aliases": [], "base_unit": "g", "units": {"szklanka": 160, "łyżka": 12}, "shopping_category_key": "wheat"},
    {"name": "mak", "aliases": [], "base_unit": "g", "units": {"szklanka": 160, "łyżka": 13}, "shopping_category_key": "wheat"},
    {"name": "kasza pęczak", "aliases": ["pęczak"], "base_unit": "g", "units": {"szklanka": 200}, "shopping_category_key": "wheat"},
    # --- Liquids (base: ml) ---
    {"name": "mleko", "aliases": ["mleka"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "milk"},
    {"name": "woda", "aliases": ["wody"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "cup-soda"},
    {"name": "olej", "aliases": ["oleju"], "base_unit": "ml", "units": {"szklanka": 220, "łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "wheat"},
    {"name": "oliwa z oliwek", "aliases": ["oliwa"], "base_unit": "ml", "units": {"szklanka": 220, "łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "wheat"},
    {"name": "śmietana", "aliases": ["śmietany", "śmietanka"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "milk"},
    {"name": "jogurt naturalny", "aliases": ["jogurt"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15}, "shopping_category_key": "milk"},
    {"name": "ocet", "aliases": ["octu"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "wheat"},
    {"name": "sok z cytryny", "aliases": ["sok cytrynowy"], "base_unit": "ml", "units": {"łyżka": 15, "łyżeczka": 5}, "shopping_category_key": "cup-soda"},
    {"name": "miód", "aliases": ["miodu"], "base_unit": "g", "units": {"łyżka": 25, "łyżeczka": 9}, "shopping_category_key": "wheat"},
    {"name": "przecier pomidorowy", "aliases": ["passata"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15}, "shopping_category_key": "wheat"},
    # --- Fats / dairy (base: g) ---
    {"name": "masło", "aliases": ["masła"], "base_unit": "g", "units": {"łyżka": 15, "łyżeczka": 5, "kostka": 200}, "shopping_category_key": "milk"},
    {"name": "margaryna", "aliases": [], "base_unit": "g", "units": {"łyżka": 15, "łyżeczka": 5, "kostka": 250}, "shopping_category_key": "milk"},
    {"name": "ser żółty", "aliases": ["ser"], "base_unit": "g", "units": {"plaster": 20}, "shopping_category_key": "milk"},
    {"name": "twaróg", "aliases": ["ser biały", "twarogu"], "base_unit": "g", "units": {"szklanka": 240, "łyżka": 30}, "shopping_category_key": "milk"},
    # --- Countable produce (base: g, with szt average weight) ---
    {"name": "jajko", "aliases": ["jajka", "jaja", "jajek"], "base_unit": "g", "units": {"szt": 56}, "shopping_category_key": "milk"},
    {"name": "cebula", "aliases": ["cebuli", "cebulę"], "base_unit": "g", "units": {"szt": 100}, "shopping_category_key": "carrot"},
    {"name": "czosnek", "aliases": ["czosnku"], "base_unit": "g", "units": {"ząbek": 5, "główka": 40}, "shopping_category_key": "carrot"},
    {"name": "marchew", "aliases": ["marchewka", "marchwi"], "base_unit": "g", "units": {"szt": 70}, "shopping_category_key": "carrot"},
    {"name": "ziemniak", "aliases": ["ziemniaki", "kartofel"], "base_unit": "g", "units": {"szt": 120}, "shopping_category_key": "carrot"},
    {"name": "pomidor", "aliases": ["pomidory", "pomidorów"], "base_unit": "g", "units": {"szt": 120}, "shopping_category_key": "carrot"},
    {"name": "ogórek", "aliases": ["ogórki", "ogórka"], "base_unit": "g", "units": {"szt": 100}, "shopping_category_key": "carrot"},
    {"name": "papryka", "aliases": ["papryki"], "base_unit": "g", "units": {"szt": 150}, "shopping_category_key": "carrot"},
    {"name": "jabłko", "aliases": ["jabłka", "jabłek"], "base_unit": "g", "units": {"szt": 150}, "shopping_category_key": "carrot"},
    {"name": "banan", "aliases": ["banany", "bananów"], "base_unit": "g", "units": {"szt": 120}, "shopping_category_key": "carrot"},
    {"name": "cytryna", "aliases": ["cytryny"], "base_unit": "g", "units": {"szt": 100}, "shopping_category_key": "carrot"},
    {"name": "pietruszka", "aliases": ["natka pietruszki"], "base_unit": "g", "units": {"pęczek": 40, "łyżka": 4}, "shopping_category_key": "carrot"},
    {"name": "koper", "aliases": ["koperek"], "base_unit": "g", "units": {"pęczek": 30, "łyżka": 4}, "shopping_category_key": "carrot"},
    {"name": "kapusta", "aliases": ["kapusty"], "base_unit": "g", "units": {"szt": 1000}, "shopping_category_key": "carrot"},
    {"name": "pieczarki", "aliases": ["pieczarka"], "base_unit": "g", "units": {"szt": 25}, "shopping_category_key": "carrot"},
    # --- Grocery staples (suggestions without unit conversions) ---
    {"name": "chleb", "aliases": ["chleba", "chleb razowy"], "base_unit": "g", "units": {"szt": 400}, "shopping_category_key": "croissant"},
    {"name": "bułka", "aliases": ["bułki", "bułkę"], "base_unit": "g", "units": {"szt": 60}, "shopping_category_key": "croissant"},
    {"name": "papier toaletowy", "aliases": ["papier"], "base_unit": "g", "units": {"opakowanie": 1}, "shopping_category_key": "spray-can"},
]
