# Homescreen Service

Powers the main screen with personalized menu recommendations, daily nutrition goal tracking, dining hall menu summaries, and meal logging. All endpoints require authentication to deliver personalized results.

## Endpoints

| Method | Endpoint | File | Description | Auth | Status |
| --- | --- | --- | --- | --- | --- |
| GET | `/recommendations/combo` | [get-combos.md](get-combos.md) | Get personalized meal combo recommendations | `user_id` query | ✅ Built |
| GET | `/goals/daily` | [get-daily-goals.md](get-daily-goals.md) | Get today's nutrition goal progress | `user_id` query | ✅ Built |
| GET | `/menus/summary` | [get-menu-summary.md](get-menu-summary.md) | Get today's highlighted menus per dining hall | `user_id` query | ✅ Built |
| POST | `/meals/log` | [log-meal.md](log-meal.md) | Log a meal with food items | `user_id` query | ✅ Built |
| POST | `/favorites` | [save-favorite.md](save-favorite.md) | Save a combo to favorites | `user_id` query | ✅ Built |
| DELETE | `/favorites/:favoriteId` | [delete-favorite.md](delete-favorite.md) | Remove a combo from favorites | `user_id` query | ✅ Built |
| GET | `/recommendations/addons` | [get-addons.md](get-addons.md) | Get addon recommendations for the selected meal period | `user_id` query | ✅ Built |

## Implementation Notes

- All homescreen endpoints support a `?date=YYYY-MM-DD` query parameter (the UI shows a 5-day date strip).
- All homescreen endpoints currently require `user_id` as a query parameter.
- Recommendation combos are generated using a greedy algorithm that matches user nutrition targets (1/3 of daily goal per meal).
- Menu summaries are filtered by the user's allergens, dislikes, and diet type.
- If `mealType` is not specified on `/recommendations/combo`, the server infers it from the time of day.
- Meal logging finds or creates a `meal_log` entry per user/date/mealType, then appends items with snapshotted nutrition.
