# TODO

## Today

- [ ] Watch the login API video
- [ ] Design the login-related DB table (`PostgreSQL`)
- [ ] Create the `users` table (`PostgreSQL`)
- [ ] Define the sign-in workflow (`Node.js + TypeScript` backend)
- [ ] Issue a JWT on successful sign-in (`JWT` auth)

## Users Table

`users`

- `id`
- `email`
- `name`
- `provider`
- `token` (optional)
- `created_at`
- `updated_at`

## Before Starting

- [ ] Decide DB types and constraints for each `users` column (`PostgreSQL`)
- [ ] Decide whether `email` must be unique globally or unique per provider (`PostgreSQL` unique constraint)
- [ ] Decide allowed `provider` values (e.g. `google`, `apple`, `kakao`) (`Node.js + TypeScript` enum/string)
- [ ] Decide whether `token` is actually needed in DB (`PostgreSQL` column)
- [ ] Define JWT payload, expiration, and secret/env strategy (`JWT` + env vars)
- [ ] Define sign-in API request/response shape (`Node.js + TypeScript` API)

## Users Table Details

- `id`: UUID or auto-increment primary key
- `email`: required, indexed
- `name`: required
- `provider`: required
- `token`: optional, only if provider token must be stored
- `created_at`: required
- `updated_at`: required

## API Shape

### Sign-In Request

- `provider`
- `provider_token` or provider auth code

### Sign-In Response

- `access_token` (JWT)
- `user.id`
- `user.email`
- `user.name`
- `user.provider`

## JWT Decisions

- Decide JWT expiry time (`JWT`)
- Decide JWT claims (`sub`, `email`, `provider`) (`JWT`)
- Decide whether refresh token is needed for MVP (`JWT` auth flow)
- Store JWT secret in environment variables (`Node.js + TypeScript` backend)

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
- Decide how to handle first sign-in vs existing user sign-in.
- Decide what happens if provider email is missing or already linked differently.