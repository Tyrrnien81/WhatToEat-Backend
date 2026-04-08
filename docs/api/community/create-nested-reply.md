# POST /community/replies/:replyId/replies

Create a nested reply under an existing reply.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Content-Type` | `application/json` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `replyId` | string (UUID) | Parent reply ID |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User creating the nested reply |

### Body

```json
{
  "content": "It was from 1849 station."
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `content` | string | Yes | Reply text |

## Response

### Success (`201 Created`)

```json
{
  "id": "890da98d-b64b-4fb9-a38d-bf8ea30783b5",
  "message": "Reply created successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | User not found, parent reply not found, or parent post not found |
| `422 Unprocessable Entity` | Validation error or blank content |
