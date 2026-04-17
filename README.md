# WhatToEat Backend

A FastAPI backend for the WhatToEat app — personalized dining hall recommendations, meal logging, food scanning, and a community feed for UW-Madison students.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ (3.12 recommended for deployment; see [Deploying on Render](#deploying-on-render)) |
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

## Technical Architecture (Current)

The current backend is a **single FastAPI service** with domain-layered modules and a separate ingestion workflow.

### Core Components

- **API application (`app/main.py`)**: Registers routers, applies CORS policy, and runs startup schema compatibility checks.
- **Authentication layer (`app/dependencies.py`)**: Validates Supabase JWTs using JWKS, caches signing keys (1-hour TTL), and resolves user identity from `sub`.
- **Routing layer (`app/routers/*`)**: Exposes domain endpoints (auth, questionnaire, homescreen, dining halls, scan, community, profile).
- **Service layer (`app/services/*`)**: Implements business logic (recommendation composition, meal logging, profile/community behaviors).
- **Data layer (`app/database.py`, `app/models/*`)**: Uses async SQLAlchemy with PostgreSQL (Supabase).
- **Ingestion pipeline (`scraper.py`, `scripts/ingest_json.py`)**: Scrapes Nutrislice data to JSON snapshots and bulk upserts normalized records into Postgres.

### Runtime Characteristics

- Async request handling with FastAPI + SQLAlchemy async sessions.
- Supabase JWT enforcement on personalized endpoints; optional `?user_id=` fallback is dev-only (`ALLOW_QUERY_USER_ID=true`).
- Compatibility handling for Supabase pooler/asyncpg behavior in DB connection setup.
- Menu/catalog data is preloaded by batch ingest and served online through read APIs.

## Data Flow

### Flow A: Authentication & Authorized Request

1. Client signs in through Supabase Auth and receives an access token.
2. Client calls API with `Authorization: Bearer <token>` (or `X-Supabase-Access-Token`).
3. Backend validates token signature/issuer against Supabase JWKS.
4. Backend extracts `sub` as `user_id` and injects it into the route/service.
5. Service reads/writes user-scoped data and returns response.

### Flow B: Menu Ingestion (Offline)

1. `scraper.py` calls Nutrislice weekly menu endpoints.
2. Weekly payloads are split into per-day files under `data/YYYY-MM-DD/`.
3. `scripts/ingest_json.py` parses snapshots and builds normalized entities.
4. Bulk upserts write to menu tables (`restaurants`, `meal_types`, `foods`, `food_nutrition`, `menu_*`).
5. Serving endpoints consume these normalized tables.

### Flow C: Recommendation Request (`GET /recommendations/combo`)

1. Request includes date/meal parameters + authenticated identity.
2. Service loads user targets/preferences (calories, macros, allergens, dislikes).
3. Service loads matching menu snapshots/foods for requested date/meal.
4. Candidate foods are filtered by allergens/dislikes.
5. Combo builder selects items, computes totals/labels, and marks logged status.
6. API returns combo list payload to client.

### Flow D: Meal Logging & Goal Tracking

1. Client logs meal items via `POST /meals/log`.
2. Backend persists `meal_logs` + `meal_log_items` with nutrition snapshot values.
3. Client requests `GET /goals/daily`.
4. Backend aggregates consumed nutrients and compares against user goals.

### Flow E: Community/Profile Updates

1. Public reads are allowed where applicable; writes require authenticated user identity.
2. Service layer enforces ownership/authorization logic.
3. DB writes are committed and response payloads are shaped by schemas.

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

## Deploying on Render

- **Python version:** New Render services default to **Python 3.14**, which often forces a **source build** of `pydantic-core` (Rust) and can fail on their build image. This repo includes **`.python-version`** with `3.12` so Render installs **3.12.x** and uses **prebuilt wheels**. Alternatively set the env var **`PYTHON_VERSION`** to a full version (e.g. `3.12.8`) in the dashboard (it overrides `.python-version`).
- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Env:** Set `DATABASE_URL`, `SUPABASE_*`, `FRONTEND_URL`, and `ALLOW_QUERY_USER_ID=false` as in [Environment Variables](#environment-variables).

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
| [`docs/architecture.md`](docs/architecture.md) | Product architecture/planning notes (legacy draft; this README documents current runtime architecture) |
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
