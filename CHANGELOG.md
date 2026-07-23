# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [2.49.0] - 2026-07-23

### Added
- **Shopping**: last-visited shopping path; inline item rename; Polish unit aliases; improved quick-add parsing and quantity controls; product suggestions with category icons and auto-categorize
- **Ingredients**: preferred unit conversion for shopping-friendly display
- **UI**: mobile shell with bottom nav and confirm sheet; ambient backgrounds / design tokens; FamilyPage and RecipesPage layout polish
- **Auth**: GitHub OAuth login backport
- **Health**: `GET /api/health/details` for Ops Monitor
- **CLI**: `users change-password`
- AI module enabled in model modules list

### Changed
- Docker Compose at repo root; shared compose auto-detect; footer GitHub from app config
- Email template branding/colors; PWA theme colors; frontend dev port `5178`
- Typography and BottomNav layout consistency

### Fixed
- RecipeEditPage navigation visibility and submit button layout on smaller screens
- Family invitation UX on login/accept flow
- Billing: family plan shown consistently across billing and family pages
- CookingPot branding favicon (replaces backpack)

### Security
- Path-safe storage and OAuth state cleanup; unified OAuth callback `/auth/callback/:provider`
- OAuth session tracking, 2FA challenge, CSRF state store; `tv`/`jti` on 2FA login/refresh
- Shared-core auth/2FA/UX backport from gear-stack; pnpm Dependabot overrides
