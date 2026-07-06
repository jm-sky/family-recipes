# Performance review — Backend

**Status:** `planned`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Scope

FastAPI backend, PostgreSQL, Redis, RustFS storage.

## Baseline

- [data-model.md](../data-model.md) — relacje i indeksy
- [api.md](../api.md) — endpointy list/detail
- [build-plan.md](../build-plan.md) — logika sumowania jednostek (Faza 3)

## Checklist

- [ ] N+1 queries w listach zakupów, pozycjach, składnikach
- [ ] Missing indexes on hot paths (`shopping_items`, `ingredients`, FKs)
- [ ] Large payloads: listy z wieloma pozycjami, eksport
- [ ] SQLAlchemy session lifecycle (commits, flush, transaction boundaries)
- [ ] Image processing and storage I/O (RustFS/S3)
- [ ] Rate limiting impact under load
- [ ] AI module: streaming, timeouts, token usage (gdy włączony)
- [ ] Caching opportunities (ingredients dataset, read-heavy endpoints)
- [ ] Konwersja jednostek — koszt obliczeń przy sumowaniu pozycji

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
