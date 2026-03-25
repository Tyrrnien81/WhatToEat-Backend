# Session Plan — March 23, 2026 — Food Selection / Favorites API

## Goal

Implement the **food favorites** (starred/saved) API — the endpoints that let users save and remove recommended meal combos from their favorites list.

---

## Endpoints to Implement

| Method | Endpoint | Description | JWT |
|--------|----------|-------------|-----|
| POST | `/favorites` | Save a recommended combo to favorites | Yes |
| DELETE | `/favorites/:favoriteId` | Remove a combo from favorites | Yes |

---

## API Docs to Reference

| File | What it tells us |
|------|-----------------|
| `docs/api/homescreen/save-favorite.md` | Request/response shape for POST `/favorites`, `favorites` table schema (JSONB `recommendation_snapshot`), 409 on duplicate |
| `docs/api/homescreen/delete-favorite.md` | Path param `favoriteId`, ownership check (403), 404 on missing |
| `docs/api/homescreen/README.md` | Service overview, all homescreen endpoints listed |
| `docs/api/homescreen/get-combos.md` | Combo shape (`id`, `name`, `items[]`, totals, `diningHall`) — this is what gets snapshotted into favorites |
| `docs/db-doc.md` | Existing DB tables (`foods`, `food_nutrition`, `food_flags`, `menu_items`) |

---

## Database: `favorites` Table (new)

Based on `save-favorite.md` notes:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key — the `favoriteId` used in DELETE |
| `user_id` | UUID | FK → `users.id` — the user who saved it |
| `combo_id` | UUID | The combo that was favorited |
| `food_id` | INT \| NULL | Optional FK → `foods.id` — for individual food favorites (null for combos) |
| `recommendation_snapshot` | JSONB | Snapshot of combo details at time of save |
| `created_at` | TIMESTAMPTZ | When the favorite was saved |

- Unique constraint on (`user_id`, `combo_id`) to prevent duplicates (drives the 409 response)

---

## Files to Create

| File | Purpose |
|------|---------|
| `app/models/favorite.py` | SQLAlchemy model for `favorites` table |
| `app/schemas/favorite.py` | Pydantic request/response schemas (`SaveFavoriteRequest`, `SaveFavoriteResponse`, `MessageResponse` reuse) |
| `app/services/favorite_service.py` | Business logic: save favorite (with duplicate check), delete favorite (with ownership check) |
| `app/routers/favorite.py` | FastAPI router — `POST /favorites`, `DELETE /favorites/{favorite_id}` |

## Existing Files to Modify

| File | Change |
|------|--------|
| `app/main.py` | Register the new `favorite` router |
| `app/models/__init__.py` | Export `Favorite` model (so `Base.metadata.create_all` picks it up) |

---

## Key Implementation Notes

- JWT required on both endpoints — reuse `get_current_user` dependency from `app/dependencies.py`
- POST saves a JSONB snapshot of the combo so it persists even after menus rotate
- DELETE verifies `favorite.user_id == current_user` before deleting (403 if mismatch)
- 409 Conflict on duplicate combo save
- 404 Not Found on delete if `favoriteId` doesn't exist

#########

## Frontend Button Audit — What the UI Actually Has

Traced every `TouchableOpacity` / interactive element across the HomeScreen flow screens.

### HomeScreenMain.tsx (main home screen)

| # | Button / Interactive Element | What it does | Location |
|---|------------------------------|--------------|----------|
| 1 | **Date pills** (Sun–Sat strip) | Selects a date — expects to reload recommendations for that day | `DateStrip` component |
| 2 | **Today's Goals card** (tap to expand/collapse) | Shows calorie + macro progress bars | `GoalsCard` component |
| 3 | **Hall card** (tap to expand) | Expands to show combo detail: item list, macro pills | `HallCard` component |
| 4 | **"Log This Meal"** button (inside expanded hall card) | Navigates to `Meal` screen (HomeScreenMeal) with the selected combo | `HallCard` expanded detail |

### HomeScreenMeal.tsx (food swap / meal detail)

| # | Button / Interactive Element | What it does | Location |
|---|------------------------------|--------------|----------|
| 5 | **Swipe-to-swap** on each food row | Opens alternative picker — user can replace an item in the combo | `SwipeableFoodItem` |
| 6 | **Alternative food card** (in picker) | Selects a substitute food item | `FoodCard` inside picker |
| 7 | **"Log This Meal"** button | Navigates to `Confirm` screen (HomeScreenConfirm) — submits the final meal | Bottom of screen |

