# DELETE /users/me

Permanently delete the authenticated user's account and all associated data.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

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
  "message": "Account deleted successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Profile not found |

## Notes

- This action is **irreversible**. All associated data is permanently removed, including:
  - User profile and preferences
  - Meal logs and meal log items
  - Saved favorites
  - Community posts, replies, and their likes
- Deletions are performed in a single database transaction to ensure consistency.
- The client should prompt the user for confirmation before calling this endpoint.
