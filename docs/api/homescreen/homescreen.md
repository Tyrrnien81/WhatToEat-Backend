# 3. Homescreen

Powers the main screen with personalized menu recommendations, daily nutrition tracking, and meal logging.

| Method | Endpoint | Description | Auth | Status |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/combo` | Get algorithmically recommended meal combos based on user preferences and available menus | `user_id` query | ✅ Built |
| GET | `/goals/daily` | Retrieve today's nutrition goal progress (calories, macros) for the status bar | `user_id` query | ✅ Built |
| GET | `/menus/summary` | Get today's highlighted menu items per dining hall, filtered by user preferences | `user_id` query | ✅ Built |
| POST | `/meals/log` | Log a meal with food items and snapshotted nutrition data | `user_id` query | ✅ Built |
| POST | `/favorites` | Save a recommended combo to the user's favorites | `user_id` query | ✅ Built |
| DELETE | `/favorites/:favoriteId` | Remove a previously saved combo from the user's favorites | `user_id` query | ✅ Built |
| GET | `/recommendations/addons` | Get add-on recommendations for the selected meal period | `user_id` query | ✅ Built |
