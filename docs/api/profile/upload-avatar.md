# POST /users/me/avatar

Upload or update the user's profile photo.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `multipart/form-data` | Yes |

### Body (`multipart/form-data`)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `avatar` | file | Yes | Profile photo image file. Supported formats: JPEG, PNG. |

## Response

### Success (`200 OK`)

```json
{
  "message": "Avatar updated successfully",
  "avatarUrl": "https://s3.amazonaws.com/whattoeat/avatars/user123.jpg"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Confirmation message |
| `avatarUrl` | string | URL of the uploaded profile photo (S3) |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | No image provided or unsupported file format |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- The image is uploaded to AWS S3 under the `avatars/` prefix.
- If the user already has an avatar, the previous image is replaced in S3.
- The `users.avatar_url` column is updated with the new URL.
