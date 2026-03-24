# API Documentation

Complete API reference for the WhatToEat backend. All endpoints are grouped by service.

## HTTP Method Guide

- `GET` = Retrieve data from the server
- `POST` = Create a new resource
- `PATCH` = Partially update an existing resource
- `DELETE` = Remove a resource

## Authentication Header

Endpoints that require user-specific data must include a valid JWT token in the request header:

```http
Authorization: Bearer <JWT token>
```

---

## 1. User Service (Authentication)

Handles user registration, email/password sign-in, Google OAuth, email verification, password recovery, token refresh, and session management.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/auth/signin` | Authenticate with email and password; returns a JWT access token and user info | No |
| POST | `/auth/signup` | Register a new account; sends a 6-digit email verification code | No |
| POST | `/auth/google` | Authenticate via Google OAuth ID token; auto-creates account if new | No |
| POST | `/auth/forgot-pw` | Initiate password reset by sending a verification code to the user's email | No |
| POST | `/auth/verify-email` | Verify email address using a 6-digit code (used in signup and password reset flows) | No |
| POST | `/auth/resend-code` | Resend verification code to email (30-second cooldown enforced) | No |
| POST | `/auth/reset-pw` | Reset password after successful email verification | No |
| POST | `/auth/refresh-token` | Refresh an expired JWT using a valid refresh token | No |
| POST | `/auth/logout` | Invalidate the current session (accessed from Settings) | Yes |
| GET | `/auth/me` | Retrieve the currently authenticated user's profile from the JWT | Yes |

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
| POST | `/save-menu` | Save a recommended combo to the user's favorites | Yes | Not built |
| DELETE | `/delete-menu` | Remove a previously saved combo from the user's favorites | Yes | Not built |

---

## 4. Dining Hall

Provides read-only access to dining hall information, station listings, and daily menus. No authentication required.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/dining-hall` | List all available dining halls | No |
| GET | `/dining-hall/:hallId` | Get details for a specific dining hall | No |
| GET | `/dining-hall/:hallId/stations` | List all food stations within a specific dining hall | No |
| GET | `/dining-hall/:hallId/stations/menu` | Get the menu items available at each station | No |

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
| GET | `/community/posts/:postId` | Retrieve a single community post by ID | No |
| DELETE | `/community/posts/:postId` | Delete a post authored by the current user | Yes |

---

## 7. Profile

Manages the authenticated user's profile information and meal history log.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/users/me` | Retrieve the current user's full profile | Yes |
| GET | `/users/me/food-log` | Retrieve the user's historical meal log (all previously recorded meals) | Yes |
| POST | `/users/me/food-log` | Manually add a past meal entry to the user's meal log | Yes |
| PATCH | `/users/me` | Update the user's profile information (name, preferences, etc.) | Yes |
