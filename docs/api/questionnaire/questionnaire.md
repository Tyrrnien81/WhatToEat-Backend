# 2. Questionnaire

Collects and manages user preference data used for personalized meal recommendations. Submitted during onboarding and editable from the profile.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/questionnaire` | Save initial user preferences (birthday, gender, height, weight, goal weight, diet type, dislikes, allergens) | Yes |
| GET | `/users/me/preferences` | Retrieve the current user's saved dietary preferences | Yes |
| PATCH | `/users/me/preferences` | Update the user's dietary preferences | Yes |
