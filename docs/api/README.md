# API Documentation

## HTTP Method Guide

- `GET` = Retrieve data from the server
- `POST` = Create a new resource
- `PATCH` = Partially update an existing resource
- `DELETE` = Remove a resource

## Authentication

Protected routes require a **Supabase access token** in the header. The backend validates it against Supabase JWKS (`issuer` from `SUPABASE_ISSUER`). Identity is always the JWT `sub` claim (matches `users.id`).

JWT header format:

```http
Authorization: Bearer <JWT token>
```

**Local integration tests only:** when the server sets `ALLOW_QUERY_USER_ID=true` (never in production), personalized routes also accept `?user_id=<uuid>` if the header is absent. Production and staging clients must send the header only.

## Services

| # | Service | Docs | Description |
|---|---------|------|-------------|
| 1 | Auth | [auth/](auth/README.md) | Sign-in, sign-up, Google OAuth, password recovery, email verification, session management |
| 2 | Questionnaire | [questionnaire/](questionnaire/README.md) | User preference collection and management |
| 3 | Homescreen | [homescreen/](homescreen/README.md) | Meal recommendations, nutrition goals, menu favoriting |
| 4 | Dining Halls | [dining-halls/](dining-halls/README.md) | Dining hall and menu browsing |
| 5 | Scan | [scan/](scan/README.md) | Food photo recognition and nutrition logging |
| 6 | Community | [community/](community/README.md) | Community posts, likes, and threaded replies |
| 7 | Profile | [profile/](profile/README.md) | User profile, food log, and account management |
