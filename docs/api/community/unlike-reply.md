# DELETE /community/replies/:replyId/likes

Remove a user's like from a reply.

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
| `user_id` | string (UUID) | Yes | User ID performing the unlike |

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
| `404 Not Found` | Reply not found |

## Notes

- If the reply was not liked by this user, response is still `200` with `message: "Reply was not liked"`.
