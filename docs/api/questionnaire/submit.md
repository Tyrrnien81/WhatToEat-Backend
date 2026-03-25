# POST /questionnaire

Save the user's initial onboarding questionnaire data. This is called once after the user's first sign-in to collect personal and dietary information that powers the meal recommendation engine.

## Request

### Headers

```http
Authorization: Bearer <JWT token>
```

### Body

```json
{
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "weight": 70,
  "goal_weight": 65,
  "diet_type": "vegetarian",
  "dislikes": ["mushrooms", "olives"],
  "allergens": ["peanuts", "shellfish"]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `birthday` | string (date) | Yes | User's date of birth (`YYYY-MM-DD`) |
| `gender` | string | Yes | `male`, `female`, or `other` |
| `height` | number | Yes | Height in cm |
| `weight` | number | Yes | Current weight in kg |
| `goal_weight` | number | Yes | Target weight in kg |
| `diet_type` | string | Yes | One of: `balanced`, `high_protein`, `vegan`, `vegetarian` |
| `dislikes` | string[] | No | List of disliked foods (e.g. `["mushrooms", "olives"]`) |
| `allergens` | string[] | No | List of allergens (e.g. `["peanuts", "shellfish"]`) |

## Response

### Success (`201 Created`)

```json
{
  "message": "Questionnaire saved successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing or invalid fields (e.g. invalid date format, unknown diet_type) |
| `401 Unauthorized` | Invalid or missing JWT token |
| `409 Conflict` | Questionnaire already submitted — use `PATCH /users/me/preferences` to update |

## Notes

- Data is stored in the `user_preferences` table, linked to the user via `user_id` (one-to-one relationship).
- Target daily calories, protein, carbs, and fat are auto-calculated from the user's profile data using standard nutrition formulas.
- This endpoint should only be called once during onboarding. Subsequent updates should use `PATCH /users/me/preferences`.
