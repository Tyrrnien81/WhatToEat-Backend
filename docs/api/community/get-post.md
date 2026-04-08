# GET /community/posts/:postId

Retrieve a single community post by its unique ID, including threaded replies.

## Request

### Headers

None required (public endpoint).

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | No | Current user ID (enables `likedByMe`) |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "post": {
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
  },
  "replies": [
    {
      "id": "e7f0b6fd-43fc-4be2-9308-5f8045bfc3f2",
      "postId": "550e8400-e29b-41d4-a716-446655440000",
      "parentReplyId": null,
      "author": {
        "id": "6ba7b814-9dad-11d1-80b4-00c04fd430c8",
        "name": "John Doe"
      },
      "content": "Looks great, which station was this from?",
      "likeCount": 2,
      "likedByMe": false,
      "createdAt": "2026-04-07T13:00:00",
      "replies": [
        {
          "id": "890da98d-b64b-4fb9-a38d-bf8ea30783b5",
          "postId": "550e8400-e29b-41d4-a716-446655440000",
          "parentReplyId": "e7f0b6fd-43fc-4be2-9308-5f8045bfc3f2",
          "author": {
            "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "name": "Jane Doe"
          },
          "content": "From 1849 station.",
          "likeCount": 0,
          "likedByMe": false,
          "createdAt": "2026-04-07T13:08:00",
          "replies": []
        }
      ]
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `post` | object | Post object |
| `post.id` | string | Post unique identifier |
| `post.author` | object | Post author info |
| `post.content` | string | Post content |
| `post.hallTag` | string \| null | Dining hall tag |
| `post.imageUrl` | string \| null | Post image URL |
| `post.likeCount` | number | Total number of post likes |
| `post.replyCount` | number | Total number of replies |
| `post.createdAt` | string | ISO 8601 creation timestamp |
| `post.likedByMe` | boolean | Whether current user liked the post |
| `replies` | array | Root-level replies |
| `replies[].parentReplyId` | string \| null | Parent reply ID (null for root replies) |
| `replies[].replies` | array | Nested replies (recursive) |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Post not found |
