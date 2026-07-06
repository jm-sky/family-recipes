# Security review — Frontend

**Status:** `planned`  
**Created:** 2026-07-06  
**Updated:** 2026-07-06  

## Scope

Vue 3 frontend (`src/`) — moduły shared (auth, settings, admin) oraz domenowe (family, shopping, recipes).

## Baseline

- [build-plan.md](../build-plan.md) — moduły frontendowe i PWA
- [sync-and-conflicts.md](../sync-and-conflicts.md) — offline cache i lokalne dane
- pnpm `overrides` w `package.json` — transitive dependency fixes

## Checklist

- [ ] Token storage: `localStorage` vs in-memory / HttpOnly cookie strategy
- [ ] Auth interceptor and refresh flow (`auth.interceptor.ts`, token refresh store)
- [ ] XSS surfaces: `v-html`, markdown rendering, user-generated content
- [ ] CSP compatibility (inline scripts, third-party: Sentry, reCAPTCHA)
- [ ] WebAuthn / passkeys implementation
- [ ] API client: credentials, error handling, no secrets in client bundle
- [ ] Route guards: auth, admin, family onboarding edge cases
- [ ] Sensitive data in localStorage (shopping lists, settings, offline queue)
- [ ] Dependency audit (direct + transitive via `pnpm.overrides`)

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
