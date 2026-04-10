# DELETE /community/posts/:postId/likes

Remove the current user's like from a community post.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to unlike |

### Query Parameters

None.

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "liked": false,
  "likeCount": 12,
  "message": "Post unliked"
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
| `404 Not Found` | Post not found |

## Notes

- If the user has not previously liked the post, response is still `200` with `message: "Post was not liked"`.
- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
