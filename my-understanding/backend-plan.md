# Plan: WhatToEat Backend Architecture & Implementation

## Quick Summary

- **Language:** Python
- **Framework:** FastAPI
- **ORM:** Django ORM (standalone)
- **Database:** PostgreSQL
- **Cache:** Redis
- **Object Storage:** AWS S3
- **Auth:** Google OAuth2 + custom JWT
- **Scheduler:** APScheduler (in-process, daily Nutrislice ingestion)
- **Deployment:** AWS (EC2/ECS)
- **Database:** 19 tables (10 menu, 3 user, 2 tracking, 1 favorites, 3 community)

**MVP Features:**
1. Auth (email + Google login, password reset via OTP)
2. Menu ingestion from Nutrislice (daily automated)
3. Menu browsing API (search, filter, favorites)
4. Meal recommendation engine (linear programming optimization)
5. Meal tracking + daily nutrition summary
6. Community (posts with dining hall tags + likes)
7. Scan (search-based food lookup for MVP, no ML)

**Out of Scope (v2):** Refresh tokens, push notifications, ML food scanning, multi-school support, weekly/monthly stats, friend features

---

## TL;DR
Build a **Python/FastAPI** monolith backend for a UW-Madison dining hall meal recommendation app. The backend handles auth, Nutrislice menu ingestion, meal recommendation, meal tracking, community posts, and food scanning — all in one service. Deploy on AWS with PostgreSQL, Redis, and S3.

---

## Decisions Made

| Decision | Choice |
|----------|--------|
| Language | Python (single service) |
| Web Framework | FastAPI |
| ORM | Django ORM (standalone, via `django.setup()`) |
| Database | PostgreSQL |
| Cache | Redis |
| Object Storage | AWS S3 |
| Auth | Google OAuth2 + custom JWT |
| Ingestion Scheduler | APScheduler (in-process) |
| Deployment | AWS (EC2/ECS) |
| Recommendation Engine | Built into the FastAPI service (no separate Python service) |

### ⚠️ Architecture Note: Django ORM + FastAPI
Django ORM is tightly coupled to the Django framework. Using it standalone with FastAPI requires:
- Calling `django.setup()` at app startup
- Defining `DJANGO_SETTINGS_MODULE` with DB config
- Running Django migrations separately
- Async support is limited (Django ORM is sync; need `sync_to_async` wrappers or thread pools)

**Alternative**: SQLAlchemy (with async support) is the natural pairing with FastAPI. If the team is more comfortable with Django ORM or plans to potentially migrate to Django later, the Django ORM choice can work but adds friction.

---

## Project Structure

```
whattoeat-backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings (env vars, DB, Redis, S3, JWT)
│   ├── dependencies.py          # Shared FastAPI dependencies (auth, db session)
│   ├── routers/
│   │   ├── auth.py              # /auth/* endpoints
│   │   ├── questionnaire.py     # /questionnaire/* endpoints
│   │   ├── dining.py            # /dining/* endpoints
│   │   ├── home.py              # /home/* endpoints
│   │   ├── recommendation.py    # /recommendation/* endpoints
│   │   ├── tracking.py          # /tracking/* endpoints
│   │   ├── scan.py              # /scan/* endpoints
│   │   ├── community.py         # /community/* endpoints
│   │   └── profile.py           # /profile/* endpoints
│   ├── models/                  # Django ORM models
│   │   ├── user.py
│   │   ├── menu.py
│   │   ├── tracking.py
│   │   └── community.py
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── menu.py
│   │   ├── recommendation.py
│   │   ├── tracking.py
│   │   └── community.py
│   ├── services/                # Business logic
│   │   ├── auth_service.py
│   │   ├── menu_service.py
│   │   ├── recommendation_service.py
│   │   ├── tracking_service.py
│   │   ├── scan_service.py
│   │   └── community_service.py
│   ├── ingestion/               # Nutrislice data pipeline
│   │   ├── scheduler.py         # APScheduler setup
│   │   ├── nutrislice_client.py # API/scraper
│   │   ├── parser.py            # JSON → normalized models
│   │   └── cache_invalidator.py # Clear Redis after ingestion
│   ├── recommendation/          # Recommendation algorithm
│   │   ├── engine.py            # Core algorithm
│   │   ├── filters.py           # Allergen/diet/preference filters
│   │   └── optimizer.py         # Nutrition goal optimizer
│   └── utils/
│       ├── jwt.py               # JWT encode/decode
│       ├── google_oauth.py      # Google token validation
│       ├── redis_client.py      # Redis connection
│       └── s3_client.py         # S3 upload/download
├── django_settings.py           # Django ORM standalone config
├── manage.py                    # Django migrations CLI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml           # Local dev: FastAPI + Postgres + Redis
└── tests/
```

