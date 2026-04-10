# DELETE /community/replies/:replyId/likes

Remove a user's like from a reply.

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
  "liked": false,
  "likeCount": 2,
  "message": "Reply unliked"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT |
| `404 Not Found` | Reply not found |

## Notes

- If the reply was not liked by this user, response is still `200` with `message: "Reply was not liked"`.
- Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` without JWT (never in production).
