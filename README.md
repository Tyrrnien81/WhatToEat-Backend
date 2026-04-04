# WhatToEat Backend

A backend service for a UW-Madison dining hall meal recommendation app. Helps students browse dining hall menus, get personalized meal recommendations based on nutrition goals, track meals, and engage with a food-focused community.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL (Supabase) |
| Cache | Redis |
| Object Storage | AWS S3 |
| Auth | Google OAuth2 + Custom JWT |
| Scheduler | APScheduler (daily Nutrislice ingestion) |
| Deployment | AWS (EC2/ECS) |
| DB Hosting | Supabase (managed Postgres, us-west-2) |

## Features (MVP)

1. **Authentication** — Email/password signup & login, Google OAuth, password reset via OTP, email verification
2. **Menu Ingestion** — Automated daily ingestion from Nutrislice API for 6 UW-Madison dining halls
3. **Menu Browsing** — Search, filter, and favorite menu items across all dining halls
4. **Meal Recommendations** — Personalized meal combos optimized via linear programming to match user nutrition targets
5. **Meal Tracking** — Log meals, view daily nutrition summary vs. goals
6. **Community** — Posts with dining hall tags, likes, and comments
7. **Scan** — Search-based food lookup and nutrition logging (ML recognition planned for v2)

## Project Structure

```
whattoeat-backend/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Settings (env vars, DB, JWT)
│   ├── database.py              # Async SQLAlchemy engine & session
│   ├── dependencies.py          # Shared dependencies (auth, db session)
│   ├── routers/                 # Route handlers per domain
│   │   ├── auth.py
│   │   └── favorite.py
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py
│   │   └── favorite.py
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth.py
│   │   └── favorite.py
│   ├── services/                # Business logic
│   │   ├── auth_service.py
│   │   └── favorite_service.py
│   └── utils/                   # JWT, OAuth helpers
│       ├── jwt.py
│       ├── google_oauth.py
│       └── email.py
├── scripts/
│   └── ingest_json.py           # Nutrislice JSON → Supabase ingestion
├── sql/
│   └── init.sql                 # Full DB schema (16 tables)
├── scraper.py                   # Nutrislice menu scraper
├── docs/                        # Per-endpoint API specs
└── requirements.txt
```

Each domain follows the pattern: **model → schema → service → router**.

## Database Schema

**16 tables** across 4 phases (all live in Supabase):

| Phase | Tables | Count |
|-------|--------|-------|
| 0 — Auth | `users`, `verification_codes`, `refresh_tokens` | 3 |
| 1 — Menu & Food | `restaurants`, `meal_types`, `foods`, `food_icons`, `menu_snapshots`, `menu_sections`, `food_nutrition`, `food_icon_assignments`, `menu_section_items` | 9 |
| 2 — User Preferences & Tracking | `user_preferences`, `meal_logs`, `meal_log_items` | 3 |
| 3 — Favorites | `favorites` | 1 |

Full schema: [`sql/init.sql`](sql/init.sql) | Column-level docs: [`docs/db-doc.md`](docs/db-doc.md)

## API Overview

All protected endpoints require a JWT token in the `Authorization: Bearer <token>` header.

| Service | Key Endpoints | Auth Required |
|---------|--------------|---------------|
| **Auth** | `POST /auth/signup`, `/auth/signin`, `/auth/google`, `/auth/forgot-pw`, `/auth/reset-pw`, `/auth/verify-email`, `/auth/refresh-token` | No (public) |
| **Questionnaire** | `POST /questionnaire`, `GET/PATCH /users/me/preferences` | Yes |
| **Home** | `GET /recommendations/combo`, `GET /goals/today`, `GET /menus/summary`, `POST /log-meal` | Yes |
| **Dining Hall** | `GET /dining-hall`, `GET /dining-hall/:id/stations/menu`, `GET /dining-hall/:id/ai-pick` | Mixed |
| **Scan** | `POST /scan`, `POST /scan/log` | Yes |
| **Community** | `GET/POST /community/posts`, `POST/DELETE .../like`, `GET/POST .../comments` | Mixed |
| **Profile** | `GET/PATCH /users/me`, `GET/POST/DELETE /users/me/food-log`, `POST /users/me/avatar` | Yes |

Full API documentation: [docs/api/README.md](docs/api/README.md) | Detailed spec: [my-understanding/detailed-api-doc.md](my-understanding/detailed-api-doc.md)

## Implementation Progress

- [x] **Project Scaffold + Auth** — FastAPI setup, user models, auth endpoints (signup/signin/Google OAuth/password reset/email verification), JWT middleware
- [x] **Database Init** — All 16 tables created in Supabase via `sql/init.sql`
- [x] **Data Ingestion** — `scripts/ingest_json.py` loads Nutrislice JSON exports into Supabase (Gordon Avenue Market ingested)
- [x] **Favorites API** — `POST /favorites` (JSONB snapshot, 409 on duplicate), `DELETE /favorites/{id}` (ownership check)
- [ ] **Dining Halls API** — List halls, get menus/stations (tables + data exist, endpoints not built)
- [ ] **Homescreen API** — `GET /recommendations/combo`, `GET /goals/today`, `POST /log-meal` (P0 — powers the core frontend flow)
- [ ] **Questionnaire API** — Submit/get/update user dietary preferences
- [ ] **Profile API** — User profile CRUD, food logging, avatar upload
- [ ] **Community API** — Posts, likes, comments (tables not yet created)
- [ ] **Scan API** — Search-based food lookup (MVP)
- [ ] **Recommendation Engine** — Linear programming optimizer for meal combos

### API Priority (from frontend button audit)

| Priority | Endpoints | Why |
|----------|-----------|-----|
| **P0** | `GET /recommendations/combo`, `GET /goals/today`, `POST /log-meal` | Powers date pills, hall cards, "Log This Meal" button |
| **P1** | Food swap alternatives, quick add-ons | Swipe-to-swap, extra meal items |
| **P2** | Favorites (done), Community, Scan | Backend-ahead or lower usage |

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Tyrrnien81/WhatToEat-Backend.git
cd WhatToEat-Backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy .env.example to .env and fill in your Supabase credentials:
#   DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:6543/postgres
# You can find the connection string in your Supabase project under
# Settings → Database → Connection string → URI (use the "connection pooling" URI on port 6543).

# Start the server
uvicorn app.main:app --reload
# Tables are auto-created on startup via SQLAlchemy Base.metadata.create_all
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase PostgreSQL connection string (e.g. `postgresql+asyncpg://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres`) |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Secret key for JWT signing |
| `GOOGLE_CLIENT_ID` | Google OAuth2 client ID |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 |
| `AWS_S3_BUCKET` | S3 bucket name for media uploads |


## Out of Scope (v2+)

- Apple/GitHub auth providers
- Real-time dining hall occupancy
- Push notifications
- Weekly/monthly nutrition statistics
- Friend features / social meal sharing
- ML-based food scanning
- Multi-school support
