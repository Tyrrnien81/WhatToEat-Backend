# GET /community/posts/:postId

Retrieve a single community post by its unique ID, including full details, like count, and comment count.

## Request

### Headers

None required (public endpoint).

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "id": "post-uuid",
  "author": {
    "id": "user-uuid",
    "name": "Jane Doe",
    "avatarUrl": "https://s3.amazonaws.com/whattoeat/avatars/user123.jpg"
  },
  "text": "Amazing grilled salmon today!",
  "imageUrl": "https://s3.amazonaws.com/whattoeat/posts/abc123.jpg",
  "diningHall": "Gordon Avenue Market",
  "likesCount": 12,
  "commentsCount": 3,
  "createdAt": "2026-03-18T12:30:00Z"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Post unique identifier |
| `author` | object | Post author info |
| `author.id` | string | Author's user ID |
| `author.name` | string | Author's display name |
| `author.avatarUrl` | string | Author's profile photo URL |
| `text` | string | Post caption or description |
| `imageUrl` | string | URL of the uploaded food photo |
| `diningHall` | string | Associated dining hall name |
| `likesCount` | number | Total number of likes |
| `commentsCount` | number | Total number of comments |
| `createdAt` | string | ISO 8601 creation timestamp |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Post not found |
