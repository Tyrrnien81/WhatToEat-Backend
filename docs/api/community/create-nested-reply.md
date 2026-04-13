# POST /community/replies/:replyId/replies

Create a nested reply under an existing reply.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `replyId` | string (UUID) | Parent reply ID |

### Query Parameters

None.

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
| `401 Unauthorized` | Missing or invalid JWT |
| `404 Not Found` | User not found, parent reply not found, or parent post not found |
| `422 Unprocessable Entity` | Validation error or blank content |

## Notes

- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
