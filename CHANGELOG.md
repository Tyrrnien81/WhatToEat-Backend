# Changelog

## 2026-04-10 — Authentication API (Supabase Direct)

### Added
- `GET /auth/me` — retrieve authenticated user's profile from database
- `POST /auth/profile` — upsert profile after Supabase auth (syncs email from JWT)
- `POST /auth/logout` — revoke Supabase session server-side via Admin API
- `app/routers/auth.py`, `app/schemas/auth.py`, `app/services/auth_service.py`
- CORS middleware with configurable `FRONTEND_URL`
- `docs/api/auth/profile-upsert.md` — new endpoint documentation

### Fixed (Security)
- Replaced `@lru_cache` JWKS fetch with 1-hour TTL cache (handles key rotation)
- Replaced sync `requests.get()` with async `httpx.AsyncClient` (non-blocking)
- Centralized Supabase config in `app/config.py` via `pydantic-settings`
- Swapped `requests` for `httpx` in requirements.txt

### Changed
- Auth architecture: Supabase-direct model (frontend handles signup/signin/OAuth/verify/reset via Supabase JS SDK)
- Rewrote all 10 auth endpoint docs to reflect Supabase-direct architecture
- Updated `docs/api-doc.md` auth section with backend vs client-side split
- Updated `docs/api/auth/README.md` with project structure and implementation notes
- Updated `required-api-document.xlsx` — 3 backend endpoints marked "Built", 8 client-side marked "Supabase"
- Cleaned up `.env.example` for Supabase-direct model

## 2026-04-10 — Questionnaire API

### Added
- `POST /questionnaire` — save initial onboarding preferences with unit conversion
- `GET /users/me/preferences` — retrieve dietary preferences and computed nutrition targets
- `PATCH /users/me/preferences` — partial update with auto-recalculation
- `app/routers/questionnaire.py`, `app/schemas/questionnaire.py`, `app/services/questionnaire_service.py`
- `favorite_dining_halls` JSONB column on `user_preferences` table

### Changed
- Updated all questionnaire docs with status badges and implementation details
- Updated `required-api-document.xlsx` — marked 3 questionnaire endpoints as "Built"
