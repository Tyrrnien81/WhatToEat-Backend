# Profile API Overview

This document provides a quick reference to all Profile endpoints. For detailed request/response specifications, see the individual endpoint docs linked below.

## All Endpoints

| # | Method | Endpoint | Description | Docs |
| --- | --- | --- | --- | --- |
| 1 | GET | `/users/me` | Get full profile | [get-profile.md](get-profile.md) |
| 2 | PATCH | `/users/me` | Update profile | [update-profile.md](update-profile.md) |
| 3 | DELETE | `/users/me` | Delete account | [delete-account.md](delete-account.md) |
| 4 | POST | `/users/me/avatar` | Upload avatar | [upload-avatar.md](upload-avatar.md) |
| 5 | POST | `/users/me/change-password` | Change password | [change-password.md](change-password.md) |
| 6 | GET | `/users/me/food-log` | Get food log | [get-food-log.md](get-food-log.md) |
| 7 | POST | `/users/me/food-log` | Add food log entry | [add-food-log.md](add-food-log.md) |
| 8 | DELETE | `/users/me/food-log/{entry_id}` | Delete food log entry | [delete-food-log.md](delete-food-log.md) |
| 9 | GET | `/users/me/food-log/summary` | Nutrition summary | [food-log-summary.md](food-log-summary.md) |
