# POST /community/posts

Create a new community post with a food photo and caption text.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `multipart/form-data` | Yes |

### Body (`multipart/form-data`)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `image` | file | Yes | Photo of the food. Supported formats: JPEG, PNG. |
| `text` | string | Yes | Post caption or description |
| `hallId` | string | No | Associated dining hall ID |

## Response

### Success (`201 Created`)

```json
{
  "id": "post-uuid",
  "message": "Post created successfully"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier for the new post |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing required fields (image or text) |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- The uploaded image is stored in AWS S3 under the `posts/` prefix, and the resulting URL is saved in the `community_posts.image_url` column.
- The `hallId` field links the post to a specific dining hall for filtering purposes.
