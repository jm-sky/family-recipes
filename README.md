# Aplikacja: Family-recipes

Product requirements dla MVP. Sekcje oznaczone **(potwierdzone)** zostały zatwierdzone w rozmowie. Punkty oznaczone **(do potwierdzenia)** czekają na decyzję.

---

## 0. Wspólny core z gear-stack (boilerplate)

Family-recipes współdzieli wspólny core z projektem **gear-stack** (https://github.com/jm-sky/gear-stack), traktowanym jako boilerplate: kod, wzorce (patterns), dobre praktyki, sposób pisania changelogów itd. **(potwierdzone)**

Z gear-stack przenosimy (dokładny zakres do ustalenia w trakcie):
- Docker Compose infrastructure (backend + baza danych)
- Backend CLI (zarządzanie bazą, użytkownikami itd.)
- Users / auth (email+hasło, WebAuthn/passkeys, JWT)
- OAuth (Google)
- 2FA
- Płatności / subskrypcje (billing) — istnieją w gear-stack; na start **disabled** (feature flag), patrz sekcja 12
- Integrację z OpenRouter (AI)
- Konfigurację linterów i narzędzi jakości kodu
- Frontend Vue 3: layouty, komponenty (shadcn-vue / reka-ui), rejestr i18n, konfiguracja PWA, setup TanStack Query, stores/patterns

Proces tworzenia nowej aplikacji na bazie tego core'u:
1. Skopiuj całość z gear-stack
2. Usuń rzeczy niepotrzebne w nowej domenie
3. Podmień fragmenty i słowa kluczowe specyficzne dla gear-stack
4. Dodaj logikę specyficzną dla domeny jako nowy moduł w `modules/`

---

## 1. Zakres MVP
- Lista zakupów + przepisy
- System rodzinny (multi-user)

---

## 2. Lista zakupów
- Wiele list (np. dom, weekend itd.)
- Kategorie (edytowalne przez użytkowników)
- Szybkie dodawanie (tekst)
- Strukturalizacja (kategoria, ilość, jednostka)
- Jednostki: **predefiniowana lista** (g, kg, ml, l, szt., szklanka, łyżka…) **(potwierdzone)**
- Odhaczanie pozycji (kupione / niekupione) **(potwierdzone)**
- Dodawanie składników z przepisu do listy jednym kliknięciem, w tym „dorzuć brakujące składniki" **(potwierdzone)**
- Sumowanie pozycji: ten sam składnik dodany wielokrotnie sumuje się w jedną pozycję **(potwierdzone)**
  - Sumowanie korzysta z **mapy konwersji jednostek zależnej od składnika** (np. szklanka mąki = N g mąki; szklanka mąki ≠ szklanka cukru) — pozycje o różnych, ale przeliczalnych jednostkach lączą się w jedną **(potwierdzone)**
  - Wymaga zbioru konwersji per składnik (dataset do zbudowania; AI może pomóc go zasilić). **Gdy brak mapowania — pozycje pozostają osobne** **(potwierdzone)**
- Współdzielenie w rodzinie
- Offline support + cache
- Sync po powrocie online
- Konflikty danych: podejście hybrydowe — szczegóły w [docs/sync-and-conflicts.md](docs/sync-and-conflicts.md)
- Brak realtime sync w MVP
- Brak push notifications

---

## 3. Przepisy
- Własne przepisy
- Wspólne dla rodziny
- Kategorie (śniadania, obiady, kolacje, desery)
- Tagi
- Składniki + porcje
- **Bez kroków przygotowania w MVP** — przepis zawiera **link do źródła**, gdzie znajduje się pełny opis z krokami **(potwierdzone)**
- Zdjęcie przepisu (wymaga storage plików — w gear-stack jest storage adapter) **(potwierdzone)**
- Import z linku (manualny + wspomagany AI, patrz sekcja 4)

---

## 4. AI (OpenRouter)
- **Import przepisów z linków — główna i jedyna pewna funkcja AI w MVP** **(potwierdzone)**
  - Rozpoznawanie składników i jednostek
  - Normalizacja danych
- Architektura gotowa na rozszerzenia AI
- **Faza 2** (poza MVP): sugestie posiłków
  - „coś lekkiego"
  - „obiad 30 min"
  - „mam X składników"

---

## 5. Użytkownicy i rodzina
- Auth: **Google OAuth + email/hasło + WebAuthn/passkeys + 2FA** (wszystko z boilerplate) **(potwierdzone)**
- **1 użytkownik = 1 rodzina**, bez przełączania między rodzinami **(potwierdzone)**
- Opuszczenie / zmiana rodziny — poza zakresem MVP **(potwierdzone)**
- Tworzenie rodziny + zaproszenia linkiem (liczba członków ograniczona planem — patrz sekcja 12)
- Wszyscy użytkownicy mają równe uprawnienia

---

## 6. Offline / Sync
- Backend jako source of truth (Postgres)
- Lokalny cache (offline-first częściowo)
- Pełny sync po reconnect
- Konflikty: podejście hybrydowe — szczegóły w [docs/sync-and-conflicts.md](docs/sync-and-conflicts.md)

---

## 7. Wyszukiwarka
- Global search (listy, przepisy, składniki)
- Na start prosta
- Możliwość rozbudowy do AI/semantycznej

---

## 8. Technologia
- Frontend: **Vue 3 + Tailwind** (shadcn-vue / reka-ui) — jak gear-stack **(potwierdzone)**
- **PWA** (vite-plugin-pwa) — instalowalna aplikacja z offline **(potwierdzone)**
- Jedna baza kodu web + Android:
  - MVP: PWA (Android = zainstalowana PWA) **(potwierdzone)**
  - W razie potrzeby natywnych funkcji Androida: opakowanie tej samej bazy w Capacitor (bez przepisywania)
- Backend: FastAPI
- DB: Postgres
- Docker (całość środowiska)
- Publiczne REST API

---

## 9. Architektura danych
- Brak pełnego versioning UI
- Minimalny audit log:
  - kto zmienił
  - kiedy zmienił

---

## 10. i18n
- Od początku pełne wsparcie i18n
- PL + EN na start

---

## 11. Notyfikacje i realtime
- Brak push notifications w MVP
- Brak realtime (WebSocket/SSE) w MVP

---

## 12. Plany i limity (tiers)

Limit dotyczy liczby członków rodziny: **(potwierdzone)**

| Plan | Limit członków rodziny |
|---|---|
| Free | 2 osoby |
| Basic | 5 osób |
| Pro | bez limitu |

- Zaproszenia linkiem respektują limit planu.
- Każda nowa rodzina startuje domyślnie na planie **Free**, z egzekwowanymi limitami **(potwierdzone)**
- **Płatności / billing**: moduł pochodzi z gear-stack (boilerplate). Na start **disabled** (feature flag) — włączany później. Przy wyłączonym billingu plany można nadawać ręcznie. **(potwierdzone)**

---
