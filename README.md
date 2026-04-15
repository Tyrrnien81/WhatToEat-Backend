# WhatToEat Backend

A backend service for a UW-Madison dining hall meal recommendation app. Helps students browse dining hall menus, get personalized meal recommendations based on nutrition goals, track meals, and engage with a food-focused community.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Framework | FastAPI |
| ORM | Django ORM (standalone) |
| Database | PostgreSQL |
| Cache | Redis |
| Object Storage | AWS S3 |
| Auth | Google OAuth2 + Custom JWT |
| Scheduler | APScheduler (daily Nutrislice ingestion) |
| Deployment | AWS (EC2/ECS) |

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
│   ├── config.py                # Settings (env vars, DB, Redis, S3, JWT)
│   ├── dependencies.py          # Shared dependencies (auth, db session)
│   ├── routers/                 # Route handlers per domain
│   │   ├── auth.py
│   │   ├── questionnaire.py
│   │   ├── dining.py
│   │   ├── home.py
│   │   ├── recommendation.py
│   │   ├── tracking.py
│   │   ├── scan.py
│   │   ├── community.py
│   │   └── profile.py
│   ├── models/                  # Django ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── services/                # Business logic
│   ├── ingestion/               # Nutrislice data pipeline
│   ├── recommendation/          # Recommendation algorithm
│   └── utils/                   # JWT, OAuth, Redis, S3 helpers
├── django_settings.py           # Django ORM standalone config
├── manage.py                    # Django migrations CLI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml           # Local dev: FastAPI + Postgres + Redis
└── tests/
```

## Database Schema

**19 tables** across 5 domains:

- **Menu (10 tables):** `restaurants`, `meal_types`, `menu_snapshots`, `menu_sections`, `stations`, `foods`, `food_nutrition`, `food_icons`, `food_icon_assignments`, `menu_section_items`
- **User (3 tables):** `users`, `user_preferences`, `otp_codes`
- **Tracking (2 tables):** `meal_logs`, `meal_log_items`
- **Favorites (1 table):** `favorites`
- **Community (3 tables):** `posts`, `post_media`, `post_likes`

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

Full API documentation: [api-document/README.md](api-document/README.md) | Detailed spec: [my-understanding/detailed-api-doc.md](my-understanding/detailed-api-doc.md)

## Implementation Phases

1. **Project Scaffold + Auth** — FastAPI setup, Docker Compose, user models, auth endpoints, JWT middleware
2. **Menu Ingestion Pipeline** — Nutrislice client, parser, daily scheduler, S3 raw storage, Redis cache invalidation
3. **Menu API** — Dining hall listing, menu browsing, search, favorites, Redis caching
4. **Recommendation Engine** — Allergen/diet filtering, linear programming optimizer, top-N combo generation
5. **Meal Tracking** — Meal logging, daily nutrition summary vs. goals
6. **Community** — Posts with media (S3), likes, comments, pagination
7. **Scan** — Search-based food lookup (MVP), image upload flow

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Tyrrnien81/WhatToEat-Backend.git
cd WhatToEat-Backend

# Start services (Postgres + Redis + FastAPI)
docker-compose up -d

# Run migrations
python manage.py migrate

# Start the server
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Secret key for JWT signing |
| `GOOGLE_CLIENT_ID` | Google OAuth2 client ID |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for S3 |
| `AWS_S3_BUCKET` | S3 bucket name for media uploads |
| `DJANGO_SETTINGS_MODULE` | Path to Django settings (e.g., `django_settings`) |

## Out of Scope (v2+)

- Refresh tokens
- Apple/GitHub auth providers
- Real-time dining hall occupancy
- Push notifications
- Weekly/monthly nutrition statistics
- Friend features / social meal sharing
- ML-based food scanning
- Multi-school support
- Comments on community posts (included in detailed API doc, deferred in backend plan)

```
WhatToEat-Backend
├─ .DS_Store
├─ API-Skeleton.text
├─ CODE_ARCHITECTURE.md
├─ Gordon-Station
├─ Gordon_Avenue_Market_03-15-2026.json
├─ IMPLEMENTATION_CHECKLIST.md
├─ IMPLEMENTATION_SUMMARY.md
├─ README.md
├─ START_HERE.md
├─ TROUBLESHOOTING.md
├─ app
│  ├─ .DS_Store
│  ├─ __init__.py
│  ├─ config.py
│  ├─ confirm_user.py
│  ├─ database.py
│  ├─ dependencies.py
│  ├─ main.py
│  ├─ models
│  │  ├─ __init__.py
│  │  ├─ favorite.py
│  │  └─ user.py
│  ├─ routers
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  └─ favorite.py
│  ├─ schemas
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  └─ favorite.py
│  ├─ services
│  │  ├─ __init__.py
│  │  └─ favorite_service.py
│  └─ utils
│     └─ __init__.py
├─ docs
│  ├─ AUTHENTICATION_GUIDE.md
│  ├─ api
│  │  ├─ README.md
│  │  ├─ auth
│  │  │  ├─ README.md
│  │  │  ├─ forgot-pw.md
│  │  │  ├─ google.md
│  │  │  ├─ logout.md
│  │  │  ├─ me.md
│  │  │  ├─ refresh-token.md
│  │  │  ├─ resend-code.md
│  │  │  ├─ reset-pw.md
│  │  │  ├─ signin.md
│  │  │  ├─ signup.md
│  │  │  └─ verify-email.md
│  │  ├─ community
│  │  │  ├─ README.md
│  │  │  ├─ community.md
│  │  │  ├─ create-comment.md
│  │  │  ├─ create-post.md
│  │  │  ├─ delete-comment.md
│  │  │  ├─ delete-post.md
│  │  │  ├─ get-post.md
│  │  │  ├─ like-post.md
│  │  │  ├─ list-comments.md
│  │  │  ├─ list-posts.md
│  │  │  └─ unlike-post.md
│  │  ├─ dining-hall
│  │  │  └─ dining-hall.md
│  │  ├─ dining-halls
│  │  │  ├─ README.md
│  │  │  ├─ dining-halls.md
│  │  │  ├─ get-hall.md
│  │  │  ├─ get-menus.md
│  │  │  ├─ get-stations.md
│  │  │  └─ list-halls.md
│  │  ├─ homescreen
│  │  │  ├─ README.md
│  │  │  ├─ delete-favorite.md
│  │  │  ├─ get-combos.md
│  │  │  ├─ get-daily-goals.md
│  │  │  ├─ get-menu-summary.md
│  │  │  ├─ homescreen.md
│  │  │  └─ save-favorite.md
│  │  ├─ profile
│  │  │  ├─ README.md
│  │  │  ├─ add-food-log.md
│  │  │  ├─ change-password.md
│  │  │  ├─ delete-account.md
│  │  │  ├─ delete-food-log.md
│  │  │  ├─ food-log-summary.md
│  │  │  ├─ get-food-log.md
│  │  │  ├─ get-profile.md
│  │  │  ├─ profile.md
│  │  │  ├─ update-profile.md
│  │  │  └─ upload-avatar.md
│  │  ├─ questionnaire
│  │  │  ├─ README.md
│  │  │  ├─ get-preferences.md
│  │  │  ├─ questionnaire.md
│  │  │  ├─ submit.md
│  │  │  └─ update-preferences.md
│  │  └─ scan
│  │     ├─ README.md
│  │     ├─ log-scan.md
│  │     ├─ scan.md
│  │     └─ upload-scan.md
│  ├─ api-doc.md
│  ├─ architecture.md
│  ├─ db-doc.md
│  ├─ explanation.md
│  └─ user-table.md
└─ requirements.txt

```