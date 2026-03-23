# GET /community/posts/:postId/comments

Retrieve a paginated list of comments on a community post.

## Request

### Headers

None required (public endpoint).

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post |

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `page` | number | No | `1` | Page number for pagination |
| `limit` | number | No | `20` | Number of comments per page |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "comments": [
    {
      "id": "comment-uuid",
      "author": {
        "id": "user-uuid",
        "name": "John Doe"
      },
      "body": "Looks delicious! Which station was this from?",
      "createdAt": "2026-03-18T13:00:00Z"
    }
  ],
  "total": 3,
  "page": 1,
  "limit": 20
}
```

| Field | Type | Description |
| --- | --- | --- |
| `comments` | array | List of comments |
| `comments[].id` | string | Comment unique identifier |
| `comments[].author` | object | Comment author info |
| `comments[].author.id` | string | Author's user ID |
| `comments[].author.name` | string | Author's display name |
| `comments[].body` | string | Comment text |
| `comments[].createdAt` | string | ISO 8601 creation timestamp |
| `total` | number | Total number of comments on this post |
| `page` | number | Current page number |
| `limit` | number | Comments per page |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Post not found |

## Notes

- Comments are returned in chronological order (oldest first).
