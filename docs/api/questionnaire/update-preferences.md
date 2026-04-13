# PATCH /users/me/preferences

Partially update the current user's dietary preferences. Only the fields included in the request body are updated — omitted fields remain unchanged.

> **Status:** ✅ Implemented — `app/routers/questionnaire.py` → `app/services/questionnaire_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body (partial update)

```json
{
  "weight": 150,
  "weight_unit": "lb",
  "goal_weight": 140,
  "dislikes": ["Mushroom"],
  "favorite_dining_halls": ["liz", "gordon"]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `birthday` | string (date) | No | Updated date of birth (`YYYY-MM-DD`) |
| `gender` | string | No | `male`, `female`, `other`, or `prefer` |
| `height` | number | No | Updated height in specified unit |
| `height_unit` | string | No | `cm` (default) or `ft` |
| `weight` | number | No | Updated weight in specified unit |
| `weight_unit` | string | No | `kg` (default) or `lb` |
| `goal_weight` | number | No | Updated target weight in specified unit |
| `diet_type` | string | No | `balanced`, `high_protein`, `vegan`, or `vegetarian` |
| `dislikes` | string[] | No | Updated full list of disliked foods (replaces existing list) |
| `allergens` | string[] | No | Updated full list of allergen IDs (replaces existing list) |
| `favorite_dining_halls` | string[] | No | Updated ordered list of up to 3 dining hall IDs (replaces existing list) |

## Response

### Success (`200 OK`)

```json
{
  "message": "Preferences updated successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Invalid field values (e.g. negative weight, unknown diet_type, unknown allergen) |
| `401 Unauthorized` | Invalid or missing JWT token |
| `404 Not Found` | Preferences not yet set — user must complete the questionnaire first |

## Notes

- Array fields (`dislikes`, `allergens`, `favorite_dining_halls`) are replaced entirely, not merged. To add an item, the client must send the full updated list.
- When `weight`, `goal_weight`, `height`, or `diet_type` change, the nutrition targets (`target_calories`, `target_protein_g`, etc.) are automatically recalculated.
- Height is converted to cm and weight to kg before storage when imperial units are specified via `height_unit` or `weight_unit`.
- This endpoint updates the `user_preferences` table row linked to the authenticated user.
