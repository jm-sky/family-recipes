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
  pozycje sumują się w jedną, o ile jednostka się zgadza.
  - *(do potwierdzenia)* zachowanie przy różnych jednostkach.
- **Last-write-wins** wymaga znacznika czasu / wersji na rekordzie (do doprecyzowania
  na etapie modelu danych: `updated_at` po stronie serwera vs. zegar klienta).

## Do doprecyzowania

- Mechanizm wykrywania zmian od ostatniego synca (np. `updated_at` / cursor / tombstones
  dla usunięć).
- Usuwanie pozycji vs. równoległa edycja (delete vs. update) — którą stronę preferujemy.
- Źródło znacznika czasu dla last-write-wins (serwer vs. klient) i tolerancja rozjazdu zegarów.
