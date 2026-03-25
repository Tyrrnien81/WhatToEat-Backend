# DELETE /favorites/:favoriteId

Remove a previously saved combo from the user's favorites. Used when the user taps the unlike/unheart button on a previously favorited combo.

## Request

### Headers

```http
Authorization: Bearer <JWT token>
```

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `favoriteId` | string (UUID) | The ID of the favorite record to remove |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "message": "Favorite removed successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid or missing JWT token |
| `403 Forbidden` | Cannot delete another user's favorite |
| `404 Not Found` | Favorite not found (already removed or invalid ID) |

## Notes

- The favorite is permanently deleted from the `favorites` table.
- Only the user who created the favorite can delete it — the server verifies ownership against the JWT.
