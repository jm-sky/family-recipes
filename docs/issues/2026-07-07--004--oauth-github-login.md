# OAuth GitHub — logowanie przez GitHub

**Status:** `done`  
**Created:** 2026-07-07  
**Moduł:** `auth` (shared core)  
**Source:** [gear-stack #014](../../gear-stack/docs/issues/2026-07-07--014--oauth-github-login.md) · [AI-workspace](../../AI-workspace)

## Problem

Brak logowania przez GitHub OAuth — tylko Google i Facebook. AI-workspace ma już pełną implementację.

## Zakres (backport)

- [x] Backend: `GitHubOAuthProvider`, `GITHUB_OAUTH_*`
- [x] Frontend: `OAuthGitHubButton`, trasa `/auth/github`, `useOAuth.ts`
- [x] `LoginForm.vue`, `RegisterForm.vue`

## Weryfikacja

Po ustawieniu `GITHUB_OAUTH_*` i `VITE_GITHUB_OAUTH_CLIENT_ID` — login przez GitHub na `/auth/login`.
