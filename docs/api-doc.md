# API Documentation

Complete API reference for the WhatToEat backend. All endpoints are grouped by service.

For the same content organized with links to per-endpoint pages, see [`docs/api/README.md`](api/README.md). Authentication architecture and Supabase split: [`docs/api/auth/README.md`](api/auth/README.md). Profile details: [`docs/api/profile/README.md`](api/profile/README.md).

## HTTP Method Guide

- `GET` = Retrieve data from the server
- `POST` = Create a new resource
- `PATCH` = Partially update an existing resource
- `DELETE` = Remove a resource

## Authentication

Protected routes require a **Supabase access token** in the header. The backend validates it against Supabase JWKS (`issuer` from `SUPABASE_ISSUER`). Identity is always the JWT `sub` claim (matches `users.id`).

```http
Authorization: Bearer <JWT token>
```

**Local integration tests only:** when the server sets `ALLOW_QUERY_USER_ID=true` (never in production), some personalized routes also accept `?user_id=<uuid>` if the header is absent. Production and staging clients must send the header only.

---

## 1. Authentication

Sign-in, sign-up, Google OAuth, email verification, password reset, and token refresh are handled by **Supabase Auth** on the client (`@supabase/supabase-js`). This FastAPI backend validates Supabase-issued JWTs and exposes three routes for profile sync and server-side logout.

### Backend endpoints

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/auth/me` | Retrieve the authenticated user's profile from the database | Yes |
| POST | `/auth/profile` | Create or update profile after Supabase auth (sync into `profiles`) | Yes |
| POST | `/auth/logout` | Revoke the Supabase session server-side | Yes |

### Supabase client-side flows

These flows are **not** implemented on this backend; the frontend calls Supabase directly.

| Flow | Supabase method | Notes |
| --- | --- | --- |
| Sign in | `signInWithPassword()` | — |
| Sign up | `signUp()` | — |
| Google OAuth | `signInWithOAuth()` | — |
| Forgot password | `resetPasswordForEmail()` | — |
| Verify email | Email link or OTP | Per Supabase project settings |
| Resend code | `resend()` | — |
| Reset password | `updateUser()` | After recovery flow |
| Refresh token | SDK session management | Automatic |

---

## 2. Questionnaire

Collects and manages user preference data used for personalized meal recommendations. Submitted during onboarding and editable from the profile.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/questionnaire` | Save initial user preferences (birthday, gender, height, weight, goal weight, diet type, dislikes, allergens) | Yes |
| GET | `/users/me/preferences` | Retrieve the current user's saved dietary preferences | Yes |
| PATCH | `/users/me/preferences` | Update the user's dietary preferences | Yes |

---

## 3. Homescreen

Powers the main screen with personalized menu recommendations, daily nutrition tracking, and meal logging.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/combo` | Get algorithmically recommended meal combos based on user preferences and available menus | Yes | ✅ Built |
| GET | `/goals/daily` | Retrieve today's nutrition goal progress (calories, macros) for the status bar | Yes | ✅ Built |
| GET | `/menus/summary` | Get today's highlighted menu items per dining hall, filtered by user preferences | Yes | ✅ Built |
| POST | `/meals/log` | Log a meal with food items and snapshotted nutrition data | Yes | ✅ Built |
| POST | `/favorites` | Save a recommended combo to the user's favorites | Yes | ✅ Built |
| DELETE | `/favorites/{favorite_id}` | Remove a previously saved combo from the user's favorites | Yes | ✅ Built |
| GET | `/recommendations/addons` | Get addon recommendations and quick-add items for the selected meal period | Yes | ✅ Built |

---

## 4. Dining Hall

Provides read-only access to dining hall information, station listings, and daily menus. Most routes do not require authentication; `/dining-halls/full` accepts an optional JWT to personalize filtering when provided.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/dining-halls` | List all available dining halls | No |
| GET | `/dining-halls/{hall_id}` | Get details for a specific dining hall | No |
| GET | `/dining-halls/{hall_id}/stations` | List all food stations within a specific dining hall | No |
| GET | `/dining-halls/{hall_id}/menus` | Get the menu items available at each station | No |
| GET | `/dining-halls/full` | Get frontend-oriented nested hall/day/menu payload | Optional |

---

## 5. Scan

Enables food recognition via photo upload. Identifies the food item and returns nutritional data, which can then be logged to the user's meal history.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/scan` | Upload a food photo for recognition; returns identified food name, calories, and nutritional breakdown | Yes |
| POST | `/scan/log` | Save the recognized food and its nutritional data to the user's meal log | Yes |

---

## 6. Community

A social feed where users can share and browse dining hall food photos and posts.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a feed of community posts (food photos, reviews) related to dining halls | No |
| POST | `/community/posts` | Create a new community post with a photo and text | Yes |
| GET | `/community/posts/{post_id}` | Retrieve a single community post by ID | No |
| DELETE | `/community/posts/{post_id}` | Delete a post authored by the current user | Yes |
| POST | `/community/posts/{post_id}/likes` | Like a post | Yes |
| DELETE | `/community/posts/{post_id}/likes` | Unlike a post | Yes |
| POST | `/community/posts/{post_id}/replies` | Create a top-level reply to a post | Yes |
| POST | `/community/replies/{reply_id}/replies` | Create a nested reply to a reply | Yes |
| POST | `/community/replies/{reply_id}/likes` | Like a reply | Yes |
| DELETE | `/community/replies/{reply_id}/likes` | Unlike a reply | Yes |

---

## 7. Profile

Manages the authenticated user's profile information, account settings, and food consumption log.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/users/me` | Retrieve the current user's full profile | Yes |
| PATCH | `/users/me` | Update profile information (name, preferences, body metrics, etc.) | Yes |
| DELETE | `/users/me` | Delete the user's account and associated data | Yes |
| POST | `/users/me/avatar` | Upload a profile photo | Yes |
| POST | `/users/me/change-password` | Change password (Supabase Auth; not for OAuth-only users) | Yes |
| GET | `/users/me/food-log` | Retrieve food consumption history (supports date filter and pagination) | Yes |
| POST | `/users/me/food-log` | Manually add a food log entry | Yes |
| DELETE | `/users/me/food-log/{entry_id}` | Delete a food log entry | Yes |
| GET | `/users/me/food-log/summary` | Retrieve nutrition summary and streaks (`range`: `week` \| `month` \| `all`) | Yes |
