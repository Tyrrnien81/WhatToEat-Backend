# WhatToEat Backend

A FastAPI backend for the WhatToEat app — personalized dining hall recommendations, meal logging, food scanning, and a community feed for UW-Madison students.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL (Supabase) |
| Validation | Pydantic v2 |
| Auth | Supabase Auth (JWT / JWKS) |
| HTTP Client | httpx (async) |

## API Overview (2026-04-10)

All endpoints are **implemented and documented**. Full details: [`docs/api-doc.md`](docs/api-doc.md).

| Service | Key Endpoints | Auth | Docs |
|---------|---------------|------|------|
| **Auth** | `GET /auth/me`, `POST /auth/profile`, `POST /auth/logout` | JWT | [auth/](docs/api/auth/README.md) |
| **Questionnaire** | `POST /questionnaire`, `GET/PATCH /users/me/preferences` | JWT | [questionnaire/](docs/api/questionnaire/README.md) |
| **Homescreen** | `GET /recommendations/combo`, `GET /goals/daily`, `GET /menus/summary`, `POST /meals/log`, `POST/DELETE /favorites`, `GET /recommendations/addons` | JWT | [homescreen/](docs/api/homescreen/README.md) |
| **Dining Halls** | `GET /dining-halls`, `GET /dining-halls/{id}`, `/stations`, `/menus`, `/full` | Public (optional JWT on `/full`) | [dining-halls/](docs/api/dining-halls/README.md) |
| **Scan** | `POST /scan`, `POST /scan/log` | JWT | [scan/](docs/api/scan/README.md) |
| **Community** | `GET/POST /community/posts`, detail, delete, likes, replies (full CRUD) | JWT for writes; optional JWT for reads | [community/](docs/api/community/README.md) |
| **Profile** | `GET/PATCH/DELETE /users/me`, avatar, change-password, food-log CRUD, food-log summary | JWT | [profile/](docs/api/profile/README.md) |

### Interactive docs

Start the server and visit **`/docs`** (Swagger UI) or **`/redoc`** to explore and test endpoints in the browser.

## Authentication

The frontend authenticates users via **Supabase Auth** (JS SDK). The backend validates Supabase-issued **JWT tokens** using JWKS:

```
Authorization: Bearer <access_token>
```

- User identity is extracted from the JWT `sub` claim (`users.id`).
- JWKS signing keys are cached for 1 hour and auto-rotated.
- **Auth, profile, questionnaire** routes use strict JWT enforcement.
- **Homescreen, community writes, scan** use JWT with a dev-only `?user_id=` fallback (see below).
- **Dining hall** and **community read** routes are public; optional JWT enables personalized flags (`likedByMe`, `favorited`).

### Dev-only query fallback

Setting `ALLOW_QUERY_USER_ID=true` (env var) lets personalized routes accept `?user_id=<uuid>` when no `Authorization` header is present. This exists **only for local integration test scripts**. **Never enable in production.**

## Project Structure

```
whattoeat-backend/
├── app/
│   ├── main.py                  # FastAPI entry point + router registration
│   ├── config.py                # Pydantic settings (DB, Supabase, CORS, dev flags)
│   ├── database.py              # Async SQLAlchemy engine/session/base
│   ├── dependencies.py          # JWT validation (JWKS), auth dependencies
│   ├── models/
│   │   ├── user.py              # User/profile model
│   │   ├── menu.py              # Dining hall, food, nutrition models
│   │   ├── tracking.py          # Meal logs, favorites, user preferences
│   │   └── community.py         # Posts, replies, likes
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── homescreen.py
│   │   ├── dining_hall.py
│   │   ├── community.py
│   │   ├── questionnaire.py
│   │   ├── scan.py
│   │   └── profile.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── homescreen_service.py
│   │   ├── dining_hall_service.py
│   │   ├── community_service.py
│   │   ├── questionnaire_service.py
│   │   ├── scan_service.py
│   │   └── profile_service.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── homescreen.py
│   │   ├── dining_hall.py
│   │   ├── community.py
│   │   ├── questionnaire.py
│   │   ├── scan.py
│   │   └── profile.py
│   └── utils/
├── scripts/
│   ├── ingest_json.py           # Nutrislice → DB menu ingestion
│   ├── test_homescreen_api.py
│   ├── test_dining_hall_api.py
│   ├── test_community_api.py
│   └── test_scan_api.py
├── data/                        # Scraped Nutrislice JSON snapshots by date
├── sql/
│   ├── init.sql
│   └── *.sql
├── docs/
│   ├── api-doc.md               # Single-page API reference
│   ├── api/                     # Per-service endpoint documentation
│   ├── architecture.md
│   └── db-doc.md
├── personal-docs/
│   ├── api/                     # API doc standards (standard-api-structure.md)
│   └── notes/summaries/         # Dated session summaries and reviews
├── supabase/                    # Supabase Edge Functions
├── scraper.py                   # Nutrislice menu scraper
└── requirements.txt
```

