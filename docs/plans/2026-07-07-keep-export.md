# Plan: Eksport list zakupów do Google Keep (Gmail)

**Status:** `planned`  
**Data:** 2026-07-07  
**Kontekst:** Użytkownik korzysta z Google Keep, żona z Domownika; Family Recipes jest hubem rodziny. Potrzebny **jednokierunkowy** sync listy zakupów **Family → Keep** (lustro osobiste), bez ręcznego kopiowania.

## Cel produktowy

Wybrana lista zakupów w aplikacji automatycznie pojawia się jako checklista w Google Keep użytkownika, który włączył integrację. Zmiany w rodzinnej liście (dodanie, edycja, odhaczenie, usunięcie) są odzwierciedlane w Keep.

**Poza scope:** import z Keep, sync z Domownikiem, sync przepisów, dwukierunkowe odhaczanie z Keep.

## Ograniczenia platformy (Gmail)

| Ścieżka | Gmail | Uwagi |
|---------|-------|-------|
| Oficjalne Keep API (`keep.googleapis.com`) | **nie** | Tylko Google Workspace Enterprise |
| **gkeepapi** (nieoficjalny protokół mobilny) | **tak** | Reverse-engineered; może się zepsuć bez ostrzeżenia |
| Istniejące OAuth logowania (auth) | **nie wystarczy** | Inny produkt; brak scope Keep na Gmail |

**Decyzja:** integracja oparta o **gkeepapi** + **gpsoauth** (master token), za feature flagą `KEEP_SYNC_ENABLED=false` domyślnie.

## Zasady

- **Family Recipes = source of truth** — push tylko w kierunku Keep.
- **Per user** — każdy członek rodziny może podłączyć własne Keep; lustro jest osobiste, nie współdzielone w Google.
- **Jedna lista FR ↔ jedna notatka Keep** (checklista).
- **Odhaczenia w Keep** nie aktualizują aplikacji (MVP); kolejny push nadpisuje stan z Family.
- **Tokeny wrażliwe** — master token szyfrowany at-rest (wzorzec `encrypt_token` z modułu AI).
- **Minimalny diff** — osobny moduł `integrations`, bez mieszania z Fazą 6 (offline PWA).

---

## Architektura

```
┌─────────────────────────────────────────────────────────┐
│ Family Recipes (Postgres)                                │
│  ShoppingList ──< ShoppingListItem                        │
│       ▲                                                  │
│       │ push (1-way)                                     │
│  KeepListMirror (user_id, shopping_list_id, keep_note_id)│
└───────┼─────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ Google Keep (konto użytkownika, via gkeepapi)           │
│  Note + CheckItems: "mleko 1 l" ☑/☐                     │
└─────────────────────────────────────────────────────────┘
```

### Moduł backend

```
backend/app/modules/integrations/
  __init__.py
  db_models.py          # KeepConnectionDB, KeepListMirrorDB
  schemas.py
  repository.py
  keep_client.py        # wrapper gkeepapi (authenticate, sync, CRUD note)
  keep_sync_service.py  # mapowanie FR list → Keep checklist
  router.py             # REST pod /api/integrations/keep
```

### Zależności Python

```
gkeepapi>=0.15
gpsoauth>=1.0
```

Dodać do `backend/requirements.txt`; rebuild obrazu `backend:dev` po merge.

---

## Model danych (migracja)

### `keep_connections`

| Pole | Typ | Uwagi |
|------|-----|-------|
| id | String(36) PK | UUID |
| user_id | FK users.id unique | jedno połączenie Keep per user |
| google_email | String(255) | email konta Keep |
| encrypted_master_token | Text | Fernet |
| device_id | String(64) | wymagany przez gkeepapi |
| created_at / updated_at | DateTime(tz) | |
| last_sync_at | DateTime(tz) nullable | |
| last_error | Text nullable | ostatni błąd sync (do UI) |

### `keep_list_mirrors`

| Pole | Typ | Uwagi |
|------|-----|-------|
| id | String(36) PK | |
| user_id | FK users.id | |
| shopping_list_id | FK shopping_lists.id | |
| keep_note_id | String(128) | ID notatki w Keep |
| auto_sync | Boolean | domyślnie `true` |
| last_pushed_at | DateTime(tz) nullable | |
| created_at | DateTime(tz) | |

