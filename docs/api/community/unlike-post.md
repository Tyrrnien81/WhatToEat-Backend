# DELETE /community/posts/:postId/like

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

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "message": "Post unliked",
  "likesCount": 12
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

- If the user has not previously liked the post, the request succeeds with no side effects.
