# DELETE /favorites/:favoriteId

Remove a previously saved combo from the user's favorites. Used when the user taps the unlike/unheart button on a previously favorited combo.

## Request

### Headers

None required.

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `favoriteId` | string (UUID) | The ID of the favorite record to remove |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User ID deleting the favorite |

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
| `403 Forbidden` | Cannot delete another user's favorite |
| `404 Not Found` | Favorite not found (already removed or invalid ID) |

## Notes

- The favorite is permanently deleted from the `favorites` table.
- Only the user who created the favorite can delete it.
