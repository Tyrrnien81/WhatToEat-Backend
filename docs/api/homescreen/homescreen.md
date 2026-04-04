# 3. Homescreen

Powers the main screen with personalized menu recommendations, daily nutrition tracking, and meal logging.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/combo` | Get algorithmically recommended meal combos based on user preferences and available menus | Yes | ✅ Built |
| GET | `/goals/daily` | Retrieve today's nutrition goal progress (calories, macros) for the status bar | Yes | ✅ Built |
| GET | `/menus/summary` | Get today's highlighted menu items per dining hall, filtered by user preferences | Yes | ✅ Built |
| POST | `/meals/log` | Log a meal with food items and snapshotted nutrition data | Yes | ✅ Built |
| POST | `/favorites` | Save a recommended combo to the user's favorites | Yes | Not built |
| DELETE | `/favorites/:favoriteId` | Remove a previously saved combo from the user's favorites | Yes | Not built |
