# 7. Profile

Manages the authenticated user's profile information and meal history log.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/users/me` | Retrieve the current user's full profile | Yes |
| GET | `/users/me/meal-logs` | Retrieve the user's historical meal log (all previously recorded meals) | Yes |
| POST | `/users/me/meal-logs` | Manually add a past meal entry to the user's meal log | Yes |
| PATCH | `/users/me` | Update the user's profile information (name, preferences, etc.) | Yes |
