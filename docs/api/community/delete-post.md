# DELETE /community/posts/:postId

Delete a community post authored by the current user. Removes the post, its image from S3, and all associated likes and comments.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to delete |

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
| `401 Unauthorized` | Missing or invalid JWT token |
| `403 Forbidden` | Cannot delete another user's post |
| `404 Not Found` | Post not found |

## Notes

- Only the post author can delete their own post.
- Deleting a post cascades to remove all associated likes and comments.
- The post image is also deleted from S3 storage.
