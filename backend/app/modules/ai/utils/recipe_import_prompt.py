"""Prompt and parsing helpers for AI recipe import."""

from __future__ import annotations

import json
import re

from app.modules.ai.exceptions import StructuredOutputParsingError
from app.modules.recipes.constants import RECIPE_CATEGORIES
from app.modules.shopping.constants import UNITS

_RECIPE_IMPORT_JSON_PATTERN = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)

VALID_UNITS = ", ".join(UNITS)
VALID_CATEGORIES = ", ".join(sorted(RECIPE_CATEGORIES))


def build_recipe_import_prompt(page_text: str, source_url: str) -> list[dict[str, str]]:
    """Build chat messages for extracting a recipe draft from page text."""
    system = f"""You extract structured recipe data from web page text for a Polish family recipes app.
Return ONLY a JSON object (no markdown, no commentary) with this shape:
{{
  "title": "recipe title",
  "category": "one of: {VALID_CATEGORIES}",
  "servings": 4,
  "ingredients": [
    {{"name": "ingredient name in Polish when possible", "quantity": 2, "unit": "szklanka"}}
  ]
}}

Rules:
- Use Polish ingredient names when the page is Polish; otherwise translate common ingredients to Polish.
- quantity must be a number or null; unit must be one of: {VALID_UNITS}, or null.
- Prefer canonical units from the list (e.g. "łyżka" not "tbsp", "g" not "gram").
- Include all listed ingredients; skip section headers and instructions.
- category: breakfast for śniadania, lunch for obiady/dania główne, dinner for kolacje/light meals, dessert for desery.
- servings: integer or null if unknown."""

    user = f"""Source URL: {source_url}

Page text:
{page_text}"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def parse_recipe_import_json(message: str) -> dict:
    """Parse JSON recipe draft from an AI response."""
    candidates: list[str] = []

    for match in _RECIPE_IMPORT_JSON_PATTERN.finditer(message):
        candidates.append(match.group(1))

    if not candidates:
        object_match = _JSON_OBJECT_PATTERN.search(message.strip())
        if object_match:
            candidates.append(object_match.group(0))

    for raw in candidates:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "title" in data and "ingredients" in data:
            return data

    raise StructuredOutputParsingError("AI response did not contain a valid recipe JSON")
