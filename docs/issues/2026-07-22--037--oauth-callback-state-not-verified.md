# OAuth callback does not verify the CSRF `state` server-side (037)

**Status:** `verification needed`
**Created:** 2026-07-22
**Severity:** Medium
**Module:** `auth` / `core.oauth` (backend — OAuth)
**Source:** Backport from [gear-stack issue 037](../../../gear-stack/docs/issues/2026-07-21--037--oauth-callback-state-not-verified.md)

## Problem

The OAuth flow generates a `state` parameter server-side and returns it to the client from `POST /api/auth/oauth/auth-url`. The callback handler never verified `state` — only the frontend compared it (in `sessionStorage`). The backend kept no record of issued state.

## Resolution (2026-07-22)

Backported from gear-stack:

- Added `OAuthStateStore` (`backend/app/core/oauth_state_store.py`) — Redis-backed, single-use, TTL'd store bound to provider.
- `POST /oauth/auth-url` persists state; `POST /oauth/callback/{provider}` requires and consumes it (400 on missing/expired/reused/mismatched).

## Scope

- [x] `backend/app/core/oauth_state_store.py` (new)
- [x] `backend/app/modules/auth/router.py` — store/consume state
- [x] Tests: `backend/tests/test_oauth_state_store.py`

## Verification

1. Normal state consumption succeeds — `test_normal_login_state_is_valid`.
2. Replayed state rejected — `test_replayed_state_is_rejected`.
3. Never-issued state rejected — `test_never_issued_state_is_rejected`.