---

## Database Schema (Refined from existing analysis)

### Menu Domain (10 tables)
1. **`restaurants`** — `id`, `external_restaurant_id`, `name`, `slug`, `latitude`, `longitude`, `address`, `operating_hours` (JSONB)
2. **`meal_types`** — `id`, `external_meal_type_id`, `name` (Breakfast/Lunch/Dinner)
3. **`menu_snapshots`** — `id`, `restaurant_id` FK, `meal_type_id` FK, `service_date`, `fetched_at`
4. **`menu_sections`** — `id`, `snapshot_id` FK, `external_menu_id`, `display_name`, `position`
5. **`stations`** — `id`, `name` (Entree, Sides, Breads, etc.)
6. **`foods`** — `id`, `external_food_id`, `name`, `description`, `food_category`, `base_price`, `image_url`
7. **`food_nutrition`** — `id`, `food_id` FK (unique), `serving_size`, `calories`, `total_fat`, `saturated_fat`, `cholesterol`, `sodium`, `total_carbs`, `dietary_fiber`, `sugars`, `protein`, `vitamin_a_pct`, `vitamin_c_pct`, `calcium_pct`, `iron_pct`
8. **`food_icons`** — `id`, `name`, `slug`, `is_filter`, `is_highlight`, `sort_order`
9. **`food_icon_assignments`** — `food_id` FK, `icon_id` FK (composite PK)
10. **`menu_section_items`** — `id`, `section_id` FK, `food_id` FK, `station_id` FK (nullable), `position`, `price`

### User Domain (3 tables)
11. **`users`** — `id` (UUID), `email`, `name`, `provider` (google/email/guest), `password_hash` (nullable), `phone`, `bio`, `created_at`, `updated_at`
12. **`user_preferences`** — `id`, `user_id` FK (unique), `birthday`, `gender`, `height_cm`, `weight_kg`, `goal_weight_kg`, `target_calories`, `target_protein_g`, `target_carbs_g`, `target_fat_g`, `diet_type` (vegan/vegetarian/halal/none), `dislikes` (text[]), `allergens` (text[]), `preferred_dining_halls` (int[])
13. **`otp_codes`** — `id`, `user_id` FK, `code` (6 digits), `expires_at`, `used`

### Tracking Domain (2 tables)
14. **`meal_logs`** — `id`, `user_id` FK, `date`, `meal_type`, `restaurant_id` FK, `created_at`
15. **`meal_log_items`** — `id`, `meal_log_id` FK, `food_id` FK, `quantity` (default 1)

### Favorites (1 table)
16. **`favorites`** — `id`, `user_id` FK, `food_id` FK (nullable), `recommendation_snapshot` (JSONB, nullable), `created_at`

### Community Domain (3 tables)
17. **`posts`** — `id`, `user_id` FK, `restaurant_id` FK, `title`, `body`, `created_at`, `updated_at`
18. **`post_media`** — `id`, `post_id` FK, `media_url` (S3), `media_type` (image/video)
19. **`post_likes`** — `user_id` FK, `post_id` FK (composite PK), `created_at`

**Total: 19 tables**

---

## Phase-by-Phase Implementation

### Phase 1: Project Scaffold + Auth
> Unblocks frontend login flow immediately