### HomeScreenConfirm.tsx (confirmation / logged state)

| # | Button / Interactive Element | What it does | Location |
|---|------------------------------|--------------|----------|
| 8 | **"Continue"** button | Navigates to `Add` screen (HomeScreenAdd) — proceed to add extras | Bottom of hero card |

### HomeScreenAdd.tsx (add extra foods to meal)

| # | Button / Interactive Element | What it does | Location |
|---|------------------------------|--------------|----------|
| 9 | **Close (✕)** button | `navigation.popToTop()` — back to main home | Top-right header |
| 10 | **Meal option cards** (2×2 grid: Scrambled Eggs, Pancakes, Avocado Toast, Yogurt Parfait) | Selects an additional meal item to add | Options grid |
| 11 | **Quick add-on chips** (Banana, Latte, OJ, Toast) | Adds a quick snack/drink item | Horizontal scroll row |

---

## Do the Planned APIs Cover These Buttons?

The today-plan only scopes **POST /favorites** and **DELETE /favorites/:favoriteId**. But looking at the buttons above, **none of them** are a "star" or "save to favorites" action. The buttons the frontend actually has today are about:

1. **Browsing combos** (date strip, hall cards)
2. **Swapping items** in a combo
3. **Logging a meal** (the "Log This Meal" button)
4. **Adding extra foods** after logging

### Verdict on the favorites plan

The favorites API (`POST /favorites`, `DELETE /favorites/:favoriteId`) **is still valid** — it maps to the `POST /save-menu` and `DELETE /delete-menu` endpoints in the api-doc. However, **the frontend hasn't wired up a star/heart button on the hall cards yet**. That's fine — the backend can be built ahead of the UI. But it means we can't end-to-end test favorites from the frontend today.

### APIs that the existing buttons actually need RIGHT NOW

These are the APIs the buttons above are actively calling (or will need to call once connected):

| Priority | Button(s) | API Needed | Endpoint (from api-doc) | Status |
|----------|-----------|------------|-------------------------|--------|
| **P0** | Date pills (#1), Hall cards (#3) | Fetch today's combos per dining hall | `GET /recommendations/combo?date=YYYY-MM-DD` | Not built |
| **P0** | Today's Goals card (#2) | Fetch calorie/macro progress | `GET /goals/today?date=YYYY-MM-DD` | Not built |
| **P0** | "Log This Meal" (#4, #7) | Log the selected combo | `POST /log-meal` | Not built |
| **P1** | Swipe-to-swap (#5, #6) | Fetch alternative items for a food | `GET /recommendations/combo` (items already include `alternatives` — may need a dedicated swap endpoint or just client-side from combo data) | Unclear |
| **P1** | Meal option cards (#10), Quick add-ons (#11) | Fetch add-on options / log additional items | `GET /meals/quick-addons` + `POST /log-meal` (with extra items) | Not built |
| **P2** | "Continue" (#8), Close (#9) | Pure navigation — no API needed | — | N/A |
| **P2** | Star/favorite (not in UI yet) | Save/remove favorite | `POST /save-menu` / `DELETE /delete-menu` | **This is what today-plan covers** |

---

## Recommendation for Today's Session

Since the today-plan scopes favorites — go ahead and build that. But be aware:

- **The highest-impact APIs** for the frontend are `GET /recommendations/combo`, `GET /goals/today`, and `POST /log-meal` — those power the core flow (buttons #1–#7).
- **Favorites** (buttons not yet in UI) is a valid backend-first build but **won't have a frontend consumer today**.
- **No additional APIs are needed** beyond what's in the api-doc — the doc already covers every button's needs.

### TL;DR

| What | Answer |
|------|--------|
| Are the predicted favorites buttons correct? | The API is valid, but the frontend **doesn't have a favorite/star button yet** — it's backend-ahead work |
| Do we need further APIs? | Not new ones — but `GET /recommendations/combo`, `GET /goals/today`, and `POST /log-meal` are what the existing buttons actually need |
| Should we still build favorites today? | Yes — it's scoped, simple, and gets a table + router pattern established for the rest |
