# DELETE /users/me/food-log/:entryId

Delete a specific food log entry.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `entryId` | string | The unique ID of the food log entry to delete |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "message": "Food log entry deleted successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Entry not found or does not belong to the current user |

## Notes

- Users can only delete their own food log entries.
