# Dining Halls Service

Provides read-only access to UW-Madison dining hall information, station listings, and daily menus. All endpoints are public — no authentication required.

## Endpoints

| Method | Endpoint | File | Description | JWT Required |
| --- | --- | --- | --- | --- |
| GET | `/dining-halls` | [list-halls.md](list-halls.md) | List all dining halls | No |
| GET | `/dining-halls/:hallId` | [get-hall.md](get-hall.md) | Get details for a specific hall | No |
| GET | `/dining-halls/:hallId/stations` | [get-stations.md](get-stations.md) | List stations in a hall | No |
| GET | `/dining-halls/:hallId/menus` | [get-menus.md](get-menus.md) | Get menu items by station | No |
| GET | `/dining-halls/full` | [get-full.md](get-full.md) | Get frontend-oriented nested hall/day/menu payload | No |

## Implementation Notes

- Dining hall data originates from the Nutrislice API and is ingested daily via APScheduler.
- Each dining hall has a unique `external_restaurant_id` mapped from the Nutrislice data source.
- Menu data is stored in the `menu_snapshots`, `menu_sections`, `menu_section_items`, and `foods` tables.
- `/dining-halls/full` can optionally include user-specific favorite flags via `user_id` query parameter.
