# Plan budowy (dla Fable)

Ten dokument jest **wykonawczy** — opisuje, jak zbudować MVP family-recipes na
bazie boilerplate'u gear-stack, w kolejności faz nadających się do realizacji
autonomicznej. Dokumenty powiązane:
[README.md](../README.md) (zakres), [data-model.md](data-model.md) (encje),
[api.md](api.md) (endpointy), [sync-and-conflicts.md](sync-and-conflicts.md) (offline).

## Zasada bazowa

gear-stack (https://github.com/jm-sky/gear-stack) to boilerplate. Proces
(README sekcja 0):
1. Skopiuj całość z gear-stack.
2. Usuń rzeczy niepotrzebne w domenie przepisów.
3. Podmień fragmenty i słowa kluczowe specyficzne dla gear-stack.
4. Dodaj logikę domenową jako nowe moduły w `modules/`.

Stack docelowy (README sekcja 8): Vue 3 + Tailwind (shadcn-vue/reka-ui) + PWA,
FastAPI, Postgres, Docker, TanStack Query, Pinia, i18n (PL+EN), pnpm.

## Co z gear-stack ZOSTAJE (bez zmian domenowych)

Infrastruktura / shared core — kopiujemy 1:1, tylko rebranding nazw/portów:
- `backend/app/core/*` (database, auth, storage adapter, email)
- `backend/app/common/*`, `backend/app/exceptions/*`
- `backend/cli/*` (zarządzanie bazą, użytkownikami, seed, test)
- `backend/migrations/*` (baza pod migracje)
- Docker Compose (`compose.yaml` → `docker-compose.dev.yml` w root)
- Frontend: `src/shared/*`, `src/components/ui/*`, `src/components/data-table/*`,
  `src/components/layout/*`, `src/layouts/*`, `src/router/*`, `src/i18n/*`,
  konfiguracja PWA (`pwa.config.ts`), Vite/ESLint/TS config.

Moduły przenoszone jak są (z rebrandingiem):
- `auth` (email+hasło, WebAuthn/passkeys, JWT), `users`, `two_factor`,
  OAuth Google, `settings`, `admin`, `stats`, `logs`, `feature_limits`.
- `ai` — **zostaje szkielet** (OpenRouter provider, cache, router), ale zawartość
  domenowa (prompty/parsery gear) → wymieniana na import przepisów.
- `billing` — zostaje, **disabled** feature flagą (README sekcja 12).

## Co z gear-stack ZNIKA / zostaje wymienione

- Cały moduł domenowy `gear` (backend `app/modules/gear`, frontend `src/modules/gear`)
  — usuwany. Jego **wzorce** (V2: repository/service/router/schemas, TanStack
  Query keys, Pinia store, data-table) są szablonem dla nowych modułów.
  Nie przenosimy długu V1/V2 — nowe moduły od razu w jednym, czystym modelu.
- `gear_settings`, obrazy katalogu gear, seed „catalogue" — usuwane.
- `tenants` → **przemianowany na `family`** (patrz niżej), nie duplikujemy.

## Mapa rebrandingu (podmiana słów kluczowych)

| gear-stack | family-recipes |
|---|---|
| `gear-stack` / „Gear Stack" | `family-recipes` / „Family Recipes" |
| `tenant` / `Tenant` | `family` / `Family` |
| `container` / `gear item` | (brak — domena inna) |
| kontener `gear-stack-app` | `family-recipes-app` |
| localStorage `gear-stack:*` | `family-recipes:*` |
| port dev 5176 | do wyboru (np. 5177) |

## Nowe moduły domenowe

Backend (`backend/app/modules/`), każdy wg wzorca gear V2
(`db_models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`):
- `family` — rodzina, membership, zaproszenia (z `tenants` + limity planu).
- `shopping` — listy zakupów i pozycje (sumowanie + konwersja jednostek).
- `recipes` — przepisy, składniki, tagi, upload zdjęć.
- `ingredients` — dataset kanoniczny + `IngredientUnit` (konwersje), seed.
- rozszerzenie `ai` — endpoint importu przepisu z linku.
- `sync` — endpointy `changes` / `push` (offline reconcile).
- `audit` — minimalny audit log (kto/kiedy).

Frontend (`src/modules/`), wg wzorca gear (pages/components/store/services/
composables/types/routes.ts/i18n):
- `family` — onboarding rodziny, członkowie, zaproszenia, plan.
- `shopping` — listy, pozycje, szybkie dodawanie, odhaczanie, offline cache.
- `recipes` — lista/edycja przepisów, import z linku (AI), „dodaj do listy".
- `search` — global search.

## Konwersja jednostek i sumowanie (rdzeń domenowy)

Kluczowa logika w `shopping.service` + `ingredients`:
1. Dodawana pozycja → dopasuj `ingredient_id` (po `name`/`aliases`).
2. Jeśli istnieje pozycja tego samego składnika: przelicz obie do `base_unit`
   przez `IngredientUnit` (`amount_in_base`), zsumuj, zapisz w jednostce
   prezentacji. Patrz [data-model.md](data-model.md).
3. Brak mapowania jednostki dla składnika → **pozycje osobne** (README sekcja 2).
4. „Dorzuć brakujące składniki" = dodaj z przepisu tylko to, czego nie ma
   (odhaczone/istniejące pomijane) — `POST /recipes/{id}/add-to-list?mode=missing`.

Seed `ingredients` + `IngredientUnit`: startowy zestaw popularnych składników z
konwersjami (szklanka/łyżka/łyżeczka → g/ml). AI może dosilać dataset.

## Fazy budowy

**Faza 0 — Bootstrap z boilerplate**
- Skopiuj gear-stack, rebranding (mapa wyżej), usuń moduł `gear` i zależności.
- Docker + baza + CLI wstają; auth/users/2FA/OAuth działają; frontend startuje
  z layoutami, i18n (PL+EN), PWA. Billing disabled.
- Kryterium: `docker compose up` + logowanie + pusty dashboard działają.

**Faza 1 — Family + limity**
- `tenants` → `family`; plan (`free/basic/pro`) + limit członków (feature_limits).
- Onboarding: nowa rodzina = domyślnie `free`; zaproszenia linkiem z egzekwowaniem
  limitu; „1 user = 1 rodzina".
- Kryterium: użytkownik zakłada rodzinę, zaprasza (limit działa), member dołącza.

**Faza 2 — Listy zakupów (bez konwersji)**
- Moduł `shopping`: wiele list, kategorie edytowalne, dodawanie/edycja/odhaczanie,
  szybkie dodawanie z tekstu, kolejność. Współdzielenie w rodzinie.
- Kryterium: pełny CRUD list i pozycji, odhaczanie, kategorie.

**Faza 3 — Ingredients + sumowanie/konwersja**
- Moduł `ingredients` + seed datasetu i `IngredientUnit`.
- Sumowanie pozycji przez mapę konwersji; brak mapowania → osobne.
- Kryterium: dwukrotne dodanie „szklanka mąki" + „130 g mąki" = jedna pozycja;
  „szklanka cukru" osobno od „szklanka mąki".

**Faza 4 — Przepisy**
- Moduł `recipes`: CRUD, kategorie (śniadania/obiady/kolacje/desery), tagi,
  składniki+porcje, `source_url`, upload zdjęcia (storage adapter).
- „Dodaj do listy" (all/missing).
- Kryterium: przepis z zdjęciem i składnikami; jednym klikiem na listę.

**Faza 5 — AI import przepisu z linku**
- Rozszerz `ai`: `POST /ai/recipes/import` (OpenRouter) → draft z rozpoznanymi
  składnikami/jednostkami, normalizacja, dopasowanie do datasetu.
- Kryterium: wklejenie linku → wypełniony formularz przepisu do potwierdzenia.

**Faza 6 — Offline / sync + search**
- PWA cache + kolejka lokalnych zmian; `sync/changes` + `sync/push`; rozstrzyganie
  konfliktów wg [sync-and-conflicts.md](sync-and-conflicts.md).
- Global search (prosty ILIKE), audit log (kto/kiedy).
- Kryterium: praca offline na liście, po reconnect dane się godzą bez utraty
  dodanych pozycji (merge), odhaczenia = last-write-wins.

## Testy i jakość

- Backend: pytest (integration na Postgres test DB, jak gear-stack), `black`,
  `mypy` przed commitem Pythona.
- Frontend: vitest; `pnpm type-check`, `pnpm lint`, `pnpm build` (regeneruje SW).
- Priorytet testów: konwersja/sumowanie jednostek (Faza 3), rozstrzyganie
  konfliktów (Faza 6), egzekwowanie limitów planu (Faza 1).

## Otwarte decyzje (do potwierdzenia przed/na etapie budowy)

- Prezentacja jednostki po zsumowaniu (jednostka pierwszej pozycji vs `base_unit`).
- Zakres seed datasetu składników na start (ile pozycji/konwersji).
- Delete vs. równoległa edycja — przyjęto LWW po `updated_at`/`deleted_at`
  (patrz sync-and-conflicts.md); potwierdzić.
