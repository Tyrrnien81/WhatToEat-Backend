# API Documentation

Complete API reference for the WhatToEat backend. All endpoints are grouped by service.

## HTTP Method Guide

- `GET` = Retrieve data from the server
- `POST` = Create a new resource
- `PATCH` = Partially update an existing resource
- `DELETE` = Remove a resource

## Authentication Header

Endpoints that require user-specific data must include a valid Supabase JWT in the request header:

```http
Authorization: Bearer <JWT token>
```

The backend verifies the token with Supabase JWKS; the caller’s user id is taken from the `sub` claim.

**Local testing only:** if `ALLOW_QUERY_USER_ID=true` is set on the server (off by default), some personalized routes accept `?user_id=<uuid>` when the header is missing. Do not enable in production.

### Common response status codes

| Code | When |
| --- | --- |
| `200 OK` | Successful read, update, or delete returning a body |
| `201 Created` | Resource created (`POST` questionnaire, meal log, favorites, community replies, etc.) |
| `400 Bad Request` | Invalid input |
| `401 Unauthorized` | Missing/invalid JWT on a protected route |
| `404 Not Found` | Resource does not exist |
| `413 Payload Too Large` | Request body exceeds limit (e.g. scan image) |
| `422 Unprocessable Entity` | Validation error (Pydantic / business rules) |

---

## 1. Authentication

Authentication uses **Supabase Auth** (client-side). The frontend calls Supabase JS SDK directly for signup, signin, Google OAuth, email verification, password reset, and token refresh. The backend validates Supabase-issued JWT tokens and exposes 3 endpoints for profile management and logout.

### Backend Endpoints

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| GET | `/auth/me` | Retrieve the authenticated user's profile from the database | Yes | ✅ Built |
| POST | `/auth/profile` | Create or update the user's profile after Supabase auth | Yes | ✅ Built |
| POST | `/auth/logout` | Revoke the Supabase session server-side | Yes | ✅ Built |

### Supabase Client-Side Flows (handled by frontend)

| Flow | Supabase Method | Description |
| --- | --- | --- |
| Sign in | `supabase.auth.signInWithPassword()` | Email/password authentication |
| Sign up | `supabase.auth.signUp()` | Register new account with email verification |
| Google OAuth | `supabase.auth.signInWithOAuth()` | Google social login |
| Forgot password | `supabase.auth.resetPasswordForEmail()` | Send password reset email |
| Verify email | Automatic via Supabase email link/OTP | Email confirmation |
| Resend code | `supabase.auth.resend()` | Resend verification email |
| Reset password | `supabase.auth.updateUser()` | Set new password after reset |
| Refresh token | Automatic via Supabase session management | Token rotation handled by SDK |

---

## 2. Questionnaire

Collects and manages user preference data used for personalized meal recommendations. Submitted during onboarding and editable from the profile. Supports unit conversion (ft/lb → cm/kg) and auto-calculates nutrition targets.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| POST | `/questionnaire` | Save initial onboarding preferences (body metrics, diet, dislikes, allergens, favorite dining halls) with unit conversion | Yes | ✅ Built |
| GET | `/users/me/preferences` | Retrieve the current user's saved dietary preferences and computed nutrition targets | Yes | ✅ Built |
| PATCH | `/users/me/preferences` | Partially update dietary preferences; auto-recalculates targets when body metrics change | Yes | ✅ Built |

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

Provides read-only access to dining hall information, station listings, and daily menus. Most routes are public; `/dining-halls/full` accepts an optional JWT to personalize `favorited` flags.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| GET | `/dining-halls` | List all available dining halls | No | ✅ Built |
| GET | `/dining-halls/{hall_id}` | Get details for a specific dining hall | No | ✅ Built |
| GET | `/dining-halls/{hall_id}/stations` | List all food stations within a specific dining hall | No | ✅ Built |
| GET | `/dining-halls/{hall_id}/menus` | Get the menu items available at each station | No | ✅ Built |
| GET | `/dining-halls/full` | Get frontend-oriented nested hall/day/menu payload | Optional | ✅ Built |

---

## 5. Scan

Enables food recognition via photo upload. Identifies the food item and returns nutritional data, which can then be logged to the user's meal history.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| POST | `/scan` | Upload a food photo for recognition; returns identified food name, calories, and nutritional breakdown | Yes | ✅ Built |
| POST | `/scan/log` | Save the recognized food and its nutritional data to the user's meal log | Yes | ✅ Built |

---

## 6. Community

A social feed where users can share and browse dining hall food photos and posts.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a feed of community posts (food photos, reviews) related to dining halls | Optional | ✅ Built |
| POST | `/community/posts` | Create a new community post with a photo and text | Yes | ✅ Built |
| GET | `/community/posts/{post_id}` | Retrieve a single community post by ID | Optional | ✅ Built |
| DELETE | `/community/posts/{post_id}` | Delete a post authored by the current user | Yes | ✅ Built |
| POST | `/community/posts/{post_id}/likes` | Like a post | Yes | ✅ Built |
| DELETE | `/community/posts/{post_id}/likes` | Unlike a post | Yes | ✅ Built |
| POST | `/community/posts/{post_id}/replies` | Create a top-level reply to a post | Yes | ✅ Built |
| POST | `/community/replies/{reply_id}/replies` | Create a nested reply to a reply | Yes | ✅ Built |
| POST | `/community/replies/{reply_id}/likes` | Like a reply | Yes | ✅ Built |
| DELETE | `/community/replies/{reply_id}/likes` | Unlike a reply | Yes | ✅ Built |

---

## 7. Profile

Manages the authenticated user's profile information, account settings, and food consumption log.

| Method | Endpoint | Description | JWT Required | Status |
| --- | --- | --- | --- | --- |
| GET | `/users/me` | Retrieve the current user's full profile (including body metrics and preferences) | Yes | ✅ Built |
| PATCH | `/users/me` | Update profile information (name, body metrics, diet type) | Yes | ✅ Built |
| DELETE | `/users/me` | Permanently delete the user's account and all associated data | Yes | ✅ Built |
| POST | `/users/me/avatar` | Upload or update profile photo | Yes | ✅ Built |
| POST | `/users/me/change-password` | Change the user's password (email-based accounts only) | Yes | ✅ Built |
| GET | `/users/me/food-log` | Retrieve food consumption history with pagination and date filtering | Yes | ✅ Built |
| POST | `/users/me/food-log` | Manually add a food log entry | Yes | ✅ Built |
| DELETE | `/users/me/food-log/{entry_id}` | Delete a specific food log entry | Yes | ✅ Built |
| GET | `/users/me/food-log/summary` | Retrieve nutrition summary, streaks, and weight history | Yes | ✅ Built |
