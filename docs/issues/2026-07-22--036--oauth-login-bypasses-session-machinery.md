# OAuth login bypasses session tracking, token-version, and 2FA machinery (036)

**Status:** `verification needed`
**Created:** 2026-07-22
**Severity:** Medium
**Module:** `auth` (backend — OAuth)
**Source:** Backport from [gear-stack issue 036](../../../gear-stack/docs/issues/2026-07-21--036--oauth-login-bypasses-session-machinery.md)

## Problem

Password login funnels through `AuthService._issue_login_tokens`, which mints tokens with a session `jti`, the user's `tv` (token version), `emailVerified`, and 2FA claims, and registers the session in Redis via `track_user_session`.

`AuthService.login_with_oauth` instead called the low-level builders directly:

```python
access_token = create_access_token({"sub": user.id})
refresh_token = create_refresh_token({"sub": user.id})
```

No `jti`, no `tv`, no `emailVerified`, no 2FA context, and no `track_user_session` call.

## Resolution (2026-07-22)

Backported from gear-stack:

- Split `login_with_oauth` into `_resolve_oauth_user` (lookup/link/create, no tokens) + `login_with_oauth` (calls `_resolve_oauth_user` then `_issue_login_tokens`).
- `AuthServiceWith2FA.login_with_oauth` override honors 2FA the same as password login (shared `_build_two_factor_challenge` helper).
- `auth_utils.py` — pass `jti`/`tv` through `create_access_token`/`create_refresh_token` (required for `_issue_login_tokens` claims to appear in tokens).

## Scope

- [x] `backend/app/modules/auth/service.py` — `_resolve_oauth_user`, `login_with_oauth` reuses `_issue_login_tokens`
- [x] `backend/app/modules/auth/auth_utils.py` — `jti`/`tv` passthrough in token builders
- [x] `backend/app/modules/two_factor/auth_integration.py` — `_build_two_factor_challenge`, OAuth override
- [x] Tests: `test_auth_service.py::TestLoginWithOAuth`, `test_oauth_2fa_login.py`

## Verification

1. OAuth login issues tokens with `jti`/`tv`/`emailVerified` — covered by unit tests.
2. OAuth login for a user with `tokenVersion > 0` succeeds — covered by `test_login_with_oauth_survives_token_version_bump`.
3. OAuth login with 2FA enabled returns challenge — covered by `test_oauth_2fa_login.py`.