**Steps:**
1. Initialize FastAPI project, configure Django ORM standalone, set up `docker-compose.yml` (Postgres + Redis)
2. Define Django models for `users`, `user_preferences`, `otp_codes`
3. Run initial migration
4. Implement `POST /auth/signup` — email/password registration (bcrypt hash)
5. Implement `POST /auth/signin` — email/password login, return JWT
6. Implement `POST /auth/google` — validate Google OAuth2 id_token, create-or-find user, return JWT
7. Implement `POST /auth/forgot-password` — generate 6-digit OTP, store in `otp_codes`, send via email (AWS SES)
8. Implement `POST /auth/verify-otp` — validate OTP
9. Implement `POST /auth/reset-password` — update password after OTP verification
10. Implement JWT middleware dependency (`get_current_user`) for protected routes
11. Implement `POST /questionnaire` — save user preferences after first login
12. Implement `GET /profile`, `PUT /profile`, `PUT /profile/password` — profile CRUD

**Auth decisions:**
- JWT access token: 24h expiry (MVP, no refresh token)
- Password requirements: 8+ chars, upper, lower, digit, special char
- Guest users: no DB record, limited endpoints (menu read-only)

### Phase 2: Menu Ingestion Pipeline
> Populates DB with real Nutrislice data

**Steps:**
1. Define Django models for all menu-domain tables (restaurants, foods, food_nutrition, etc.)
2. Run migration
3. Build `nutrislice_client.py` — HTTP client to fetch menu JSON from Nutrislice API/site
4. Build `parser.py` — parse Nutrislice JSON, separating section headers from food items, extracting nutrition and icons. Reference the structure from `Gordon_Avenue_Market_03-15-2026.json`
5. Build ingestion pipeline — upsert restaurants → meal types → snapshots → sections → foods → nutrition → icons → section items
6. Store raw Nutrislice JSON to S3 for debugging/reprocessing
7. Set up APScheduler to run ingestion daily (e.g., 5 AM CT)
8. Add retry logic with exponential backoff on Nutrislice failures
9. Invalidate relevant Redis cache keys after successful ingestion
10. Seed DB with existing JSON file (`Gordon_Avenue_Market_03-15-2026.json`) for development

### Phase 3: Menu API
> Frontend can display dining halls and menus

**Steps:**
1. Implement `GET /dining/halls` — list all dining halls with open/closed status (based on `operating_hours`), sortable by relevance/open-now
2. Implement `GET /dining/halls/{id}/menu?date=&meal=` — return menu for a hall, date, meal type, grouped by station/section
3. Implement `GET /dining/search?q=` — search menu items by name across all halls
4. Implement Redis caching layer: cache today's menus, hall list, popular items
5. Implement `POST /favorites` and `GET /favorites` — star/unstar food items and combos
6. Implement `GET /dining/halls/{id}/occupancy` — placeholder/mock for occupancy data (future: real-time integration)

### Phase 4: Recommendation Engine
> Core differentiator — meal combo optimization

**Steps:**
1. Build `filters.py` — filter today's menu by: allergens, diet type (vegan/halal/etc.), user dislikes, dining hall preference
2. Build `optimizer.py` — given filtered foods + user nutrition targets, find top-N meal combos that minimize distance to target macros. Algorithm options:
   - **Greedy**: sort by protein density, pick greedily (fast, less optimal)
   - **Knapsack-variant**: treat calories as weight, protein as value (better)
   - **Linear programming** (scipy.optimize.linprog): minimize |actual - target| across macros (best for MVP)
3. Build `engine.py` — orchestrate: load user prefs → get today's menu → filter → optimize → format response
4. Implement `GET /home/recommendations?date=` — return top 3 recommended plates per dining hall, with nutrition breakdown
5. Cache recommendation results in Redis (invalidate on menu change or preference update)

### Phase 5: Meal Tracking
> Users log what they ate, see progress

**Steps:**
1. Define Django models for `meal_logs`, `meal_log_items`
2. Implement `POST /tracking/log` — log a meal (dining hall, meal type, list of food items)
3. Implement `GET /tracking/logs?date=` — get logged meals for a date
4. Implement `GET /tracking/summary?date=` — daily nutrition totals vs. goals
5. Implement `DELETE /tracking/log/{id}` — remove a logged meal
6. Implement `POST /tracking/log/{id}/items` — add more items to existing log

### Phase 6: Community
> Social features — posts with dining hall tags

