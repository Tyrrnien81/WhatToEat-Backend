# DELETE /community/posts/:postId

Delete a community post authored by the current user.

## Request

### Headers

None required.

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to delete |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | Post author's user ID |

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
| `403 Forbidden` | Cannot delete another user's post |
| `404 Not Found` | Post not found |

## Notes

- Only the post author can delete their own post.
- Deleting a post cascades to remove associated post likes, replies, and reply likes.
