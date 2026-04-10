# GET /community/posts

Retrieve a paginated feed of community posts.

## Request

### Headers

Public endpoint. Optionally send `Authorization: Bearer <JWT>` so each post includes accurate `likedByMe` for the authenticated user (`sub`). Without auth, `likedByMe` is always `false`.

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `page` | number | No | `1` | Page number for pagination |
| `limit` | number | No | `20` | Number of posts per page |
| `q` | string | No | — | Search keyword for post content |
| `hallTag` | string | No | — | Filter by dining hall tag (exact match) |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "page": 1,
  "limit": 20,
  "hasMore": true,
  "posts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "author": {
        "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "name": "Jane Doe"
      },
      "content": "Amazing grilled salmon today!",
      "hallTag": "gordon-avenue-market",
      "imageUrl": "https://s3.amazonaws.com/whattoeat/posts/abc123.jpg",
      "likeCount": 12,
      "replyCount": 3,
      "createdAt": "2026-04-07T12:30:00",
      "likedByMe": false
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `posts` | array | List of community posts |
| `posts[].id` | string | Post unique identifier |
| `posts[].author` | object | Post author info |
| `posts[].author.id` | string | Author's user ID |
| `posts[].author.name` | string | Author's display name |
| `posts[].content` | string | Post content |
| `posts[].hallTag` | string \| null | Dining hall tag associated with the post |
| `posts[].imageUrl` | string | URL of the uploaded food photo (S3) |
| `posts[].likeCount` | number | Total number of likes |
| `posts[].replyCount` | number | Total number of replies |
| `posts[].createdAt` | string | ISO 8601 creation timestamp |
| `posts[].likedByMe` | boolean | Whether the current user liked this post |
| `page` | number | Current page number |
| `limit` | number | Posts per page |
| `hasMore` | boolean | Whether there are more posts beyond current page |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid or expired JWT (only if `Authorization` was sent) |

## Notes

- Posts are returned in reverse chronological order (newest first).
- Without a valid JWT, `likedByMe` is always `false`. Local dev only: if the server has `ALLOW_QUERY_USER_ID=true`, `?user_id=` can supply identity when the header is omitted (never use in production).
