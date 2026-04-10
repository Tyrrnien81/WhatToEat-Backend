# GET /users/me/preferences

Retrieve the current user's saved dietary preferences and personal information. Used to populate the preferences/settings screen and to power the recommendation algorithm.

> **Status:** ✅ Implemented — `app/routers/questionnaire.py` → `app/services/questionnaire_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175.0,
  "weight": 70.0,
  "goal_weight": 65.0,
  "diet_type": "balanced",
  "dislikes": ["Mushroom", "Eggplant"],
  "allergens": ["peanuts", "dairy"],
  "favorite_dining_halls": ["gordon", "fourlakes", "liz"],
  "target_calories": 2450,
  "target_protein_g": 153,
  "target_carbs_g": 276,
  "target_fat_g": 82
}
```

| Field | Type | Description |
| --- | --- | --- |
| `birthday` | string (date) | User's date of birth |
| `gender` | string | `male`, `female`, `other`, or `prefer` |
| `height` | number | Height in cm (always metric regardless of original submission unit) |
| `weight` | number | Current weight in kg |
| `goal_weight` | number | Target weight in kg |
| `diet_type` | string | `balanced`, `high_protein`, `vegan`, or `vegetarian` |
| `dislikes` | string[] | List of disliked foods |
| `allergens` | string[] | List of allergen IDs |
| `favorite_dining_halls` | string[] | Ordered list of preferred dining hall IDs |
| `target_calories` | number | Auto-calculated daily calorie target |
| `target_protein_g` | number | Auto-calculated daily protein target (grams) |
| `target_carbs_g` | number | Auto-calculated daily carbohydrate target (grams) |
| `target_fat_g` | number | Auto-calculated daily fat target (grams) |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid or missing JWT token |
| `404 Not Found` | Preferences not yet set — user has not completed the questionnaire |

## Notes

- The nutrition targets (`target_calories`, etc.) are derived from the user's profile data and may be recalculated when preferences are updated.
- Height and weight are always returned in metric units (cm, kg), regardless of what unit was used during submission.
- This data is read from the `user_preferences` table joined on the authenticated user's `user_id`.
