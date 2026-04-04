# DELETE /users/me

Permanently delete the authenticated user's account and all associated data.

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

## Notes

- This action is **irreversible**. All associated data is permanently removed, including:
  - User profile and preferences
  - Questionnaire responses
  - Food log entries
  - Community posts, likes, and comments
  - Saved favorites
- The client should prompt the user for confirmation before calling this endpoint.
