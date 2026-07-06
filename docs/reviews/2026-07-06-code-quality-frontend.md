# Code quality review — Frontend

**Status:** `planned`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Scope

Vue 3 frontend (`src/`) — moduły domenowe (family, shopping, recipes) i shared UI.

## Baseline

- [build-plan.md](../build-plan.md) — struktura modułów frontendowych
- Konwencje w `CLAUDE.md` — ESLint, TypeScript strict, i18n PL+EN

## Checklist

- [ ] Component size and responsibility (pages vs composables vs services)
- [ ] Pinia vs TanStack Query boundaries (server vs client state)
- [ ] ESLint / project conventions (`eslint.config.ts`, Perfectionist import sort)
- [ ] TypeScript strictness, typy w `types/` per moduł
- [ ] DRY: wspólne komponenty, route helpers, i18n keys
- [ ] Test coverage (`*.spec.ts`, vitest)
- [ ] Dead code po rebrandingu z gear-stack
- [ ] Shared UI (`src/shared/`, `src/components/ui/`) — spójność z boilerplate'em
- [ ] Moduł shopping: offline cache, optimistic updates

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
