# 4. Dining Hall

Provides read-only access to dining hall information, station listings, and daily menus.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/dining-halls` | List all available dining halls | No |
| GET | `/dining-halls/:hallId` | Get details for a specific dining hall | No |
| GET | `/dining-halls/:hallId/stations` | List all food stations within a specific dining hall | No |
| GET | `/dining-halls/:hallId/menus` | Get the menu items available at each station | No |
| GET | `/dining-halls/full` | Get a frontend-ready nested hall/day/menu structure | No |
