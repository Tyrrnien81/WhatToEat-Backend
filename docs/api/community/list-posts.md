# GET /community/posts

Retrieve a paginated feed of community posts including food photos and reviews related to dining halls.

## Request

### Headers

None required (public endpoint).

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `page` | number | No | `1` | Page number for pagination |
| `limit` | number | No | `20` | Number of posts per page |
| `hallId` | string | No | — | Filter posts by dining hall ID |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "posts": [
    {
      "id": "post-uuid",
      "author": {
        "id": "user-uuid",
        "name": "Jane Doe"
      },
      "text": "Amazing grilled salmon today!",
      "imageUrl": "https://s3.amazonaws.com/whattoeat/posts/abc123.jpg",
      "diningHall": "Gordon Avenue Market",
      "likesCount": 12,
      "commentsCount": 3,
      "createdAt": "2026-03-18T12:30:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

| Field | Type | Description |
| --- | --- | --- |
| `posts` | array | List of community posts |
| `posts[].id` | string | Post unique identifier |
| `posts[].author` | object | Post author info |
| `posts[].author.id` | string | Author's user ID |
| `posts[].author.name` | string | Author's display name |
| `posts[].text` | string | Post caption or description |
| `posts[].imageUrl` | string | URL of the uploaded food photo (S3) |
| `posts[].diningHall` | string | Associated dining hall name (if any) |
| `posts[].likesCount` | number | Total number of likes |
| `posts[].commentsCount` | number | Total number of comments |
| `posts[].createdAt` | string | ISO 8601 creation timestamp |
| `total` | number | Total number of posts matching the query |
| `page` | number | Current page number |
| `limit` | number | Posts per page |

### Errors

None expected.

## Notes

- Posts are returned in reverse chronological order (newest first).
- The `hallId` filter allows the client to show posts relevant to a specific dining hall page.
