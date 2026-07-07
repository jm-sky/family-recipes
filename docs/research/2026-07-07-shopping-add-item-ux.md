# Research: UX dodawania produktów do listy zakupów

**Status:** `done`  
**Data:** 2026-07-07  
**Kontekst:** Faza 3 (ingredients + sumowanie) jest w toku; UI listy zakupów nadal opiera się na ręcznym wpisywaniu bez podpowiedzi.

## Cel

Zrozumieć, jak konkurencja (Domownik, Listonic) rozwiązuje szybkie dodawanie produktów z podpowiedziami, ikonami i kolorami kategorii — oraz co z tego ma sens w Family Recipes bez rozrostu scope’u MVP.

## Stan obecny (Family Recipes)

| Obszar | Stan |
|--------|------|
| Dodawanie pozycji | Formularz (nazwa + ilość + jednostka) + osobne pole „szybkie dodawanie z tekstu” |
| Autocomplete / podpowiedzi | **Brak** — zwykły `<Input>` |
| API składników | `GET /api/ingredients?q=` — **istnieje**, frontend **nie korzysta** |
| Dataset | ~50 składników kuchennych (seed) z aliasami i konwersjami jednostek |
| Kategorie | 9 domyślnych per rodzina (nabiał, pieczywo, napoje…) z kluczem ikony Lucide w DB |
| Ikony kategorii w UI | **Niewykorzystane** — `CategoryManager` i nagłówki grup pokazują tylko tekst |
| Auto-kategoryzacja | **Brak** — `quick_add` i dopasowanie składnika nie ustawiają `category_id` |
| Historia zakupów | Dane są w DB (`shopping_list_items`), brak endpointu sugestii |

Obecny ekran (`ShoppingListPage.vue`) wymaga od użytkownika znajomości nazwy produktu i ręcznego wyboru kategorii (ukryty pod „Dodaj kategorię”). To działa technicznie, ale jest wolne w sklepie / przy szybkim uzupełnianiu listy.

## Benchmark: Domownik

**Źródło:** opis w Google Play, doświadczenie użytkownika (referencja w rozmowie).

| Funkcja | Domownik | Family Recipes |
|---------|----------|----------------|
| Współdzielone listy rodzinne | tak | tak |
| Ilość + jednostka | tak | tak |
| Przenoszenie składników z przepisu | tak (premium: jadłospis) | planowane / częściowo w API |
| Podpowiedzi produktów + search | tak (wg użytkownika) | brak |
| Ikony / kolory kategorii przy dodawaniu | tak (wg użytkownika) | ikony w DB, brak w UI |
| Personalizacja koloru **listy** (nie kategorii) | tak | brak |
| Realtime sync | tak | poza MVP |

Domownik to szeroki „home organizer” (kalendarz, zadania, nagrody). Lista zakupów jest jednym z wielu modułów — nie jest źródłem prawdy dla logiki sumowania składników. Family Recipes ma przewagę w **dopasowaniu składników i konwersji jednostek**, ale przegrywa w **szybkości dodawania**.

## Benchmark: Listonic (najlepiej udokumentowany w PL)

[Listonic — Sugestie produktów](https://listonic.com/pl/funkcje/sugestie-produktow):

1. **Sugestie bez pisania** — popularne produkty widoczne od razu po otwarciu listy (chipy / szybkie tapnięcie).
2. **Autocomplete przy wpisywaniu** — katalog + dopasowanie do wpisywanego tekstu.
3. **Personalizacja** — historia zakupów + częstotliwość; nowy user dostaje zestaw popularny.
4. **Katalog wg kategorii sklepowych** — przeglądanie alejek (napoje, nabiał, pieczywo…).
5. **Auto-sortowanie wg kategorii** — lista w sklepie uporządkowana jak alejki.

Wnioski dla nas:
- „Zero-state suggestions” (puste pole → chipy) dają największy zysk UX przy małym nakładzie.
- Osobny katalog produktów to duży dataset (setki/tysiące pozycji) — na start wystarczy dataset składników + historia rodziny.
- Auto-kategoryzacja jest oczekiwana — użytkownik nie chce ręcznie przypisywać „mleko” do „Nabiał”.

## Luki techniczne do uwzględnienia w planie

1. **Wyszukiwanie składników** — `IngredientRepository.search` szuka tylko po `name`, nie po `aliases` (np. „mąki” nie znajdzie „mąka pszenna”).
2. **Brak mapowania składnik → kategoria zakupów** — dopasowany `ingredient_id` nie ustawia `category_id`.
3. **Ikony kategorii** — backend zapisuje klucze Lucide (`milk`, `croissant`…), frontend nie ma `categoryIcons.ts` (wzorzec istnieje w gear-stack).
4. **Dwa pola dodawania** (formularz + quick-add) — mylące; konkurencja ma jeden punkt wejścia.
5. **Dataset vs katalog** — seed to składniki kuchenne (mąka, jajko), nie pełny katalog sklepu (chleb, papier toaletowy, proszek do prania). Chemia/napoje są w kategoriach domyślnych, ale bez produktów-sugestii.

## Rekomendacja kierunku (wysoki poziom)

**Jeden unified „Dodaj produkt”** zamiast dwóch formularzy:

```
┌─────────────────────────────────────────┐
│ 🔍 Szukaj lub wpisz produkt…             │
├─────────────────────────────────────────┤
│ [Mleko] [Chleb] [Jajka] [Masło] …      │  ← popularne / ostatnie (chipy)
├─────────────────────────────────────────┤
│ 🥛 Nabiał    🥐 Pieczywo    🥤 Napoje   │  ← filtr kategorii (opcjonalnie v2)
│   mleko        —              woda      │
│   masło                                 │
└─────────────────────────────────────────┘
```

Po wyborze / Enter:
- nazwa wypełniona (kanoniczna z datasetu lub własna),
- `ingredient_id` ustawiony gdy match,
- `category_id` auto z mapy składnik→kategoria,
- opcjonalny krok: ilość + jednostka (sheet / inline, nie blokuje szybkiego tap).

**Wzorzec UI:** istniejący `ComboBox.vue` (Command + CommandInput) + slot na ikonę kategorii; wzorzec ikon z gear-stack `categoryIcons.ts`.

## Co świadomie odkładamy (poza scope)

- Pełny katalog sklepu (setki produktów branded) — osobna encja / import, nie rozszerzenie `Ingredient`.
- Głosowe dodawanie (Listonic) — faza późniejsza.
- Realtime podpowiedzi między urządzeniami — brak realtime w MVP.
- Kolory **list** (Domownik) — inna funkcja niż kolory kategorii produktów.

## Powiązane pliki w repo

- Frontend: `src/modules/shopping/pages/ShoppingListPage.vue`
- Backend kategorie: `backend/app/modules/shopping/constants.py` (`DEFAULT_CATEGORIES`)
- Backend składniki: `backend/app/modules/ingredients/`
- Wzorzec ikon: `gear-stack/src/modules/gear/utils/categoryIcons.ts`
- Komponent: `src/components/ui/combo-box/ComboBox.vue`

## Następny krok

Plan implementacji: [../plans/2026-07-07-shopping-product-suggestions.md](../plans/2026-07-07-shopping-product-suggestions.md).
