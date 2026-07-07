# Plan: Podpowiedzi produktów przy dodawaniu do listy

**Status:** `planned`  
**Data:** 2026-07-07  
**Research:** [../research/2026-07-07-shopping-add-item-ux.md](../research/2026-07-07-shopping-add-item-ux.md)

## Cel produktowy

Skrócić dodawanie pozycji do listy zakupów do 1–2 tapnięć dla typowych produktów, z wizualnym rozróżnieniem kategorii (ikony, kolory), bez utraty możliwości wpisania dowolnej nazwy.

## Zasady

- **Offline-friendly:** podpowiedzi z cache (ingredients + ostatnie pozycje rodziny); search działa lokalnie gdy dataset jest mały.
- **Nie psuj sumowania:** wybór z podpowiedzi = kanoniczna nazwa + `ingredient_id` (już obsługiwane w `_add_or_merge`).
- **Własne nazwy zawsze dozwolone** — jak Listonic: „dodaj własny produkt” gdy brak w katalogu.
- **Minimalny diff:** wykorzystać istniejące API i komponenty (`ComboBox`, Lucide).

---

## Faza A — Fundament (backend, ~0.5–1 dzień)

### A1. Poprawka wyszukiwania składników

- Rozszerzyć `IngredientRepository.search` o dopasowanie w `aliases` (JSONB).
- Dodać ranking: exact name > prefix name > alias match.
- Limit wyników: 15–20 (już jest `limit=20`).

### A2. Mapowanie składnik → kategoria zakupów

Dodać pole opcjonalne w seedzie składników, np. `shopping_category_key`:

```python
# Klucze zgodne z DEFAULT_CATEGORIES (constants.py)
SHOPPING_CATEGORY_KEYS = (
    "produce", "dairy", "bakery", "meat", "dry", "drinks", "frozen", "household", "other"
)
```

W seed_data przypisać każdy składnik do jednej kategorii (np. `mleko` → `dairy`, `jabłko` → `produce`).

**Mapowanie na `category_id` rodziny:** w `ShoppingService._add_or_merge`, gdy `category_id is None` i jest `ingredient_id`:
1. Pobrać `shopping_category_key` składnika.
2. Znaleźć kategorię rodziny po `icon` lub zmapowanym `sort_order` / stałej nazwie domyślnej.

Alternatywa bez migracji DB: statyczna mapa `ingredient_name_prefix → icon_key` w `constants.py` (szybsze na MVP, gorsze na rozbudowę).

**Decyzja rekomendowana:** kolumna `shopping_category_key` w `ingredients` (nullable) — jedno źródło prawdy, łatwe dla AI enrichment później.

### A3. Endpoint sugestii (opcjonalny, ale czystszy)

`GET /api/shopping-lists/suggestions?q=&limit=`

Zwraca zunifikowaną listę:

```json
{
  "suggestions": [
    {
      "name": "mleko",
      "ingredientId": "...",
      "categoryId": "...",
      "categoryIcon": "milk",
      "source": "ingredient" | "recent" | "popular"
    }
  ]
}
```

Źródła (priorytet):
1. Ostatnie unikalne nazwy z list rodziny (ostatnie 90 dni, max 10).
2. Dopasowanie do `ingredients` (+ aliasy).
3. Stała lista „popularnych” (top 15 z seedu) gdy brak historii.

Jeśli wolimy mniejszy diff: frontend składa to z `GET /ingredients` + lokalnej historii z cache list — bez nowego endpointu w Fazie B.

---

## Faza B — UI v1: autocomplete + chipy (~1–2 dni)

### B1. Komponent `ProductAddPanel`

Nowy komponent w `src/modules/shopping/components/`:

| Element | Zachowanie |
|---------|------------|
| Pole search | `CommandInput` / combobox; debounce 200 ms → `GET /ingredients?q=` |
| Lista wyników | Nazwa + mała ikona kategorii (kolor tła chip) |
| Chipy pod polem | Gdy puste: „Popularne” (15 pozycji); gdy historia: „Ostatnie” |
| Tap na chip / wynik | `addItem({ name, ingredientId?, categoryId? })` — ilość opcjonalna |
| Enter na własnym tekście | Dodaj jak dziś (nazwa free-text) |
| Ilość / jednostka | Collapsible „Więcej opcji” lub inline po dodaniu (edycja pozycji) — **nie** blokuje szybkiego dodania |

Zastąpić obecny dual-form (structured + quick-add) jednym panelem. Quick-add parser (`2 kg mąki`) zostaje jako **ukryta supermoc**: jeśli wpis zawiera liczbę + jednostkę, parsuj przed dodaniem (reuse `quickAdd` API lub ten sam parser po stronie klienta).

