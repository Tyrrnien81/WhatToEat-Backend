# DELETE /community/posts/:postId/comments/:commentId

Delete your own comment on a community post.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post |
| `commentId` | string | The unique ID of the comment to delete |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "message": "Comment deleted successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
| `403 Forbidden` | Cannot delete another user's comment |
| `404 Not Found` | Comment not found |

## Notes

- Only the comment author can delete their own comment.
