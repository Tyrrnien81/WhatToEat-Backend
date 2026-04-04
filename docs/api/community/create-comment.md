# POST /community/posts/:postId/comments

Add a comment to a community post.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to comment on |

### Body

```json
{
  "body": "Looks delicious! Which station was this from?"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `body` | string | Yes | The comment text. Must not be empty. |

## Response

### Success (`201 Created`)

```json
{
  "id": "comment-uuid",
  "message": "Comment added successfully"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier for the new comment |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Empty comment body |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Post not found |