**Steps:**
1. Define Django models for `posts`, `post_media`, `post_likes`
2. Implement `POST /community/posts` — create post (required: dining hall tag, body; optional: media)
3. Implement `GET /community/posts?hall=&q=&page=` — paginated feed, filterable by dining hall, searchable by keyword
4. Implement `POST /community/posts/{id}/like` and `DELETE /community/posts/{id}/like`
5. Media upload: accept image/video → upload to S3 → store URL in `post_media`
6. Implement `DELETE /community/posts/{id}` — author only

### Phase 7: Scan
> Camera → nutrition lookup

**Steps:**
1. Implement `POST /scan/analyze` — accept image upload
2. Options for food recognition:
   - **Option A**: Use a third-party API (Google Cloud Vision, Clarifai, LogMeal API) to identify food → match against our DB foods by name
   - **Option B**: Simple barcode/label OCR → parse nutrition text
   - **Option C**: Manual search fallback — user types food name, we look up in our DB
3. Return matched food(s) with nutrition info
4. Allow adding scanned result to meal log

**Recommendation**: Start with **Option C** (search-based) for MVP, integrate ML-based recognition in v2.

---

## Relevant Files (Existing)

- `api-doc.md` — existing API endpoint design (needs updating for FastAPI/Python)
- `architecture.md` — system architecture overview (needs updating: remove Node.js, single Python service)
- `db-doc.md` — current DB schema (too simple, replace with 19-table schema above)
- `Gordon_Avenue_Market_03-15-2026.json` — sample Nutrislice data for parser development
- `my-understanding/data-structure-analysis.md` — Nutrislice JSON structure analysis (use as parser reference)
- `explanation.md` — user auth design notes
- `user-table.md` — Nutrislice data raw analysis

---

## Verification

1. **Auth**: Test signup → signin → JWT → protected endpoint flow. Test Google OAuth with test account. Test OTP generation and password reset.
2. **Ingestion**: Run parser against `Gordon_Avenue_Market_03-15-2026.json`, verify all 58 food items + nutrition + icons are correctly inserted. Verify section headers are excluded.
3. **Menu API**: Query `GET /dining/halls` and verify all 6 halls returned. Query menu for a specific date and verify station grouping is correct.
4. **Recommendation**: Create user with 2000cal / 150g protein target, run recommendation against real menu data, verify combos are within 10% of targets.
5. **Tracking**: Log a meal, verify daily summary matches expected nutrition totals.
6. **Community**: Create post with image, verify S3 upload and retrieval.
7. **Integration**: Full flow — login → see recommendations → log meal → check progress.
8. **Load**: Verify Redis cache reduces DB queries on repeated menu fetches.

---

## Decisions & Scope

**In scope (MVP)**:
- Email + Google auth (JWT, no refresh token for MVP)
- Nutrislice ingestion for 6 UW-Madison dining halls
- Menu browsing with search, filtering, favorites
- Meal recommendation (linear programming optimization)
- Meal tracking with daily summary
- Basic community (posts + likes, no comments for MVP)
- Basic scan (search-based food lookup, no ML)

**Out of scope (v2+)**:
- Refresh tokens
- Apple/GitHub/Kakao auth providers
- Real-time dining hall occupancy
- Push notifications
- Weekly/monthly nutrition statistics
- Friend features / social meal sharing
- ML-based food scanning
- Multi-school support
- Comments on community posts

---

## Further Considerations

1. **Django ORM + FastAPI friction**: Django ORM is synchronous. Every DB call in FastAPI async endpoints needs `sync_to_async` wrapper or `run_in_executor`, adding boilerplate. **Recommendation**: If the team doesn't have strong Django ORM preference, switch to SQLAlchemy 2.0 (native async). If Django ORM is chosen for familiarity, accept the async overhead.

2. **Email service for OTP**: Need an email provider for password reset OTP. Options: AWS SES (fits AWS deployment), SendGrid free tier, or Gmail SMTP (dev only). **Recommendation**: AWS SES since deploying on AWS.

3. **Scan feature MVP scope**: Full camera → food recognition is a major ML undertaking. **Recommendation**: Ship scan as "search and log" for MVP (user types food name, sees matches and nutrition). Add image-based recognition in v2 via Google Cloud Vision or similar API.
