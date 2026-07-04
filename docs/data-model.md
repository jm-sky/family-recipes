# Model danych

Model danych dla MVP family-recipes. Backend: **FastAPI + SQLAlchemy + Postgres**.
Konwencje przeniesione z gear-stack (patrz [build-plan.md](build-plan.md)):
`id` jako `String(36)`/UUID, `created_at` / `updated_at` z `timezone=True`,
soft-delete przez `deleted_at` tam, gdzie potrzebny sync/tombstones.

## Diagram encji (poglądowy)

```
User ─┬─< FamilyMembership >─┬─ Family ─┬─< ShoppingList >──< ShoppingListItem
      │                      │          ├─< Category (shopping, editable)
      │                      │          ├─< Recipe >──< RecipeIngredient
      │                      │          ├─< Tag >──< RecipeTagLink
      │                      │          ├─< FamilyInvitation
      │                      │          └─< AuditLog
      └─ (owner_id) ─────────┘
Ingredient ─< IngredientUnit (base-unit conversion)
```

## Encje z boilerplate (gear-stack)

Przenoszone bez zmian domenowych (patrz build-plan): `User`, auth (sessions,
webauthn credentials, 2FA), `FeatureLimit`, billing (disabled). Poniżej tylko
encje domenowe family-recipes.

## Family (rodzina)

Odpowiednik `TenantDB` z gear-stack (rename tenant → family).

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | UUID |
| name | String(255) | |
| owner_id | FK users.id | twórca rodziny |
| plan | String(16) | `free` \| `basic` \| `pro`, domyślnie `free` |
| created_at | DateTime(tz) | |

- **1 użytkownik = 1 rodzina** (MVP): egzekwowane na poziomie serwisu —
  użytkownik może być w dokładnie jednej rodzinie.
- Limit członków wynika z `plan` (patrz feature limits / sekcja 12 README).

## FamilyMembership

Odpowiednik `TenantMembershipDB`.

| Pole | Typ | Uwagi |
|---|---|---|
| family_id | FK families.id PK | |
| user_id | FK users.id PK | |
| role | String(32) | `owner` \| `member` (równe uprawnienia w MVP) |
| created_at | DateTime(tz) | |

## FamilyInvitation

Zaproszenie linkiem; respektuje limit planu przy przyjęciu.

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| family_id | FK families.id | |
| token | String(64) unique index | trafia do linku zaproszenia |
| created_by | FK users.id | |
| expires_at | DateTime(tz) nullable | |
| accepted_at | DateTime(tz) nullable | |
| accepted_by | FK users.id nullable | |
| created_at | DateTime(tz) | |

## Category (kategoria listy zakupów)

Edytowalna przez użytkowników, per rodzina.

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| family_id | FK families.id | |
| name | String(128) | |
| icon | String(64) nullable | klucz ikony (jak `categoryIcons.ts` w gear-stack) |
| sort_order | Integer | |

## ShoppingList

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| family_id | FK families.id | |
| name | String(255) | np. „dom", „weekend" |
| created_by | FK users.id | |
| created_at | DateTime(tz) | |
| updated_at | DateTime(tz) | źródło last-write-wins |
| deleted_at | DateTime(tz) nullable | tombstone dla syncu |

## ShoppingListItem

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| list_id | FK shopping_lists.id | |
| name | String(255) | tekst składnika |
| category_id | FK categories.id nullable | |
| ingredient_id | FK ingredients.id nullable | ustawiane, gdy rozpoznano składnik z datasetu |
| quantity | Numeric(10,2) nullable | |
| unit | String(32) nullable | z predefiniowanej listy jednostek |
| is_checked | Boolean default false | kupione / niekupione |
| source_recipe_id | FK recipes.id nullable | skąd trafiło na listę |
| position | Integer | kolejność |
| created_by | FK users.id | |
| updated_at | DateTime(tz) | last-write-wins |
| deleted_at | DateTime(tz) nullable | tombstone |

- **Sumowanie pozycji** liczone w serwisie: ta sama para (`ingredient_id`
  **lub** znormalizowany `name`) sumuje się, przeliczając jednostki przez
  `IngredientUnit`. Brak mapowania jednostki → pozycje pozostają osobne
  (patrz README sekcja 2).

## Recipe (przepis)

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| family_id | FK families.id | |
| title | String(255) | |
| source_url | String(1024) nullable | link do pełnego opisu z krokami |
| image_path | String(512) nullable | storage adapter (jak gear-stack) |
| category | String(32) | `breakfast` \| `lunch` \| `dinner` \| `dessert` |
| servings | Integer nullable | liczba porcji |
| created_by | FK users.id | |
| created_at | DateTime(tz) | |
| updated_at | DateTime(tz) | |
| deleted_at | DateTime(tz) nullable | tombstone |

- **Brak kroków przygotowania w MVP** — kroki są pod `source_url`.

## RecipeIngredient

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| recipe_id | FK recipes.id | |
| name | String(255) | tekst składnika |
| ingredient_id | FK ingredients.id nullable | dopasowanie do datasetu |
| quantity | Numeric(10,2) nullable | |
| unit | String(32) nullable | predefiniowana jednostka |
| sort_order | Integer | |

## Tag / RecipeTagLink

| Tag | Typ | | RecipeTagLink | Typ |
|---|---|---|---|---|
| id | String(36) PK | | recipe_id | FK recipes.id PK |
| family_id | FK families.id | | tag_id | FK tags.id PK |
| name | String(64) | | | |

## Ingredient (dataset kanoniczny)

Zbiór składników globalny (seedowany, wzbogacany przez AI), używany do
sumowania i konwersji jednostek. Współdzielony między rodzinami (read-only dla
użytkowników w MVP).

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| name | String(255) unique | nazwa kanoniczna, np. „mąka pszenna" |
| aliases | JSONB | lista synonimów do dopasowania tekstu |
| base_unit | String(8) | `g` lub `ml` — jednostka bazowa do konwersji |

## IngredientUnit (mapa konwersji per składnik)

Realizuje **mapę konwersji zależną od składnika** (szklanka mąki ≠ szklanka
cukru — README sekcja 2).

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| ingredient_id | FK ingredients.id | |
| unit | String(32) | np. `szklanka`, `łyżka`, `szt` |
| amount_in_base | Numeric(12,4) | ile `base_unit` przypada na 1 `unit` (np. szklanka mąki = 130 g) |

- Konwersja: `value_in_base = quantity * amount_in_base`. Sumowanie liczy w
  `base_unit`, wynik prezentuje w preferowanej jednostce (domyślnie jednostka
  pierwszej pozycji lub `base_unit`).
- **Predefiniowana lista jednostek** (README sekcja 2) trzymana jako stała w
  kodzie (`UNITS`) + walidacja; nie wymaga własnej tabeli.

## AuditLog (minimalny)

| Pole | Typ | Uwagi |
|---|---|---|
| id | String(36) PK | |
| family_id | FK families.id | |
| entity_type | String(64) | np. `shopping_list_item`, `recipe` |
| entity_id | String(36) | |
| action | String(16) | `create` \| `update` \| `delete` |
| user_id | FK users.id | kto zmienił |
| created_at | DateTime(tz) | kiedy zmienił |

Zakres audytu = „kto/kiedy" (README sekcja 9); brak pełnego versioningu.