Unique: `(user_id, shopping_list_id)`.

---

## Mapowanie danych

| Family Recipes | Google Keep |
|----------------|-------------|
| `ShoppingList.name` | tytuł notatki (`"Zakupy: Dom"`) |
| `ShoppingListItem` | element checklisty |
| `name` + opcjonalnie `quantity` + `unit` | tekst: `"mleko"`, `"mleko 1 l"`, `"mąka 2 szklanki"` |
| `is_checked` | `checked` na elemencie |
| `deleted_at` / brak w liście | usunięcie elementu przy full push |
| `sort_order` | kolejność elementów (jeśli API wspiera; inaczej alfabetycznie) |

**Strategia sync (MVP):** **full push** — przy każdym syncu przebudowa checklisty w istniejącej notatce (prostsze niż diff po `keep_item_id`). Przy pierwszym powiązaniu: utworzenie nowej notatki checklisty.

Format linii (helper `_format_item_line`):

```python
def format_item_line(name: str, quantity: float | None, unit: str | None) -> str:
    if quantity is None and not unit:
        return name.strip()
    parts = [name.strip()]
    if quantity is not None:
        parts.append(str(quantity).rstrip("0").rstrip("."))
    if unit:
        parts.append(unit)
    return " ".join(parts)
```

---

## API

Prefix: `/api/integrations/keep` (wymaga auth JWT).

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/status` | `{ connected, googleEmail, lastSyncAt, lastError }` |
| POST | `/connect` | `{ email, masterToken, deviceId? }` — zapis zaszyfrowanego tokenu |
| DELETE | `/disconnect` | usuwa connection + mirrors (nie usuwa notatek w Keep) |
| GET | `/mirrors` | lista powiązań usera |
| POST | `/mirrors` | `{ shoppingListId, createNewNote?: true }` — tworzy mirror + pierwszy push |
| DELETE | `/mirrors/{id}` | usuwa powiązanie (notatka w Keep zostaje) |
| PATCH | `/mirrors/{id}` | `{ autoSync: bool }` |
| POST | `/mirrors/{id}/sync` | ręczny push teraz |
| POST | `/sync-all` | push wszystkich mirrorów z `auto_sync=true` |

Wszystkie endpointy za `Depends(require_keep_sync_enabled)` gdy `KEEP_SYNC_ENABLED=false` → 503.

---

## Flow połączenia konta (UX)

Master token **nie** pochodzi z normalnego OAuth logowania. Jednorazowy flow w ustawieniach:

1. **Ustawienia → Integracje → Google Keep**
2. Krótka instrukcja PL/EN (link do pomocy):
   - zaloguj się na konto Google w przeglądarce
   - skopiuj `oauth_token` z cookies (DevTools → Application) **lub** użyj helpera CLI `cli.py integrations keep token` (opcjonalnie Faza B)
   - wklej w formularz → backend wymienia na master token (`gpsoauth`) i szyfruje
3. Komunikat: *„Token daje dostęp do Keep — możesz go cofnąć w [myaccount.google.com/permissions](https://myaccount.google.com/permissions)”*
4. Checkbox: *„Rozumiem, że to nieoficjalna integracja — może przestać działać po zmianach Google”*

**Faza B (opcjonalnie):** skrypt CLI / osobna strona pomocy z krokami; bez embedded browser w MVP.

---

## UI (frontend)

Moduł: `src/modules/integrations/` (lub sekcja w `settings`).

| Ekran / element | Zachowanie |
|-----------------|------------|
| `SettingsIntegrationsPage` | status połączenia, connect/disconnect |
| Na `ShoppingListPage` | menu listy: „Sync z Google Keep” (gdy connected) |
| Dialog powiązania | wybór: nowa notatka vs istniejąca (MVP: tylko nowa) |
| Badge statusu | „Zsynchronizowano 2 min temu” / błąd |
| Toggle `autoSync` | włącz/wyłącz automatyczny push |

i18n: PL + EN.

Feature flag frontend: `VITE_ENABLE_KEEP_SYNC` (domyślnie `false`).

---

## Automatyczny push (Faza C)

Po ręcznym sync (Faza A) — hooki w `ShoppingService`:

1. Po `add_item`, `update_item`, `delete_item`, `quick_add`, `reorder` → enqueue job `keep_sync.push_mirror(user_ids_with_auto_sync, list_id)`
2. Worker (Redis + prosty consumer lub APScheduler w kontenerze app):
   - debounce 30 s per `(user_id, shopping_list_id)` — unikamy bursty przy wielu zmianach
   - wywołanie `KeepSyncService.push_list(user_id, shopping_list_id)`

**Alternatywa MVP bez workera:** tylko ręczny przycisk „Sync teraz” + cron co 5 min (`sync-all` dla aktywnych mirrorów). Rekomendacja: zacząć od ręcznego, dodać worker w Fazie C.

---

## Konfiguracja (.env)

```bash
# Backend
KEEP_SYNC_ENABLED=false

