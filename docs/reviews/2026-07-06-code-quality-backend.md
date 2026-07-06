# Code quality review — Backend

**Status:** `planned`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Scope

FastAPI backend (`backend/app/`, `backend/tests/`) — moduły domenowe i shared core.

## Baseline

- [build-plan.md](../build-plan.md) — wzorzec modułowy (repository/service/router/schemas)
- [data-model.md](../data-model.md) — model danych docelowy
- `backend/pyproject.toml` — black, mypy config

## Checklist

- [ ] Modułowy wzorzec: spójność `db_models`, `schemas`, `repository`, `service`, `router`
- [ ] God files — SRP, podział odpowiedzialności w `shopping`, `family`, `ingredients`
- [ ] Repository pattern consistency and interface usage
- [ ] Dependency injection (`Depends`, settings singleton vs injected)
- [ ] Error handling and logging (Sentry filters, structured logs)
- [ ] Type hints and mypy coverage on critical paths
- [ ] Test coverage vs code volume (integration tests w `backend/tests/`)
- [ ] Konwersja jednostek i sumowanie — logika w `shopping` + `ingredients`
- [ ] CLI, migrations, seed scripts maintainability
- [ ] Shared-core drift z gear-stack przy zmianach w `core/` i `common/`

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
