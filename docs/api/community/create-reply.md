# POST /community/posts/:postId/replies

Create a top-level reply on a post.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Content-Type` | `application/json` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string (UUID) | Target post ID |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User creating the reply |

### Body

```json
{
  "content": "Looks great, which station was this from?"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `content` | string | Yes | Reply text |

## Response

### Success (`201 Created`)

```json
{
  "id": "e7f0b6fd-43fc-4be2-9308-5f8045bfc3f2",
  "message": "Reply created successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | User not found or post not found |
| `422 Unprocessable Entity` | Validation error or blank content |
