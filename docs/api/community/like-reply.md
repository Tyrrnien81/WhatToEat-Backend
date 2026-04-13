# POST /community/replies/:replyId/likes

Like a reply.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `replyId` | string (UUID) | Target reply ID |

### Query Parameters

None.

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "liked": true,
  "likeCount": 3,
  "message": "Reply liked"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT |
| `404 Not Found` | User not found or reply not found |

## Notes

- If already liked, response is still `200` with `message: "Reply already liked"`.
- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
