# Family Recipes Phase 5 (AI import — recipe from URL) — completion log

Executed 2026-07-25. Endpoint for importing recipe drafts from external URLs, leveraging existing AI infrastructure (OpenRouter) for structured extraction.

## Backend

**Router:** `backend/app/modules/ai/routers/recipes.py`
- `POST /api/recipes/import` — main endpoint

**Service:** `backend/app/modules/ai/services/recipe_import_service.py`
- `import_from_url(user_id, url)` — fetch URL, parse HTML, call OpenRouter w/ structured output, validate/normalize ingredients

**Schemas** (`backend/app/modules/ai/schemas.py`):
- `RecipeImportRequest` — `{url: str}`
- `RecipeImportResponse` — `{name, description, ingredients[], source_url, status}`

**Access Control:**
- Gate via `AiAccessUser` dependency (inherited from `ai` module).
- Checks: Premium/admin/owner tier via subscription OR configured OpenRouter token (BYOK Free tier).
- Error: 403 if tier/token check fails; 503 if AI is disabled globally.

**Features:**
- **URL fetching** — HTTP GET, retry on transient errors, timeout protection.
- **HTML parsing** — lxml/BeautifulSoup for recipe meta tags + semantic extraction.
- **Structured extraction** — OpenRouter API w/ `RecipeSchema` (name, description, ingredients w/ amounts/units, source URL).
- **Ingredient normalization** — matches extracted ingredients to canonical `ingredients` dataset via fuzzy name matching; units converted to base units via `IngredientUnit` mappings.
- **Error handling** — `RecipeImportError` (bad URL, fetch timeout, parsing fail), `StructuredOutputParsingError` (AI returned invalid JSON schema).
- **Caching** — `PostgresCacheService` caches successful imports by URL (TTL 24h) to avoid re-parsing.

## Frontend

No new UI in Phase 5 — endpoint is contract-only. Frontend integration (form, upload flow, preview) deferred.

## Verification

Backend: `black`/`mypy` clean. API contract verified:
- `POST /api/recipes/import` with valid URL (e.g., food blog) → `{name, description, ingredients[], source_url}` response
- `POST /api/recipes/import` with bad URL → 400 (`RecipeImportError`)
- `POST /api/recipes/import` from Free tier (no BYOK token) → 403 (access denied)
- `POST /api/recipes/import` with disabled AI (`settings.ai.enabled=false`) → 503

Ingredients matched to dataset: tested with a real recipe containing "2 cups flour", "1 tbsp sugar" — both normalized to base units (g/ml) via `IngredientUnit` mappings.

## Follow-ups flagged, not resolved

- **Frontend UI** — forms to submit recipe URL, preview extraction, review/edit before saving. Candidates:
  - Modal on `RecipesPage` ("Import from URL" button).
  - Preview: recipe card with extracted data, edit fields for corrections.
  - Deferred pending mobile UX finalization (Faza native-mobile-ux).
- **HTML parser robustness** — current impl handles common recipe schema (JSON-LD, meta tags). Edge cases (flash-only recipes, paywalled content, non-English sites) not tested; may fail silently.
- **Ingredient dataset coverage** — matches work only for ingredients in the canonical `ingredients` table. Rare/exotic ingredients get rejected or mapped to "other"; seed dataset may need expansion.
- **Source attribution** — imported recipes store `source_url` but no UI credit/link yet. Add to recipe card when frontend lands.

## Notes

- Phase 5 arrived in same session as career-hub Phase 7 (concurrent AI delivery).
- Reuses `ai` module's OpenRouter integration, token accounting, and `AiAccessUser` pattern — no new provider setup needed.
- Service is stateless; no job queue (unlike CV PDF generation in career-hub). Single request → response cycle.
- Caching is opt-in (if enabled in config) to reduce API calls for repeated imports of same recipe URL.
