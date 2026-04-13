# 7. Profile

Manages the authenticated user's profile information, account settings, and food consumption log.

## Endpoints

| Method | Endpoint | Docs | Description | JWT Required |
| --- | --- | --- | --- | --- |
| GET | `/users/me` | [get-profile.md](get-profile.md) | Retrieve the current user's profile | Yes |
| PATCH | `/users/me` | [update-profile.md](update-profile.md) | Update profile information | Yes |
| DELETE | `/users/me` | [delete-account.md](delete-account.md) | Delete the user's account | Yes |
| POST | `/users/me/avatar` | [upload-avatar.md](upload-avatar.md) | Upload a profile photo | Yes |
| POST | `/users/me/change-password` | [change-password.md](change-password.md) | Change the user's password | Yes |
| GET | `/users/me/food-log` | [get-food-log.md](get-food-log.md) | Retrieve food consumption history | Yes |
| POST | `/users/me/food-log` | [add-food-log.md](add-food-log.md) | Manually add a food log entry | Yes |
| DELETE | `/users/me/food-log/{entry_id}` | [delete-food-log.md](delete-food-log.md) | Delete a food log entry | Yes |
| GET | `/users/me/food-log/summary` | [food-log-summary.md](food-log-summary.md) | Retrieve nutrition summary and streaks | Yes |

## Project Structure (Profile)

```
app/
├── routers/
│   └── profile.py
├── schemas/
│   └── profile.py
├── services/
│   └── profile_service.py
├── models/
│   ├── user.py          # Profile model
│   └── tracking.py      # UserPreference, MealLog, MealLogItem
└── dependencies.py       # get_current_user_id (JWT)
```

| File | Responsibility |
| --- | --- |
| `app/routers/profile.py` | Defines all `/users/me/*` route handlers |
| `app/services/profile_service.py` | Business logic for profile, food log, avatar, and password |
| `app/schemas/profile.py` | Request/response Pydantic models |
| `app/models/user.py` | `Profile` SQLAlchemy model (profiles table) |
| `app/models/tracking.py` | `UserPreference`, `MealLog`, `MealLogItem` models |

## Implementation Notes

- Profile data is assembled from two tables: `profiles` (id, email, name, avatar_url) and `user_preferences` (birthday, gender, height, weight, goal_weight, diet_type).
- `GET /users/me` joins both tables to return the full profile. If no `user_preferences` row exists, preference fields return `null`.
- `PATCH /users/me` updates `profiles.name` and creates/updates the `user_preferences` row for body metric fields.
- Food log entries are stored as `meal_log_items` linked to `meal_logs`. The GET endpoint returns flat entries (not grouped by meal).
- Account deletion cascades across all user-owned data: preferences, meal logs, favorites, community posts/replies/likes.
- Avatar upload stores files locally under `uploads/avatars/` (swap to S3 in production).
- Password change operates through the Supabase Auth Admin API and is unavailable for OAuth-only users.
