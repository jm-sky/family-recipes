# Wykonać zaplanowane review (security, code quality, UX, performance)

**Status:** `todo`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Context

W `docs/reviews/` są szablony do zapełnienia wynikami analiz. Każdy plik to **jedna dedykowana sesja AI** — należy przeprowadzić wszystkie zaplanowane review i uzupełnić sekcje **Findings** oraz **Follow-ups**.

## Symptoms

Brak ustrukturyzowanych wyników przeglądów po bootstrapie z gear-stack; ryzyko niewykrytych problemów security/UX w modułach domenowych (family, shopping, ingredients).

## Root cause

Projekt powstał jako kopia boilerplate'u — review program nie został jeszcze uruchomiony w kontekście domeny family-recipes.

## Suggested fix

1. Otwórz jeden plik review — **jedna sesja = jeden plik** (nie łączyć scope'ów).
2. Przed startem przeczytaj sekcję **Baseline** w pliku oraz [reviews/README.md](../reviews/README.md).
3. Przejdź checklistę; zapisuj wyniki w tabeli **Findings**.
4. Ustaw status w pliku review i w [reviews/README.md](../reviews/README.md) (`in progress` → `done`).
5. Dla actionable follow-upów dodaj wpisy w [issues/README.md](README.md).

### Zakres (7 sesji)

| # | Review | Scope | Plik | Status |
|---|--------|-------|------|--------|
| 1 | Security | Backend | [2026-07-06-security-backend.md](../reviews/2026-07-06-security-backend.md) | `planned` |
| 2 | Security | Frontend | [2026-07-06-security-frontend.md](../reviews/2026-07-06-security-frontend.md) | `planned` |
| 3 | Code quality | Backend | [2026-07-06-code-quality-backend.md](../reviews/2026-07-06-code-quality-backend.md) | `planned` |
| 4 | Code quality | Frontend | [2026-07-06-code-quality-frontend.md](../reviews/2026-07-06-code-quality-frontend.md) | `planned` |
| 5 | UX | Full stack (FE primary) | [2026-07-06-ux.md](../reviews/2026-07-06-ux.md) | `planned` |
| 6 | Performance | Backend | [2026-07-06-performance-backend.md](../reviews/2026-07-06-performance-backend.md) | `planned` |
| 7 | Performance | Frontend | [2026-07-06-performance-frontend.md](../reviews/2026-07-06-performance-frontend.md) | `planned` |

### Sugerowana kolejność

1. Security (backend, potem frontend)
2. Code quality (backend, frontend)
3. UX
4. Performance (backend, frontend)

## Files

- [docs/reviews/](../reviews/)
- [docs/issues/README.md](README.md)

## Related

- [build-plan.md](../build-plan.md) — fazy budowy MVP
- [data-model.md](../data-model.md) — model danych

## Follow-ups

Po ukończeniu programu: nowe actionable ustalenia → osobne pliki w `docs/issues/`.
