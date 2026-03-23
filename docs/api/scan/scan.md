# 5. Scan

Enables food recognition via photo upload. Identifies the food item and returns nutritional data, which can then be logged to the user's meal history.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/scans` | Upload a food photo for recognition; returns identified food name, calories, and nutritional breakdown | Yes |
| POST | `/scans/:scanId/log` | Save the recognized food and its nutritional data to the user's meal log | Yes |
