# AI Module

OpenRouter AI integration for Family Recipes.

## Overview

- **Recipe import from URL** — `POST /api/ai/recipes/import` fetches a page, asks OpenRouter for structured JSON, normalizes ingredients/units, returns a draft (does not persist)
- **Chat Interface** — conversational assistant (same access gate)
- **Token Management** — users can use their own OpenRouter API tokens
- **Caching** — PostgreSQL-based caching to reduce costs
- **History Tracking** — audit trail of AI interactions with token usage and costs

## Configuration

Required environment variables (see `backend/.env.example`):

```bash
AI_ENABLED=true
OPENROUTER_API_KEY=your_key_here
AI_TOKEN_ENCRYPTION_KEY=generate_with_fernet
AI_CACHE_ENABLED=true
AI_CACHE_TTL_CLASSIFY=7
AI_CACHE_TTL_EMBED=30
```

Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Access Control

AI endpoints that spend tokens use `require_ai_access` (`AiAccessUser`). Access is granted when:

1. User is **Premium**, **admin**, or **owner** (may use the system OpenRouter key), **or**
2. User has configured their **own OpenRouter API token** (`use_own_token` + encrypted token in `ai_user_settings`)

Otherwise the API returns **403**. Settings/models listing remain available to authenticated users so they can configure a token. Frontend mirrors this via `useAi().canUseAi`.

## Recipe import

```http
POST /api/ai/recipes/import
{ "url": "https://example.com/recipe" }
```

Response is a draft (`title`, `sourceUrl`, `category`, `servings`, `ingredients[]`) for the recipe form; save with `POST /api/recipes`.

## Development

### Testing

```bash
# Recipe import unit tests
pytest tests/test_recipe_import_service.py -v

# AI module tests
pytest tests/modules/ai -v
```

## References

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenAI SDK](https://github.com/openai/openai-python) (used for OpenRouter)
- [Fernet Encryption](https://cryptography.io/en/latest/fernet/)
- [docs/api.md](../../../../docs/api.md) — REST surface
- [docs/build-plan.md](../../../../docs/build-plan.md) — Faza 5 ✅
