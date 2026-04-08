# POST /community/replies/:replyId/likes

Like a reply.

## Request

### Headers

None required.

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `replyId` | string (UUID) | Target reply ID |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User ID performing the like |

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
| `404 Not Found` | User not found or reply not found |

## Notes

- If already liked, response is still `200` with `message: "Reply already liked"`.
