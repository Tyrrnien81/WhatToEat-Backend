# PATCH /users/me/preferences

Partially update the current user's dietary preferences. Only the fields included in the request body are updated — omitted fields remain unchanged.

## Request

### Headers

```http
Authorization: Bearer <JWT token>
```

### Body (partial update)

```json
{
  "weight": 68,
  "goal_weight": 63,
  "dislikes": ["mushrooms"]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `birthday` | string (date) | No | Updated date of birth |
| `gender` | string | No | `male`, `female`, or `other` |
| `height` | number | No | Updated height in cm |
| `weight` | number | No | Updated current weight in kg |
| `goal_weight` | number | No | Updated target weight in kg |
| `diet_type` | string | No | `balanced`, `high_protein`, `vegan`, or `vegetarian` |
| `dislikes` | string[] | No | Updated full list of disliked foods (replaces existing list) |
| `allergens` | string[] | No | Updated full list of allergens (replaces existing list) |

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
| `400 Bad Request` | Invalid field values (e.g. negative weight, unknown diet_type) |
| `401 Unauthorized` | Invalid or missing JWT token |
| `404 Not Found` | Preferences not yet set — user must complete the questionnaire first |

## Notes

- Array fields (`dislikes`, `allergens`) are replaced entirely, not merged. To add an item, the client must send the full updated list.
- When `weight`, `goal_weight`, `height`, or `diet_type` change, the nutrition targets (`target_calories`, `target_protein_g`, etc.) are automatically recalculated.
- This endpoint updates the `user_preferences` table row linked to the authenticated user.
