# Security review — Backend

**Status:** `planned`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Scope

FastAPI backend (`backend/app/`) — moduły shared core (auth, users, 2FA, admin, billing) oraz domenowe (family, shopping, ingredients, recipes).

## Baseline

- [data-model.md](../data-model.md) — encje, ownership przez `family_id`
- [api.md](../api.md) — endpointy i autoryzacja
- [build-plan.md](../build-plan.md) — zakres modułów i feature flags
- Shared core z gear-stack (`backend/app/core/`, `backend/app/common/`) — weryfikacja driftu przy zmianach

## Checklist

- [ ] JWT: `type` claim, blacklist, refresh rotation, `iss`/`aud`, per-purpose keys
- [ ] Auth dependencies: `CurrentUser`, `AdminUser`, 2FA-pending rejection
- [ ] CSP and security headers (`app/core/security_headers.py`)
- [ ] CORS, `TrustedHost`, rate limiting, reCAPTCHA
- [ ] Input validation (Pydantic), SQL injection surfaces, mass-assignment
- [ ] Authorization on all family/shopping/ingredients/admin/AI endpoints (IDOR, membership checks)
- [ ] File upload: mime validation, path traversal, size limits, RustFS/S3 adapter
- [ ] Secrets: `SECRET_KEY` strength, production startup assertions, `.env` handling
- [ ] Error responses: no stack traces / secrets in production
- [ ] Feature limits enforcement (plan free/basic/pro, member limits)

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
