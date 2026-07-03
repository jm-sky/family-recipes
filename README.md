# Aplikacja: Family-recipes

Poniżej pierwsza wersja product requirements dla MVP. Do weryfikacji i ustalenia szczegółów.

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
- Współdzielenie w rodzinie
- Offline support + cache
- Sync po powrocie online
- Konflikty danych:
  - podejście hybrydowe (zależnie od typu danych)
- Brak realtime sync w MVP
- Brak push notifications

---

## 3. Przepisy
- Własne przepisy
- Wspólne dla rodziny
- Kategorie (śniadania, obiady, kolacje, desery)
- Tagi
- Składniki + porcje (bez kroków w MVP)
- Import z linku (manualny)

---

## 4. AI (OpenRouter)
- Import przepisów z linków (główna funkcja AI)
- Rozpoznawanie składników i jednostek
- Normalizacja danych
- Architektura gotowa na rozszerzenia AI
- Sugestie posiłków:
  - „coś lekkiego”
  - „obiad 30 min”
  - „mam X składników”

---

## 5. Użytkownicy i rodzina
- Google OAuth (już istniejący boilerplate)
- 1 użytkownik = 1 rodzina
- Tworzenie rodziny + zaproszenia linkiem
- Wszyscy użytkownicy mają równe uprawnienia

---

## 6. Offline / Sync
- Backend jako source of truth (Postgres)
- Lokalny cache (offline-first częściowo)
- Pełny sync po reconnect
- Konflikty: hybrydowe podejście

---

## 7. Wyszukiwarka
- Global search (listy, przepisy, składniki)
- Na start prosta
- Możliwość rozbudowy do AI/semantycznej

---

## 8. Technologia
- Frontend: React + Tailwind
- Jedna baza kodu (web + Android)
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
