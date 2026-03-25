# GET /users/me/preferences

Retrieve the current user's saved dietary preferences and personal information. Used to populate the preferences/settings screen and to power the recommendation algorithm.

## Request

### Headers

```http
Authorization: Bearer <JWT token>
```

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "weight": 70,
  "goal_weight": 65,
  "diet_type": "vegetarian",
  "dislikes": ["mushrooms", "olives"],
  "allergens": ["peanuts", "shellfish"],
  "target_calories": 2000,
  "target_protein_g": 120,
  "target_carbs_g": 250,
  "target_fat_g": 65
}
```

| Field | Type | Description |
| --- | --- | --- |
| `birthday` | string (date) | User's date of birth |
| `gender` | string | `male`, `female`, or `other` |
| `height` | number | Height in cm |
| `weight` | number | Current weight in kg |
| `goal_weight` | number | Target weight in kg |
| `diet_type` | string | `balanced`, `high_protein`, `vegan`, or `vegetarian` |
| `dislikes` | string[] | List of disliked foods |
| `allergens` | string[] | List of allergens |
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
- This data is read from the `user_preferences` table joined on the authenticated user's `user_id`.
