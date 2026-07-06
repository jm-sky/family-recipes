# Performance review — Frontend

**Status:** `planned`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Scope

Vue 3 frontend, build, PWA — moduły shopping (offline) i family.

## Baseline

- [sync-and-conflicts.md](../sync-and-conflicts.md) — offline cache i kolejka zmian
- [build-plan.md](../build-plan.md) — Faza 6 offline/sync

## Checklist

- [ ] Bundle size and code-splitting (route-level lazy imports)
- [ ] TanStack Query: `staleTime`, invalidation, duplicate fetches
- [ ] Image loading: lazy load, sizes (przepisy — gdy wdrożone)
- [ ] Large lists / tables (listy zakupów, virtualizacja jeśli potrzebna)
- [ ] PWA service worker cache strategy (`pwa.config.ts`)
- [ ] Re-renders in heavy pages (lista zakupów, pozycje)
- [ ] `localStorage` read/write on hot paths (offline queue)
- [ ] `pnpm build` output size po zmianach zależności

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
