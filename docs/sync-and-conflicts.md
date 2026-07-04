# Synchronizacja i konflikty danych

Strategia offline-first dla family-recipes. Backend (Postgres) jest **source of truth**;
klient trzyma lokalny cache i synchronizuje zmiany po powrocie online.

Brak realtime sync w MVP (bez WebSocket/SSE) — synchronizacja odbywa się przy
reconnect / odświeżeniu.

## Podejście hybrydowe

Strategia rozwiązywania konfliktów zależy od typu operacji:

| Operacja | Strategia | Uzasadnienie |
|---|---|---|
| Odhaczenie pozycji na liście (kupione / niekupione) | **Last-write-wins** | Stan binarny, ostatnia zmiana wygrywa |
| Dodawanie pozycji do listy / dodawanie przepisów | **Merge (append)** | Nic nie ginie — wszystkie dodane elementy zostają zachowane |
| Edycja tej samej pozycji (te same pola) | **Last-write-wins** | Ostatni zapis nadpisuje wcześniejszy |

## Zasady szczegółowe

- **Merge przy dodawaniu**: równoległe dodanie różnych pozycji przez dwóch członków
  rodziny skutkuje sumą obu zbiorów — żadna pozycja nie jest gubiona.
- **Sumowanie składników**: przy dodawaniu tego samego składnika (patrz README, sekcja 2)
  pozycje sumują się w jedną, przeliczając jednostki przez mapę konwersji per
  składnik (`IngredientUnit`, patrz [data-model.md](data-model.md)).
  - **Przy różnych, przeliczalnych jednostkach** — łączą się w jedną (konwersja do
    `base_unit`). **Brak mapowania jednostki dla składnika → pozycje osobne.**
- **Last-write-wins** rozstrzygane po **serwerowym `updated_at`** (nie zegar klienta),
  co eliminuje rozjazd zegarów. Klient wysyła zmiany; serwer stempluje `updated_at`
  i on jest arbitrem.

## Mechanizm (rozstrzygnięte)

- **Wykrywanie zmian od ostatniego synca**: kursor oparty o serwerowy `updated_at`
  (`GET /api/sync/changes?since=`). Usunięcia jako **tombstones** — rekord z
  `deleted_at` (soft-delete), nie fizyczne skasowanie, dopóki wszyscy klienci nie
  zsynchronizują.
- **Delete vs. równoległa edycja**: traktujemy delete jako update ustawiający
  `deleted_at`; wygrywa operacja z **późniejszym serwerowym znacznikiem** (LWW).
  Spójne z resztą — brak osobnej reguły „delete-wins/update-wins".
- **Źródło znacznika czasu**: wyłącznie serwer (`updated_at`/`deleted_at` z DB).

## Do doprecyzowania

- Prezentacja jednostki po zsumowaniu pozycji o różnych jednostkach (jednostka
  pierwszej pozycji vs. `base_unit`) — patrz build-plan „Otwarte decyzje".