### B2. Ikony i kolory kategorii

- `src/modules/shopping/utils/categoryIcons.ts` — mapa klucz Lucide → komponent (wzorzec gear-stack).
- `src/modules/shopping/utils/categoryColors.ts` — mapa klucz → Tailwind token tła/tekstu (np. `dairy` → `bg-sky-100 text-sky-800`).
- `CategoryIcon.vue` — mały wrapper.
- Użyć w: `ProductAddPanel`, nagłówkach grup na liście, `CategoryManager` (podgląd ikony).

### B3. Nagłówki grup na liście

W `ShoppingListPage.vue` zamiast samego tekstu:

```
[🥛] NABIAŁ
  ☐ mleko  1 l
```

Kategoria bez ikony w DB → fallback `shopping-basket`.

---

## Faza C — Personalizacja (~1 dzień)

### C1. Historia rodziny

- Backend: query po `shopping_list_items` dla `family_id`, `deleted_at IS NULL`, group by znormalizowana nazwa, order by `max(updated_at)`.
- Cache TanStack Query: `shoppingSuggestionKeys.recent(familyId)`.
- Chipy „Ostatnie” nad popularnymi.

### C2. Auto-kategoryzacja przy quick-add

Gdy `quick_add` / `add_item` bez `categoryId` i match ingredient → ustaw `category_id` (Faza A2).

### C3. Rozszerzenie datasetu (light)

Dodać do seedu ~20 pozycji „sklepowych” bez konwersji (chleb, masło extra, papier toaletowy…) z `shopping_category_key`, opcjonalnie bez `IngredientUnit` — nadal przydatne jako sugestie, sumowanie po nazwie.

---

## Faza D — Katalog wg kategorii (opcjonalnie, po feedbacku)

- Bottom sheet / drawer: siatka kategorii (ikona + kolor + nazwa).
- Po tapnięciu kategorii: lista produktów z tej kategorii (filtrowane ingredients).
- Search globalny nad katalogiem.

To odpowiada Listonic „Katalog produktów” — większy UI, ale ten sam backend co Faza B.

---

## Model danych (propozycja migracji)

```sql
ALTER TABLE ingredients ADD COLUMN shopping_category_key VARCHAR(32) NULL;
-- opcjonalnie później:
-- ALTER TABLE categories ADD COLUMN color_key VARCHAR(32) NULL;
```

Kolory na start **tylko w frontendzie** (mapa po `icon`), bez kolumny w DB — mniej migracji.

---

## Kryteria akceptacji

### Faza B (MVP UX)

- [ ] Użytkownik dodaje „mleko” jednym tapnięciem z podpowiedzi.
- [ ] Wpisanie „mąk” pokazuje „mąka pszenna” (aliasy działają).
- [ ] Pozycja trafia do grupy „Nabiał” z ikoną bez ręcznego wyboru kategorii.
- [ ] Własna nazwa spoza katalogu nadal działa (Enter).
- [ ] Nagłówki grup na liście mają ikony kategorii.
- [ ] PL + EN w i18n.

### Faza C

- [ ] Po kilku zakupach chipy „Ostatnie” pokazują produkty rodziny.
- [ ] Quick-add „2 kg mąki” nadal parsuje ilość i sumuje.

### Testy

- Backend: test search po aliasach; test auto-category w `add_item` / `quick_add`.
- Frontend: unit test `categoryIcons`; opcjonalnie e2e Playwright — dodanie z podpowiedzi.

---

## Szacunek nakładu

| Faza | Nakład | Zależności |
|------|--------|------------|
| A | 0.5–1 d | — |
| B | 1–2 d | A (min. A1 + A2) |
| C | ~1 d | B |
| D | 1–2 d | B, większy dataset |

**Rekomendacja:** zacząć od **A + B** jako jeden PR UX; C w kolejnym.

---

## Ryzyka

| Ryzyko | Mitygacja |
|--------|-----------|
| Rodzina zmieniła nazwy kategorii | Mapowanie po `icon` (stabilny klucz), nie po `name` |
| Za mało produktów w seedzie | Chipy + historia; stopniowe rozszerzanie seedu |
| Dwa flow dodawania mylą użytkownika | Usunąć widoczny dual-form w B1 |
| Offline | Cache ingredients w TanStack / service worker przy sync fazie 6 |

---

## Poza scope tego planu

- Pełny katalog marek / EAN
- Głosowe dodawanie
- Reklamy / sponsored suggestions (Listonic)
- Kolory całej listy (Domownik)
