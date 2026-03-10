# TODO

## Today

- [ ] Watch the login API video
- [ ] Design the login-related DB table
- [ ] Create the `users` table
- [ ] Define the sign-in workflow
- [ ] Issue a JWT on successful sign-in

## Users Table

`users`

- `id`
- `email`
- `name`
- `provider`
- `token` (optional)
- `created_at`
- `updated_at`

## Sign-In Workflow

1. Client sends sign-in request with provider auth data.
2. Server validates the provider token or auth result.
3. Server finds the user by email/provider.
4. If the user does not exist, create a new user row.
5. Server issues a JWT for the user.
6. Server returns the JWT and basic user info.

## Notes

- Decide whether `token` means provider access token, refresh token, or should be removed.
- Define JWT expiration and secret management before implementation.