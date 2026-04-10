# DELETE /community/posts/:postId

Delete a community post authored by the current user.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to delete |

### Query Parameters

None.

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "message": "Post deleted successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT |
| `403 Forbidden` | Cannot delete another user's post |
| `404 Not Found` | Post not found |

## Notes

- Only the post author can delete their own post.
- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
- Deleting a post cascades to remove associated post likes, replies, and reply likes.