# Frontend
VITE_ENABLE_KEEP_SYNC=false
```

Opcjonalnie współdzielony klucz szyfrowania z AI (`AI_TOKEN_ENCRYPTION_KEY`) lub osobny `KEEP_TOKEN_ENCRYPTION_KEY`.

---

## Fazy implementacji

| Faza | Zakres | Nakład | Status |
|------|--------|--------|--------|
| **A — Fundament** | migracja, `keep_client`, connect/disconnect, mirror + ręczny push, testy mock | 1.5–2 d | `todo` |
| **B — UI** | settings connect, mirror na liście, status sync, i18n | 1 d | `todo` |
| **C — Auto-sync** | hooki shopping + debounced worker | 1 d | `todo` |
| **D — Polish** | CLI helper tokenu, lepsze błędy, retry | 0.5 d | `todo` |

**Rekomendacja:** jeden PR dla A+B (używalne end-to-end), C w kolejnym.

---

## Kryteria akceptacji

### Faza A+B (MVP)

- [ ] Użytkownik z Gmail łączy Keep (master token), widzi status „Połączono”.
- [ ] Z listy „Dom” tworzy mirror → w Keep pojawia się notatka z checklistą.
- [ ] Dodanie pozycji w aplikacji + „Sync teraz” → nowa linia w Keep.
- [ ] Odhaczenie w aplikacji → po sync pozycja odhaczona w Keep.
- [ ] Usunięcie pozycji w aplikacji → znika z Keep po sync.
- [ ] Odhaczenie **tylko w Keep** — po sync wraca stan z aplikacji (udokumentowane w UI).
- [ ] `KEEP_SYNC_ENABLED=false` — brak endpointów / ukryty UI.
- [ ] Token zaszyfrowany w DB; disconnect czyści dane.
- [ ] PL + EN.

### Testy

- [ ] Unit: `format_item_line`, mapowanie items → checklist lines.
- [ ] Unit: `KeepSyncService.push_list` z mock `keep_client`.
- [ ] Integration (opcjonalnie): connect z mockiem gkeepapi — bez prawdziwego Google w CI.

---

## Ryzyka i mitygacja

| Ryzyko | Mitygacja |
|--------|-----------|
| Google zmieni protokół Keep | feature flag; `last_error` w UI; monitoring logów |
| Master token = wysokie uprawnienia | szyfrowanie, disconnect, link revoke w pomocy |
| App verification Google | nie używamy oficjalnego scope Keep OAuth na produkcji |
| Konflikt z żoną na Domowniku | poza scope; FR pozostaje hubem rodziny |
| Full push kasuje ręczne edycje w Keep | jednokierunkowość + komunikat w UI |
| gkeepapi nieaktywny / bug | pin wersji; test przed release; fallback „sync ręczny” |

---

## Powiązane dokumenty

- [../sync-and-conflicts.md](../sync-and-conflicts.md) — wewnętrzny offline sync (Faza 6), **osobny** temat
- [../build-plan.md](../build-plan.md) — Faza 6
- [2026-07-07-shopping-product-suggestions.md](2026-07-07-shopping-product-suggestions.md) — UX list zakupów

## Poza scope

- Import Keep → Family
- Dwukierunkowy sync odhaczeń
- Integracja Domownik
- Sync przepisów
- Oficjalne Keep API (Workspace)
- Google Tasks jako zamiennik Keep
