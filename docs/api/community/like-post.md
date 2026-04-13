# POST /community/posts/:postId/likes

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

### Query Parameters

None.

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "liked": true,
  "likeCount": 13,
  "message": "Post liked"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `liked` | boolean | Whether the post is liked by current user |
| `likeCount` | number | Updated like count for the post |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT |
| `404 Not Found` | User not found or post not found |

## Notes

- If already liked, response is still `200` with `message: "Post already liked"`.
- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
