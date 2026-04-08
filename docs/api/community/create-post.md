# POST /community/posts

Create a new community post.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Content-Type` | `application/json` | Yes |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | ID of the user creating the post |

### Body (`application/json`)

```json
{
  "content": "Amazing grilled salmon today!",
  "hallTag": "gordon-avenue-market",
  "imageUrl": "https://s3.amazonaws.com/whattoeat/posts/abc123.jpg"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `content` | string | Yes | Post text content |
| `hallTag` | string | No | Dining hall tag |
| `imageUrl` | string | No | Already-uploaded image URL |

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
| `404 Not Found` | User not found |
| `422 Unprocessable Entity` | Validation error or blank content |

## Notes

- The backend trims content and rejects blank values.
- Image upload is handled outside this endpoint; send the final URL in `imageUrl`.
