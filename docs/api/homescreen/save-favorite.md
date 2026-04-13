# POST /favorites

Save a recommended meal combo to the user's favorites. When a user taps the like/heart button on a combo card, this endpoint stores the combo reference for later access.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Query Parameters

None.

### Body

```json
{
  "comboId": "combo-uuid"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `comboId` | string (UUID) | Yes | The ID of the recommended combo to save |

## Response

### Success (`201 Created`)

```json
{
  "id": "favorite-uuid",
  "message": "Combo saved to favorites"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string (UUID) | The created favorite record ID |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT |
| `422 Unprocessable Entity` | Missing required request fields |
| `409 Conflict` | This combo is already in the user's favorites |

## Notes

- The favorite is stored in the `favorites` table with the user's ID and a `recommendation_snapshot` (JSONB) capturing the combo details at the time of saving.
- This ensures the user can still see the combo even if the menu changes the next day.
- The `food_id` field may be null for combo favorites (used for individual food favorites instead).
- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
