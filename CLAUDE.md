# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Family Recipes to aplikacja PWA do rodzinnych przepisów i list zakupowych (Vue 3 + FastAPI). Projekt powstał jako kopia boilerplate'u **gear-stack** (`../gear-stack`) — współdzieli z nim core (auth, users, 2FA, admin, billing, AI-skeleton), ale ma własną domenę: rodziny (family), listy zakupów, składniki, przepisy.

Dokumenty produktowe i wykonawcze:
- [README.md](README.md) — product requirements (PRD)
- [docs/build-plan.md](docs/build-plan.md) — fazowy plan budowy (Fazy 0–6)
- [docs/data-model.md](docs/data-model.md) — encje i relacje
- [docs/api.md](docs/api.md) — REST API
- [docs/sync-and-conflicts.md](docs/sync-and-conflicts.md) — offline / konflikty

## Docs workflow

- **Issues:** [docs/issues/README.md](docs/issues/README.md)
- **Reviews:** [docs/reviews/README.md](docs/reviews/README.md)
- **Research:** [docs/research/README.md](docs/research/README.md)
- **Plans:** [docs/plans/README.md](docs/plans/README.md)

Statuses: `todo`, `planned`, `in progress`, `done`, `verification needed`. New issues: `YYYY-MM-DD--NNN--slug.md`; reviews/research/plans: `YYYY-MM-DD-slug.md`.

## CRITICAL — Shared server safety

- To jest **serwer współdzielony** — nie ruszaj niczego poza tym projektem.
- **Nie modyfikuj `../gear-stack`** (boilerplate jest tylko do odczytu).
- **Nie uruchamiaj Dockera w katalogach z prefiksem `_`** (to katalogi robocze produkcji).
- Wszystkie porty bindowane wyłącznie do `127.0.0.1`.
- Nazwy kontenerów/wolumenów/sieci z prefiksem `family-recipes-*` / `family_recipes_*`.
- Sekrety z `.env` — nigdy nie pokazuj ich w output (redaguj).

## Ports & services

| Usługa | Port (localhost) |
|---|---|
| Backend API (FastAPI) | 8002 |
| PostgreSQL | 5434 |
| Redis | 6381 |
| Frontend dev (Vite) | 5177 |

Storage: istniejący **RustFS** (S3-compatible, kontener `rustfs-server:9000` w zewnętrznej sieci `rustfs-network`), bucket `family-recipes`. Nie używamy MinIO.

API prefix: `/api` (np. `POST /api/auth/login`). Healthcheck: `GET /health`.

## Commands

### Frontend (pnpm — nigdy npm/yarn)
```bash
pnpm dev              # Dev server (port 5177)
pnpm build            # Production build (type-check + build)
pnpm type-check       # vue-tsc
pnpm lint             # ESLint z auto-fix
pnpm test:run         # Vitest (unit; e2e/integration są wykluczone)
pnpm test:e2e         # Playwright e2e (wymaga backendu + dev servera)
```

Uwaga: lokalnie brakuje bibliotek systemowych Chromium — testy e2e uruchamiaj przez Docker:
```bash
docker run --rm --network=host -v "$PWD":/work -w /work -e CI=1 \
  mcr.microsoft.com/playwright:v1.60.0-noble \
  npx playwright test tests/e2e --config=tests/e2e/playwright.config.ts --project=chromium
```

### Backend (Docker Compose V2 — `docker compose`, nie `docker-compose`)
```bash
# From repo root (compose.yaml → docker-compose.dev.yml, name: family-recipes)
docker compose up -d
docker compose down
docker exec family-recipes-app python cli.py db init      # Inicjalizacja bazy
docker exec -it family-recipes-app python cli.py users create # Tworzenie użytkownika (interaktywnie)
docker exec family-recipes-app python cli.py users create --no-input --email user@example.com --name "User" --password "SecurePass123!" # Bez TTY
docker exec family-recipes-app python -m pytest tests/ -v # Testy backendu
```

Auto-reload (WatchFiles) jest włączony — restart kontenera potrzebny tylko po zmianie `.env` lub zależności.

**Important:** Run Compose from the **repo root**, not `backend/`. Project name is set via top-level `name: family-recipes`.

**Uwaga na mounty:** do kontenera montowane są `backend/app/`, `scripts/`, `tests/`, `migrations/`, `main.py` (rw) oraz `cli/`, `cli.py` (ro). `pyproject.toml` NIE jest montowany — dlatego black/mypy uruchamiaj z podmontowanym katalogiem:

```bash
docker run --rm -v "$PWD/backend":/work -w /work --entrypoint black family-recipes-backend:dev app cli --check
docker run --rm -v "$PWD/backend":/work -w /work --entrypoint mypy  family-recipes-backend:dev app
```

## Quality gates (przed commitem)

- Backend: `black --check` + `mypy` (config w `backend/pyproject.toml`, line-length 256) + `pytest`
- Frontend: `pnpm type-check` + `pnpm lint` + `pnpm build` + `pnpm test:run`

## Architecture

### Backend (`backend/`)
FastAPI + SQLAlchemy async + PostgreSQL 17 + Redis 8. Wzorzec modułowy — każdy moduł w `app/modules/<nazwa>/` zawiera: `db_models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`. Wspólny kod w `app/core/` i `app/common/`. CLI (typer) w `cli/`. JWT z jti/tv (token versioning), WebAuthn/TOTP 2FA.

### Frontend (`src/`)
Vue 3.5 `<script setup>` + TypeScript strict + Pinia + TanStack Query + TailwindCSS v4 + shadcn-vue/reka-ui. Moduły w `src/modules/<nazwa>/` (components, pages, services, store, i18n, config/routes). Rejestr i18n: moduł eksportuje `<name>En`/`<name>Pl` z `i18n/index.ts`. i18n zawsze PL + EN.

### Konwencje kodu (za gear-stack)
- Bez średników, pojedyncze cudzysłowy, sortowanie importów (Perfectionist)
- Tailwind: `size-{n}` zamiast `w-{n} h-{n}`
- Alias `@/` = `src/`; `defineModel` dla v-model w komponentach
- Backend: black (line-length 256), mypy strict-ish, docstringi Google style

## Feature flags (stan MVP)

- `AI_ENABLED=false` / `VITE_ENABLE_AI=false` — moduł AI jest szkieletem
- `STRIPE_ENABLED=false` — billing wyłączony (plany enforce'owane lokalnie: free/basic/pro)
- `EMAIL_ENABLED=false`, `EMAIL_ADAPTER=file` — maile do pliku w dev

## Build status (Fazy z build-plan.md)

- Faza 0 (bootstrap/rebranding): ukończona
- Faza 1 (Family), Faza 2 (Shopping), Faza 3 (Ingredients + sumowanie jednostek): w toku
- Fazy 4–6 (Recipes, AI import, sync/search): poza zakresem obecnego MVP
