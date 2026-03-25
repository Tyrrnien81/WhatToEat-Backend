# POST /community/posts/:postId/like

Like a community post. This operation is idempotent — liking an already-liked post has no additional effect.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to like |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "message": "Post liked",
  "likesCount": 13
}
```

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Confirmation message |
| `likesCount` | number | Updated like count for the post |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Post not found |

## Notes

- Likes are tracked in the `community_likes` table with a unique constraint on (`user_id`, `post_id`).
- If the user has already liked the post, the request succeeds with no side effects (idempotent).
