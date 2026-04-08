# API Documentation

## HTTP Method Guide

- `GET` = Retrieve data from the server
- `POST` = Create a new resource
- `PATCH` = Partially update an existing resource
- `DELETE` = Remove a resource

## Authentication

Some endpoints still document JWT usage for app-level auth flow.
For recently implemented community and homescreen endpoints, user context is currently passed as `user_id` query parameters.

JWT header format (when applicable):

```http
Authorization: Bearer <JWT token>
```

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
