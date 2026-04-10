# DELETE /users/me/food-log/{entry_id}

Delete a specific food log entry.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `entry_id` | number | The unique ID of the food log entry to delete |

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

- Users can only delete their own food log entries. Ownership is verified by joining `meal_log_items` → `meal_logs` → `user_id`.
- If the deleted entry was the last item in its parent `meal_log`, the empty meal log is also removed.
