# POST /questionnaire

Save the user's initial onboarding questionnaire data. This is called once after the user's first sign-in to collect personal and dietary information that powers the meal recommendation engine.

> **Status:** ✅ Implemented — `app/routers/questionnaire.py` → `app/services/questionnaire_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body

```json
{
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "height_unit": "cm",
  "weight": 70.0,
  "weight_unit": "kg",
  "goal_weight": 65.0,
  "diet_type": "balanced",
  "dislikes": ["Mushroom", "Eggplant"],
  "allergens": ["peanuts", "dairy"],
  "favorite_dining_halls": ["gordon", "fourlakes", "liz"]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `birthday` | string (date) | Yes | User's date of birth (`YYYY-MM-DD`) |
| `gender` | string | Yes | `male`, `female`, `other`, or `prefer` |
| `height` | number | Yes | Height value in the specified unit |
| `height_unit` | string | No | `cm` (default) or `ft`. When `ft`, height is total inches (e.g. 70 for 5'10") |
| `weight` | number | Yes | Current weight in the specified unit |
| `weight_unit` | string | No | `kg` (default) or `lb` |
| `goal_weight` | number | Yes | Target weight in the same unit as `weight_unit` |
| `diet_type` | string | Yes | `balanced`, `high_protein`, `vegan`, or `vegetarian`. Alias `highprotein` is accepted |
| `dislikes` | string[] | No | List of disliked foods by display name (e.g. `["Broccoli", "Chicken"]`) |
| `allergens` | string[] | No | List of allergen IDs. Valid: `soy`, `peanuts`, `treenuts`, `halal`, `kosher`, `dairy`, `gluten`, `shellfish`, `fish`, `egg`, `other`. Send `["none"]` for no allergens |
| `favorite_dining_halls` | string[] | No | Ordered list of up to 3 dining hall IDs: `gordon`, `fourlakes`, `liz`, `rheta`, `carson`, `lowell` |

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
| `400 Bad Request` | Missing or invalid fields (e.g. invalid date format, unknown diet_type, unknown allergen) |
| `401 Unauthorized` | Invalid or missing JWT token |
| `409 Conflict` | Questionnaire already submitted — use `PATCH /users/me/preferences` to update |

## Notes

- Data is stored in the `user_preferences` table, linked to the user via `user_id` (one-to-one relationship).
- Height is converted to cm and weight/goal_weight to kg before storage when imperial units are used.
- Target daily calories, protein, carbs, and fat are auto-calculated using the Mifflin-St Jeor equation with a moderate activity multiplier (1.55).
- Macro ratios depend on `diet_type`: balanced (25/45/30), high_protein (40/35/25), vegan (15/55/30), vegetarian (20/50/30).
- This endpoint should only be called once during onboarding. Subsequent updates should use `PATCH /users/me/preferences`.