Each domain follows the pattern: **model → schema → service → router**.

## Getting Started

```bash
git clone https://github.com/Tyrrnien81/WhatToEat-Backend.git
cd WhatToEat-Backend

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in required values (see Environment Variables below)

uvicorn app.main:app --reload
# Tables are auto-created on startup via SQLAlchemy Base.metadata.create_all
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Async Postgres connection string (`postgresql+asyncpg://...`) |
| `SUPABASE_URL` | Yes | Supabase project URL (e.g. `https://xxx.supabase.co`) |
| `SUPABASE_ISSUER` | No | JWT issuer for token validation (auto-derived from `SUPABASE_URL` when omitted) |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key for admin operations (logout, account deletion) |
| `FRONTEND_URL` | No | Allowed CORS origin (default: `http://localhost:3000`) |
| `ALLOW_QUERY_USER_ID` | No | Dev-only: allow `?user_id=` on personalized routes (default: `false`) |

## Integration Tests

### Full API + auth review (pre-release)

Runs in-process via FastAPI `TestClient` (no separate server). Checks public routes, JSON shapes, **401 without JWT** on protected routes, and—when `ALLOW_QUERY_USER_ID=true` and a user exists in the DB (or `--user-id` is passed)—authenticated flows including scan and meal log.

```bash
python scripts/review_all_endpoints.py
WTE_ACCESS_TOKEN='<supabase access_token>' python scripts/review_all_endpoints.py   # optional Bearer check
```

### Per-area scripts

Each test script auto-starts a local uvicorn server (with `ALLOW_QUERY_USER_ID=true`) if one isn't already running, resolves or creates test users, and verifies API responses against DB state.

```bash
python scripts/test_homescreen_api.py --base-url http://127.0.0.1:8000
python scripts/test_dining_hall_api.py --base-url http://127.0.0.1:8000
python scripts/test_community_api.py  --base-url http://127.0.0.1:8000
python scripts/test_scan_api.py       --base-url http://127.0.0.1:8000
```

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/api-doc.md`](docs/api-doc.md) | Single-page API reference (all services, JWT rules, status codes) |
| [`docs/api/README.md`](docs/api/README.md) | API docs index with per-service links |
| [`docs/api/<service>/`](docs/api/) | Per-endpoint documentation (request/response/errors) |
| [`docs/architecture.md`](docs/architecture.md) | System architecture overview |
| [`docs/db-doc.md`](docs/db-doc.md) | Database schema documentation |

## Database

- Base schema: [`sql/init.sql`](sql/init.sql)
- SQLAlchemy models: `app/models/user.py`, `menu.py`, `tracking.py`, `community.py`
- Tables auto-created on startup; menu data ingested via `scripts/ingest_json.py`

## Security (2026-04-10)

- All personalized routes require **Supabase JWT** (`Authorization: Bearer`).
- JWKS keys cached with 1-hour TTL; async fetch via `httpx`.
- Scan uploads capped at **10 MB** (`413 Payload Too Large`).
- CORS configured to allowed origin only.
- `ALLOW_QUERY_USER_ID` defaults to **`false`** and must never be enabled in production.
- Run `python scripts/review_all_endpoints.py` before releases to re-check JWT behavior on all routes.

## Out of Scope (v2+)

- ML-based food scanning (current scan uses template matching)
- Real-time features and notifications
- Multi-school expansion
