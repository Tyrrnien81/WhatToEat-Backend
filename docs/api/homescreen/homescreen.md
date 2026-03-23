# 3. Homescreen

Powers the main screen with personalized menu recommendations, daily nutrition tracking, and menu favoriting.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/recommendations/combos` | Get algorithmically recommended meal combos based on user preferences and available menus | Yes |
| GET | `/goals/daily` | Retrieve today's nutrition goal progress (calories, macros) for the status bar | Yes |
| GET | `/menus/summary` | Get today's highlighted menu items per dining hall, filtered by user preferences | Yes |
| POST | `/favorites` | Save a recommended combo to the user's favorites | Yes |
| DELETE | `/favorites/:favoriteId` | Remove a previously saved combo from the user's favorites | Yes |
