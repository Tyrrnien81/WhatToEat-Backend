# 7. Profile

Manages the authenticated user's profile information, account settings, and food consumption log.

## Endpoints

| Method | Endpoint | Description | Auth | Docs |
| --- | --- | --- | --- | --- |
| GET | `/users/me` | Retrieve the current user's profile | Yes | [get-profile.md](get-profile.md) |
| PATCH | `/users/me` | Update profile information | Yes | [update-profile.md](update-profile.md) |
| DELETE | `/users/me` | Delete the user's account | Yes | [delete-account.md](delete-account.md) |
| POST | `/users/me/avatar` | Upload a profile photo | Yes | [upload-avatar.md](upload-avatar.md) |
| POST | `/users/me/change-password` | Change the user's password | Yes | [change-password.md](change-password.md) |
| GET | `/users/me/food-log` | Retrieve food consumption history | Yes | [get-food-log.md](get-food-log.md) |
| POST | `/users/me/food-log` | Manually add a food log entry | Yes | [add-food-log.md](add-food-log.md) |
| DELETE | `/users/me/food-log/:entryId` | Delete a food log entry | Yes | [delete-food-log.md](delete-food-log.md) |
| GET | `/users/me/food-log/summary` | Retrieve nutrition summary and streaks | Yes | [food-log-summary.md](food-log-summary.md) |

## Implementation Notes

- User profile data is stored in the `users` table with fields for personal info, dietary preferences, and body metrics.
- The food log is stored in a dedicated table linked to the user, with each entry containing food name, macros, and timestamp.
- Profile photos are uploaded to AWS S3 and the URL is stored in the `users.avatar_url` column.
- Password changes require the current password for verification.
- Account deletion is permanent and cascades to all associated data (food logs, community posts, questionnaire data).
