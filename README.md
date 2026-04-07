# WhatToEat Backend

A FastAPI backend for the WhatToEat app (UW-Madison dining workflow).

This repository currently focuses on:
- Homescreen recommendation and meal logging APIs
- Dining hall browsing APIs
- Community post/like/reply APIs
- Menu data ingestion scripts and integration test scripts

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL (Supabase) |
| Validation | Pydantic v2 |

## Current API Status (2026-04-07)

Implemented and tested in this branch:
- Homescreen
	- `GET /recommendations/combo`
	- `GET /goals/daily`
	- `GET /menus/summary`
	- `POST /meals/log`
	- `POST /favorites`
	- `DELETE /favorites/{favorite_id}`
	- `GET /recommendations/addons`
- Dining Halls
	- `GET /dining-halls`
	- `GET /dining-halls/{hall_id}`
	- `GET /dining-halls/{hall_id}/stations`
	- `GET /dining-halls/{hall_id}/menus`
	- `GET /dining-halls/full`
- Community
	- `GET /community/posts`
	- `POST /community/posts`
	- `GET /community/posts/{post_id}`
	- `DELETE /community/posts/{post_id}`
	- `POST /community/posts/{post_id}/likes`
	- `DELETE /community/posts/{post_id}/likes`
	- `POST /community/posts/{post_id}/replies`
	- `POST /community/replies/{reply_id}/replies`
	- `POST /community/replies/{reply_id}/likes`
	- `DELETE /community/replies/{reply_id}/likes`

Planned next domains:
- Questionnaire
- Scan
- Profile
- Auth/session hardening

## Project Structure

```
whattoeat-backend/
├── app/
│   ├── main.py                  # FastAPI entry point + router registration
│   ├── config.py                # Settings (currently DATABASE_URL)
│   ├── database.py              # Async SQLAlchemy engine/session/base
│   ├── models/
│   │   ├── user.py
│   │   ├── menu.py
│   │   ├── tracking.py
│   │   └── community.py
│   ├── schemas/
│   │   ├── homescreen.py
│   │   ├── dining_hall.py
│   │   └── community.py
│   ├── services/
│   │   ├── homescreen_service.py
│   │   ├── dining_hall_service.py
│   │   └── community_service.py
│   ├── routers/
│   │   ├── homescreen.py
│   │   ├── dining_hall.py
│   │   └── community.py
│   └── utils/
├── scripts/
│   ├── ingest_json.py
│   ├── test_homescreen_api.py
│   ├── test_dining_hall_api.py
│   └── test_community_api.py
├── data/                        # Scraped Nutrislice JSON snapshots by date
├── sql/
│   ├── init.sql
│   └── *.sql                    # Additional migration/ops SQL files
├── docs/
│   └── api/                     # Per-domain API documentation
├── scraper.py                   # Nutrislice menu scraper entry
└── requirements.txt
```

Each domain follows the pattern: **model → schema → service → router**.

## Auth Note (Current)

The current implemented APIs use `user_id` query parameters for user-scoped operations in local/integration flows.

JWT header-based enforcement is documented in planning/docs and intended for production-grade auth hardening.

## API Documentation

- API doc index: [docs/api/README.md](docs/api/README.md)
- Community detail doc: [docs/api/community/community.md](docs/api/community/community.md)
- Dining halls docs: [docs/api/dining-halls/README.md](docs/api/dining-halls/README.md)
- Homescreen docs: [docs/api/homescreen/README.md](docs/api/homescreen/README.md)

## Database

Schema sources:
- Base schema SQL: [sql/init.sql](sql/init.sql)
- SQLAlchemy models (including community tables):
	- `app/models/user.py`
	- `app/models/menu.py`
	- `app/models/tracking.py`
	- `app/models/community.py`

## Test Scripts

Run domain integration tests:

```bash
python scripts/test_homescreen_api.py --base-url http://127.0.0.1:8000
python scripts/test_dining_hall_api.py --base-url http://127.0.0.1:8000
python scripts/test_community_api.py --base-url http://127.0.0.1:8000
```

Each script:
- Resolves/creates test context as needed
- Auto-starts local uvicorn if not already running
- Verifies key API responses against DB state

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
cp .env.example .env
# Required:
# DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:6543/postgres

# Start the server
uvicorn app.main:app --reload
# Tables are auto-created on startup via SQLAlchemy Base.metadata.create_all
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Postgres connection string for async SQLAlchemy |


## Out of Scope (v2+)

- Production auth/session enforcement (JWT middleware integration)
- ML-based food scanning
- Realtime features and notifications
- Multi-school expansion
