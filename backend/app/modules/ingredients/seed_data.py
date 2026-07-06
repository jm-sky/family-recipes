"""Seed dataset: ~50 popular Polish-kitchen ingredients with conversions.

Each entry: name, aliases (incl. common inflections), base_unit (g|ml) and a
``units`` map of unit -> amount in the base unit (how many base units one of
that unit weighs/measures). Values are typical culinary approximations.
"""

from typing import TypedDict


class IngredientSeed(TypedDict):
    name: str
    aliases: list[str]
    base_unit: str
    units: dict[str, float]


INGREDIENTS: list[IngredientSeed] = [
    # --- Dry / baking (base: g) ---
    {"name": "mąka pszenna", "aliases": ["mąka", "mąki", "maka", "mąkę"], "base_unit": "g", "units": {"szklanka": 130, "łyżka": 10, "łyżeczka": 3}},
    {"name": "mąka żytnia", "aliases": ["mąka razowa"], "base_unit": "g", "units": {"szklanka": 120, "łyżka": 10, "łyżeczka": 3}},
    {"name": "cukier", "aliases": ["cukru", "cukier biały"], "base_unit": "g", "units": {"szklanka": 200, "łyżka": 12, "łyżeczka": 5}},
    {"name": "cukier puder", "aliases": ["puder"], "base_unit": "g", "units": {"szklanka": 130, "łyżka": 10, "łyżeczka": 3}},
    {"name": "cukier wanilinowy", "aliases": [], "base_unit": "g", "units": {"łyżeczka": 4}},
    {"name": "sól", "aliases": ["soli"], "base_unit": "g", "units": {"łyżka": 20, "łyżeczka": 6}},
    {"name": "pieprz czarny", "aliases": ["pieprz"], "base_unit": "g", "units": {"łyżka": 7, "łyżeczka": 2}},
    {"name": "soda oczyszczona", "aliases": ["soda"], "base_unit": "g", "units": {"łyżka": 15, "łyżeczka": 5}},
    {"name": "proszek do pieczenia", "aliases": [], "base_unit": "g", "units": {"łyżka": 12, "łyżeczka": 4}},
    {"name": "kakao", "aliases": ["kakao gorzkie"], "base_unit": "g", "units": {"szklanka": 100, "łyżka": 8, "łyżeczka": 3}},
    {"name": "ryż", "aliases": ["ryżu"], "base_unit": "g", "units": {"szklanka": 225, "łyżka": 20}},
    {"name": "kasza gryczana", "aliases": ["kasza"], "base_unit": "g", "units": {"szklanka": 180, "łyżka": 15}},
    {"name": "kasza jaglana", "aliases": [], "base_unit": "g", "units": {"szklanka": 200, "łyżka": 16}},
    {"name": "płatki owsiane", "aliases": ["owsianka", "płatki"], "base_unit": "g", "units": {"szklanka": 90, "łyżka": 8}},
    {"name": "makaron", "aliases": ["makaronu"], "base_unit": "g", "units": {"szklanka": 100}},
    {"name": "kasza manna", "aliases": ["manna"], "base_unit": "g", "units": {"szklanka": 170, "łyżka": 14}},
    {"name": "bułka tarta", "aliases": ["panierka"], "base_unit": "g", "units": {"szklanka": 130, "łyżka": 10}},
    {"name": "orzechy włoskie", "aliases": ["orzechy"], "base_unit": "g", "units": {"szklanka": 100, "łyżka": 9}},
    {"name": "migdały", "aliases": [], "base_unit": "g", "units": {"szklanka": 140, "łyżka": 11}},
    {"name": "rodzynki", "aliases": [], "base_unit": "g", "units": {"szklanka": 160, "łyżka": 12}},
    {"name": "mak", "aliases": [], "base_unit": "g", "units": {"szklanka": 160, "łyżka": 13}},
    {"name": "kasza pęczak", "aliases": ["pęczak"], "base_unit": "g", "units": {"szklanka": 200}},
    # --- Liquids (base: ml) ---
    {"name": "mleko", "aliases": ["mleka"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}},
    {"name": "woda", "aliases": ["wody"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}},
    {"name": "olej", "aliases": ["oleju"], "base_unit": "ml", "units": {"szklanka": 220, "łyżka": 15, "łyżeczka": 5}},
    {"name": "oliwa z oliwek", "aliases": ["oliwa"], "base_unit": "ml", "units": {"szklanka": 220, "łyżka": 15, "łyżeczka": 5}},
    {"name": "śmietana", "aliases": ["śmietany", "śmietanka"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}},
    {"name": "jogurt naturalny", "aliases": ["jogurt"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15}},
    {"name": "ocet", "aliases": ["octu"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15, "łyżeczka": 5}},
    {"name": "sok z cytryny", "aliases": ["sok cytrynowy"], "base_unit": "ml", "units": {"łyżka": 15, "łyżeczka": 5}},
    {"name": "miód", "aliases": ["miodu"], "base_unit": "g", "units": {"łyżka": 25, "łyżeczka": 9}},
    {"name": "przecier pomidorowy", "aliases": ["passata"], "base_unit": "ml", "units": {"szklanka": 250, "łyżka": 15}},
    # --- Fats / dairy (base: g) ---
    {"name": "masło", "aliases": ["masła"], "base_unit": "g", "units": {"łyżka": 15, "łyżeczka": 5, "kostka": 200}},
    {"name": "margaryna", "aliases": [], "base_unit": "g", "units": {"łyżka": 15, "łyżeczka": 5, "kostka": 250}},
    {"name": "ser żółty", "aliases": ["ser"], "base_unit": "g", "units": {"plaster": 20}},
    {"name": "twaróg", "aliases": ["ser biały", "twarogu"], "base_unit": "g", "units": {"szklanka": 240, "łyżka": 30}},
    # --- Countable produce (base: g, with szt average weight) ---
    {"name": "jajko", "aliases": ["jajka", "jaja", "jajek"], "base_unit": "g", "units": {"szt": 56}},
    {"name": "cebula", "aliases": ["cebuli", "cebulę"], "base_unit": "g", "units": {"szt": 100}},
    {"name": "czosnek", "aliases": ["czosnku"], "base_unit": "g", "units": {"ząbek": 5, "główka": 40}},
    {"name": "marchew", "aliases": ["marchewka", "marchwi"], "base_unit": "g", "units": {"szt": 70}},
    {"name": "ziemniak", "aliases": ["ziemniaki", "kartofel"], "base_unit": "g", "units": {"szt": 120}},
    {"name": "pomidor", "aliases": ["pomidory", "pomidorów"], "base_unit": "g", "units": {"szt": 120}},
    {"name": "ogórek", "aliases": ["ogórki", "ogórka"], "base_unit": "g", "units": {"szt": 100}},
    {"name": "papryka", "aliases": ["papryki"], "base_unit": "g", "units": {"szt": 150}},
    {"name": "jabłko", "aliases": ["jabłka", "jabłek"], "base_unit": "g", "units": {"szt": 150}},
    {"name": "banan", "aliases": ["banany", "bananów"], "base_unit": "g", "units": {"szt": 120}},
    {"name": "cytryna", "aliases": ["cytryny"], "base_unit": "g", "units": {"szt": 100}},
    {"name": "pietruszka", "aliases": ["natka pietruszki"], "base_unit": "g", "units": {"pęczek": 40, "łyżka": 4}},
    {"name": "koper", "aliases": ["koperek"], "base_unit": "g", "units": {"pęczek": 30, "łyżka": 4}},
    {"name": "kapusta", "aliases": ["kapusty"], "base_unit": "g", "units": {"szt": 1000}},
    {"name": "pieczarki", "aliases": ["pieczarka"], "base_unit": "g", "units": {"szt": 25}},
]
