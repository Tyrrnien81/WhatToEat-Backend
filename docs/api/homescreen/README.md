# Homescreen Service

Powers the main screen with personalized menu recommendations, daily nutrition goal tracking, dining hall menu summaries, and menu favoriting. All endpoints require authentication to deliver personalized results.

## Endpoints

| Method | Endpoint | File | Description | JWT Required |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/combos` | [get-combos.md](get-combos.md) | Get personalized meal combo recommendations | Yes |
| GET | `/goals/daily` | [get-daily-goals.md](get-daily-goals.md) | Get today's nutrition goal progress | Yes |
| GET | `/menus/summary` | [get-menu-summary.md](get-menu-summary.md) | Get today's highlighted menus per dining hall | Yes |
| POST | `/favorites` | [save-favorite.md](save-favorite.md) | Save a combo to favorites | Yes |
| DELETE | `/favorites/:favoriteId` | [delete-favorite.md](delete-favorite.md) | Remove a combo from favorites | Yes |

## Implementation Notes

- All homescreen endpoints support a `?date=YYYY-MM-DD` query parameter (the UI shows a 5-day date strip).
- Recommendation combos are generated using a linear programming optimizer that matches user nutrition targets.
- Menu summaries are filtered by the user's allergens, dislikes, and diet type.
