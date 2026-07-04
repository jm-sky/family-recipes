# REST API

Publiczne REST API (README sekcja 8). Prefiks `/api`. Wszystkie endpointy
domenowe wymagają uwierzytelnienia (JWT z boilerplate) i są scope'owane do
rodziny bieżącego użytkownika (`CurrentUser` → membership → `family_id`).
Konwencje odpowiedzi/paginacji jak w gear-stack.

Endpointy auth / users / 2FA / billing pochodzą z boilerplate i nie są tu
powtarzane — patrz gear-stack.

## Family

| Metoda | Ścieżka | Opis |
|---|---|---|
| POST | `/api/families` | utwórz rodzinę (domyślnie plan `free`), twórca = owner |
| GET | `/api/families/me` | rodzina bieżącego użytkownika + plan + limit + liczba członków |
| GET | `/api/families/me/members` | lista członków |
| DELETE | `/api/families/me/members/{user_id}` | usuń członka (owner) |
| POST | `/api/families/me/invitations` | utwórz link zaproszenia (403 gdy limit planu osiągnięty) |
| GET | `/api/families/me/invitations` | aktywne zaproszenia |
| POST | `/api/invitations/{token}/accept` | przyjmij zaproszenie (waliduje limit planu i „1 user = 1 rodzina") |

## Categories (listy zakupów)

| Metoda | Ścieżka | Opis |
|---|---|---|
| GET | `/api/categories` | kategorie rodziny |
| POST | `/api/categories` | utwórz |
| PATCH | `/api/categories/{id}` | edytuj (name, icon, sort_order) |
| DELETE | `/api/categories/{id}` | usuń |

## Shopping lists

| Metoda | Ścieżka | Opis |
|---|---|---|
| GET | `/api/shopping-lists` | listy rodziny |
| POST | `/api/shopping-lists` | utwórz listę |
| GET | `/api/shopping-lists/{id}` | lista + pozycje |
| PATCH | `/api/shopping-lists/{id}` | zmień nazwę |
| DELETE | `/api/shopping-lists/{id}` | soft-delete (tombstone) |
| POST | `/api/shopping-lists/{id}/items` | dodaj pozycję (z sumowaniem — patrz niżej) |
| POST | `/api/shopping-lists/{id}/items/quick-add` | szybkie dodanie z tekstu (parsowanie kategoria/ilość/jednostka) |
| PATCH | `/api/shopping-lists/{id}/items/{item_id}` | edytuj / odhacz (`is_checked`) |
| DELETE | `/api/shopping-lists/{id}/items/{item_id}` | soft-delete pozycji |
| POST | `/api/shopping-lists/{id}/items/reorder` | batch zmiana kolejności |

- Przy dodawaniu pozycji serwis próbuje **zsumować** z istniejącą pozycją tego
  samego składnika (po `ingredient_id` lub znormalizowanej nazwie), przeliczając
  jednostki przez `IngredientUnit`. Brak mapowania → nowa, osobna pozycja.

## Recipes

| Metoda | Ścieżka | Opis |
|---|---|---|
| GET | `/api/recipes` | przepisy rodziny (filtry: `category`, `tag`, `q`) |
| POST | `/api/recipes` | utwórz przepis |
| GET | `/api/recipes/{id}` | przepis + składniki + tagi |
| PATCH | `/api/recipes/{id}` | edytuj |
| DELETE | `/api/recipes/{id}` | soft-delete |
| POST | `/api/recipes/{id}/image` | upload zdjęcia (storage adapter) |
| POST | `/api/recipes/{id}/add-to-list` | dodaj składniki przepisu do listy; `?mode=all\|missing` („dorzuć brakujące") |
| GET | `/api/tags` | tagi rodziny |
| POST | `/api/tags` | utwórz tag |

## AI (OpenRouter)

| Metoda | Ścieżka | Opis |
|---|---|---|
| POST | `/api/ai/recipes/import` | import przepisu z linku: `{ url }` → rozpoznane `{ title, ingredients[], servings, source_url }` (draft, nie zapisuje) |

- Import zwraca **draft** do potwierdzenia/edycji przez użytkownika przed
  zapisem (`POST /api/recipes`). Rozpoznawanie składników i jednostek +
  normalizacja + próba dopasowania do `Ingredient` datasetu.
- Architektura AI gotowa na Fazę 2 (sugestie posiłków — poza MVP).

## Search

| Metoda | Ścieżka | Opis |
|---|---|---|
| GET | `/api/search?q=` | global search: listy, przepisy, składniki (prosty ILIKE w MVP, rozszerzalne do semantycznego) |

## Sync

| Metoda | Ścieżka | Opis |
|---|---|---|
| GET | `/api/sync/changes?since={cursor}` | zmiany (create/update/delete) od kursora — dla offline reconcile |
| POST | `/api/sync/push` | batch lokalnych zmian; serwer rozstrzyga konflikty (patrz [sync-and-conflicts.md](sync-and-conflicts.md)) |

- `since` = kursor oparty o `updated_at` serwera. Usunięcia widoczne jako
  rekordy z `deleted_at` (tombstones).
