# API Documentation

## HTTP Method Guide

- `GET` — Retrieve data
- `POST` — Create data
- `PATCH` — Update data
- `DELETE` — Delete data

## Authentication Header

All APIs that require personalized information must include a JWT token in the request header.

```http
Authorization: Bearer <JWT token>
```

---

## 1. User Service (Authentication)

Handles user sign-in, sign-up, password recovery, and Google login.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/auth/signin` | Sign in with email and password; returns a JWT token | No |
| POST | `/auth/signup` | Register a new user account | No |
| POST | `/auth/google` | Sign in using Google OAuth | No |
| POST | `/auth/forgot-pw` | Send a verification code to the user's email for password reset | No |
| POST | `/auth/reset-pw` | Reset the password after email verification | No |
| POST | `/auth/logout` | Log out the current user (accessed from Settings, not the home screen) | Yes |
| GET | `/auth/me` | Retrieve the current user's information from the JWT | Yes |
| POST | `/auth/verify-email` | Verify user's email address with a 6-digit code sent after signup or password reset | No |
| POST | `/auth/resend-code` | Resend verification code to the user's email (30-second cooldown between attempts) | No |
| POST | `/auth/refresh-token` | Refresh an expired JWT token to maintain user session | No |

### `POST /auth/signin`

Sign in with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourPassword123"
}
```

**Response (`200 OK`):**
```json
{
  "token": "<JWT token>",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `401 Unauthorized` — Incorrect email or password

---

### `POST /auth/signup`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourPassword123",
  "name": "John Doe"
}
```

**Response (`201 Created`):**
```json
{
  "message": "Account created successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `409 Conflict` — Email already registered

---

### `POST /auth/google`

Authenticate using a Google OAuth token.

**Request Body:**
```json
{
  "idToken": "<Google OAuth ID token>"
}
```

**Response (`200 OK`):**
```json
{
  "token": "<JWT token>",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or expired Google token

---

### `POST /auth/forgot-pw`

Send a verification code to the user's email to initiate password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (`200 OK`):**
```json
{
  "message": "Verification code sent to email"
}
```

**Error Responses:**
- `404 Not Found` — Email not registered

---

### `POST /auth/reset-pw`

Reset the user's password after email verification.

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "newPassword": "newSecurePassword456"
}
```

**Response (`200 OK`):**
```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid or expired verification code
- `404 Not Found` — Email not registered

---

### `POST /auth/logout`

Log out the current user. This is accessed from the Settings screen.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "message": "Logged out successfully"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `GET /auth/me`

Retrieve the currently authenticated user's information from the JWT.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `POST /auth/verify-email`

Verify the user's email address using a 6-digit verification code. Used during signup and password reset flows. Code expires after approximately 6 minutes.

**Error Responses:**
- `400 Bad Request` — Invalid or expired verification code
- `404 Not Found` — Email not registered

---

### `POST /auth/resend-code`

Resend a verification code to the user's email. Enforces a 30-second cooldown between resend attempts.

**Error Responses:**
- `404 Not Found` — Email not registered
- `429 Too Many Requests` — Resend cooldown has not elapsed

---

### `POST /auth/refresh-token`

Refresh an expired JWT token. Used on app launch and when API calls return 401 to maintain seamless user sessions.

**Error Responses:**
- `401 Unauthorized` — Refresh token is invalid or expired

---

## 2. Questionnaire

Handles saving and retrieving user-provided preferences and personal information.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/questionnaire` | Save the user's onboarding data (birthday, gender, height, weight, goal weight, diet type, dislikes, allergens) | Yes |
| GET | `/users/me/preferences` | Retrieve the current user's preferences | Yes |
| PATCH | `/users/me/preferences` | Update the current user's preferences | Yes |
| GET | `/users/me/preferences/allergens` | Retrieve the user's allergen/food restriction list separately | Yes |

> **Implementation Note:** Height supports cm/ft units; weight supports kg/lb units. `diet_type` values: `balanced`, `high_protein`, `vegan`, `vegetarian`. Dislikes are organized by category: Vegetables, Proteins, Dairy, Herbs & Spices, Grains.

### `POST /questionnaire`

Save the user's initial onboarding questionnaire data.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:**
```json
{
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "weight": 70,
  "goal_weight": 65,
  "diet_type": "vegetarian",
  "dislikes": ["mushrooms", "olives"],
  "allergens": ["peanuts", "shellfish"]
}
```

**Response (`201 Created`):**
```json
{
  "message": "Questionnaire saved successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `401 Unauthorized` — Invalid or missing token

---

### `GET /users/me/preferences`

Retrieve the current user's saved preferences.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "weight": 70,
  "goal_weight": 65,
  "diet_type": "vegetarian",
  "dislikes": ["mushrooms", "olives"],
  "allergens": ["peanuts", "shellfish"]
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Preferences not yet set

---

### `PATCH /users/me/preferences`

Update the current user's preferences. Only include the fields to be updated.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body (partial update):**
```json
{
  "weight": 68,
  "goal_weight": 63,
  "dislikes": ["mushrooms"]
}
```

**Response (`200 OK`):**
```json
{
  "message": "Preferences updated successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid fields
- `401 Unauthorized` — Invalid or missing token

---

## 3. Home Screen

Provides personalized meal recommendations, daily nutrition goals, and saved menu management.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/recommendations/combo` | Retrieve personalized meal combo recommendations based on user preferences | Yes |
| GET | `/goals/today` | Retrieve today's nutrition goal progress data (for the status bar) | Yes |
| GET | `/menus/summary` | Retrieve today's recommended menus from each dining hall, tailored to user preferences | Yes |
| POST | `/save-menu` | Save a recommended combo to the user's daily menu (like/favorite) | Yes |
| DELETE | `/delete-menu` | Remove a saved combo from the user's daily menu (unlike/unfavorite) | Yes |
| POST | `/log-meal` | Log a meal the user has eaten (from recommendations or manual) | Yes |
| GET | `/meals/logged` | Retrieve logged meals for a specific date | Yes |
| GET | `/meals/quick-addons` | Retrieve quick add-on food items for a meal (e.g., banana, latte, toast) | No |

> **Query Param Notes:** `GET /recommendations/combo`, `GET /goals/today`, and `GET /menus/summary` should all support a `?date=YYYY-MM-DD` query parameter (UI shows a 5-day date strip). `GET /recommendations/combo` should also support `?mealType=breakfast|lunch|dinner` for context-aware results.

### `GET /recommendations/combo`

Retrieve personalized meal combo recommendations generated by the recommendation algorithm based on user preferences.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "combos": [
    {
      "id": "combo-uuid",
      "name": "Balanced Lunch",
      "items": [
        {
          "id": "item-uuid",
          "name": "Grilled Chicken",
          "calories": 350,
          "protein": 30,
          "carbs": 10,
          "fat": 15
        }
      ],
      "totalCalories": 650,
      "diningHall": "Main Dining Hall"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `GET /goals/today`

Retrieve today's nutrition goal progress for the status bar display.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "calories": { "goal": 2000, "consumed": 850 },
  "protein": { "goal": 120, "consumed": 55 },
  "carbs": { "goal": 250, "consumed": 100 },
  "fat": { "goal": 65, "consumed": 30 }
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `GET /menus/summary`

Retrieve today's recommended menus from each dining hall, tailored to the user's preferences. Results may be grouped by dining hall.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "diningHalls": [
    {
      "id": "hall-uuid",
      "name": "Main Dining Hall",
      "recommendedItems": [
        {
          "id": "item-uuid",
          "name": "Grilled Salmon",
          "calories": 400,
          "station": "Grill"
        }
      ]
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `POST /save-menu`

Save a recommended combo to the user's daily menu when the user taps the like/favorite button.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:**
```json
{
  "comboId": "combo-uuid"
}
```

**Response (`201 Created`):**
```json
{
  "message": "Menu saved successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid combo ID
- `401 Unauthorized` — Invalid or missing token
- `409 Conflict` — Menu already saved

---

### `DELETE /delete-menu`

Remove a previously saved combo from the user's daily menu (unfavorite).

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:**
```json
{
  "comboId": "combo-uuid"
}
```

**Response (`200 OK`):**
```json
{
  "message": "Menu removed successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid combo ID
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Menu not found in saved list

---

### `POST /log-meal`

Log a meal that the user has eaten. Supports logging from recommendations, dining hall menus, or manual entry. Can include substitutions and additional items selected during the meal customization flow.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `401 Unauthorized` — Invalid or missing token

---

### `GET /meals/logged`

Retrieve all meals the user has logged for a specific date. Used to show "Logged" badges on meal cards.

**Headers:** `Authorization: Bearer <JWT token>`

**Query Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `date` | string | Date to retrieve logs for (format: `YYYY-MM-DD`, defaults to today) |
| `mealType` | string | Optional filter: `breakfast`, `lunch`, or `dinner` |

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `GET /meals/quick-addons`

Retrieve a list of common quick add-on food items (e.g., banana, latte, toast) that the user can add to a meal.

**Error Responses:**
- None expected (public endpoint)

---

## 4. Dining Hall

Provides information about dining halls, their stations, and available menus.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/dining-hall` | Retrieve a list of all dining halls | No |
| GET | `/dining-hall/:hallId` | Retrieve details for a specific dining hall | No |
| GET | `/dining-hall/:hallId/stations` | Retrieve all stations within a specific dining hall | No |
| GET | `/dining-hall/:hallId/stations/menu` | Retrieve menus for each station in a specific dining hall | No |
| GET | `/dining-hall/:hallId/ai-pick` | Retrieve AI-generated meal recommendation for the user at a specific hall | Yes |

> **Query Param Notes:** `GET /dining-hall` supports `?sort=openNow|closest|relevance` for sorting results. `GET /dining-hall/:hallId/stations/menu` supports `?mealPeriod=breakfast|lunch|dinner` and `?date=YYYY-MM-DD`. Hall response should include: status (open/soon/closed), hours, occupancy level/percentage, and emoji identifier.

### `GET /dining-hall`

Retrieve a list of all available dining halls.

**Response (`200 OK`):**
```json
{
  "diningHalls": [
    {
      "id": "hall-uuid",
      "name": "Main Dining Hall",
      "location": "Building A",
      "hours": "7:00 AM – 9:00 PM"
    }
  ]
}
```

---

### `GET /dining-hall/:hallId`

Retrieve details for a specific dining hall.

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `hallId` | string | The unique ID of the dining hall |

**Response (`200 OK`):**
```json
{
  "id": "hall-uuid",
  "name": "Main Dining Hall",
  "location": "Building A",
  "hours": "7:00 AM – 9:00 PM",
  "description": "The main campus dining facility"
}
```

**Error Responses:**
- `404 Not Found` — Dining hall not found

---

### `GET /dining-hall/:hallId/stations`

Retrieve all food stations within a specific dining hall.

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `hallId` | string | The unique ID of the dining hall |

**Response (`200 OK`):**
```json
{
  "stations": [
    {
      "id": "station-uuid",
      "name": "Grill",
      "description": "Burgers, grilled chicken, and more"
    },
    {
      "id": "station-uuid",
      "name": "Salad Bar",
      "description": "Fresh salads and dressings"
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` — Dining hall not found

---

### `GET /dining-hall/:hallId/stations/menu`

Retrieve the menus available at each station in a specific dining hall.

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `hallId` | string | The unique ID of the dining hall |

**Response (`200 OK`):**
```json
{
  "stations": [
    {
      "stationName": "Grill",
      "items": [
        {
          "id": "item-uuid",
          "name": "Cheeseburger",
          "calories": 550,
          "protein": 28,
          "carbs": 40,
          "fat": 30,
          "allergens": ["dairy", "gluten"]
        }
      ]
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` — Dining hall not found

---

### `GET /dining-hall/:hallId/ai-pick`

Retrieve an AI-generated personalized meal recommendation for the authenticated user at a specific dining hall. Returns a label (e.g., "AI Pick · High Protein") and a meal name.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Dining hall not found

---

## 5. Scan

Handles food image recognition and nutrition logging.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/scan` | Upload a food photo for recognition (via image analysis or OCR); returns identified food items, calories, and nutrition info | Yes |
| POST | `/scan/log` | Save the recognized food items and their nutrition data to the user's food log | Yes |

### `POST /scan`

Upload a food photo for recognition. The server processes the image (via AI-based image recognition or OCR) and returns identified food items along with calorie and nutrition data.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:** `multipart/form-data`
| Field | Type | Description |
| --- | --- | --- |
| `image` | file | The food photo to analyze |

**Response (`200 OK`):**
```json
{
  "items": [
    {
      "name": "Grilled Chicken Breast",
      "confidence": 0.92,
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` — No image provided or unsupported format
- `401 Unauthorized` — Invalid or missing token
- `422 Unprocessable Entity` — Could not identify food in the image

---

### `POST /scan/log`

Save the recognized food items and their nutrition data to the user's daily food log.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:**
```json
{
  "items": [
    {
      "name": "Grilled Chicken Breast",
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12
    }
  ]
}
```

**Response (`201 Created`):**
```json
{
  "message": "Food log saved successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `401 Unauthorized` — Invalid or missing token

---

## 6. Community

Handles community posts related to dining halls, including food photos and reviews.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve all community posts (dining hall food photos, reviews, etc.) | No |
| POST | `/community/posts` | Create a new community post with a photo and text | Yes |
| GET | `/community/posts/:postId` | Retrieve a single community post by ID | No |
| DELETE | `/community/posts/:postId` | Delete one of your own community posts | Yes |
| POST | `/community/posts/:postId/like` | Like a community post | Yes |
| DELETE | `/community/posts/:postId/like` | Unlike a community post | Yes |
| GET | `/community/posts/:postId/comments` | Retrieve comments on a post | No |
| POST | `/community/posts/:postId/comments` | Add a comment to a post | Yes |
| DELETE | `/community/posts/:postId/comments/:commentId` | Delete your own comment | Yes |

### `GET /community/posts`

Retrieve all community posts, including food photos and reviews related to dining halls.

**Query Parameters (optional):**
| Parameter | Type | Description |
| --- | --- | --- |
| `page` | number | Page number for pagination (default: 1) |
| `limit` | number | Number of posts per page (default: 20) |
| `hallId` | string | Filter posts by dining hall ID |

**Response (`200 OK`):**
```json
{
  "posts": [
    {
      "id": "post-uuid",
      "author": { "id": "user-uuid", "name": "Jane Doe" },
      "text": "Amazing grilled salmon today!",
      "imageUrl": "https://...",
      "diningHall": "Main Dining Hall",
      "createdAt": "2026-03-18T12:30:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

---

### `POST /community/posts`

Create a new community post with a photo and text.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:** `multipart/form-data`
| Field | Type | Description |
| --- | --- | --- |
| `image` | file | Photo of the food |
| `text` | string | Post caption or description |
| `hallId` | string | (Optional) Associated dining hall ID |

**Response (`201 Created`):**
```json
{
  "id": "post-uuid",
  "message": "Post created successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Missing required fields
- `401 Unauthorized` — Invalid or missing token

---

### `GET /community/posts/:postId`

Retrieve a single community post by its ID.

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post |

**Response (`200 OK`):**
```json
{
  "id": "post-uuid",
  "author": { "id": "user-uuid", "name": "Jane Doe" },
  "text": "Amazing grilled salmon today!",
  "imageUrl": "https://...",
  "diningHall": "Main Dining Hall",
  "createdAt": "2026-03-18T12:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` — Post not found

---

### `DELETE /community/posts/:postId`

Delete one of your own community posts (photo and text).

**Headers:** `Authorization: Bearer <JWT token>`

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `postId` | string | The unique ID of the post to delete |

**Response (`200 OK`):**
```json
{
  "message": "Post deleted successfully"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `403 Forbidden` — Cannot delete another user's post
- `404 Not Found` — Post not found

---

### `POST /community/posts/:postId/like`

Like a community post. Idempotent — liking an already-liked post has no effect.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Post not found

---

### `DELETE /community/posts/:postId/like`

Unlike a previously liked community post.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Post not found

---

### `GET /community/posts/:postId/comments`

Retrieve comments on a community post, with pagination.

**Query Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `page` | number | Page number (default: 1) |
| `limit` | number | Comments per page (default: 20) |

**Error Responses:**
- `404 Not Found` — Post not found

---

### `POST /community/posts/:postId/comments`

Add a comment to a community post.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `400 Bad Request` — Empty comment body
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Post not found

---

### `DELETE /community/posts/:postId/comments/:commentId`

Delete your own comment on a community post.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `403 Forbidden` — Cannot delete another user's comment
- `404 Not Found` — Comment not found

---

## 7. Profile

Manages the current user's profile information and food log history.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/users/me` | Retrieve the current user's profile | Yes |
| GET | `/users/me/food-log` | Retrieve the user's food consumption history | Yes |
| POST | `/users/me/food-log` | Manually add a food entry to the user's food log | Yes |
| DELETE | `/users/me/food-log/:entryId` | Delete a specific food log entry | Yes |
| PATCH | `/users/me` | Update the current user's profile information | Yes |
| DELETE | `/users/me` | Delete the user's account | Yes |
| POST | `/users/me/avatar` | Upload a profile photo (multipart/form-data) | Yes |
| POST | `/users/me/change-password` | Change password (requires current password) | Yes |
| GET | `/users/me/food-log/summary` | Retrieve nutrition summary, streaks, and weight history | Yes |

### `GET /users/me`

Retrieve the currently authenticated user's profile.

**Headers:** `Authorization: Bearer <JWT token>`

**Response (`200 OK`):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "weight": 70,
  "goal_weight": 65,
  "diet_type": "vegetarian"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `GET /users/me/food-log`

Retrieve the user's food consumption history.

**Headers:** `Authorization: Bearer <JWT token>`

**Query Parameters (optional):**
| Parameter | Type | Description |
| --- | --- | --- |
| `date` | string | Filter by date (format: `YYYY-MM-DD`). Defaults to today. |
| `page` | number | Page number for pagination (default: 1) |
| `limit` | number | Number of entries per page (default: 20) |

**Response (`200 OK`):**
```json
{
  "entries": [
    {
      "id": "entry-uuid",
      "name": "Grilled Chicken Breast",
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12,
      "loggedAt": "2026-03-18T12:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `POST /users/me/food-log`

Manually add a food entry to the user's food log (for items not logged via scan).

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:**
```json
{
  "name": "Banana",
  "calories": 105,
  "protein": 1,
  "carbs": 27,
  "fat": 0,
  "date": "2026-03-18"
}
```

**Response (`201 Created`):**
```json
{
  "id": "entry-uuid",
  "message": "Food log entry added successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `401 Unauthorized` — Invalid or missing token

---

### `PATCH /users/me`

Update the current user's profile information. Only include the fields to be updated.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body (partial update):**
```json
{
  "name": "John Smith",
  "weight": 68
}
```

**Response (`200 OK`):**
```json
{
  "message": "Profile updated successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid fields
- `401 Unauthorized` — Invalid or missing token

---

### `DELETE /users/me/food-log/:entryId`

Delete a specific food log entry.

**Headers:** `Authorization: Bearer <JWT token>`

**Path Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `entryId` | string | The unique ID of the food log entry to delete |

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
- `404 Not Found` — Entry not found

---

### `DELETE /users/me`

Permanently delete the user's account and all associated data.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `POST /users/me/avatar`

Upload or update the user's profile photo.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:** `multipart/form-data`
| Field | Type | Description |
| --- | --- | --- |
| `avatar` | file | Profile photo image file |

**Error Responses:**
- `400 Bad Request` — No image provided or unsupported format
- `401 Unauthorized` — Invalid or missing token

---

### `POST /users/me/change-password`

Change the user's password. Requires the current password for verification.

**Headers:** `Authorization: Bearer <JWT token>`

**Error Responses:**
- `400 Bad Request` — Current password incorrect or new password too weak
- `401 Unauthorized` — Invalid or missing token

---

### `GET /users/me/food-log/summary`

Retrieve aggregated nutrition summary, streak data, and weight history for the user's profile dashboard.

**Headers:** `Authorization: Bearer <JWT token>`

**Query Parameters:**
| Parameter | Type | Description |
| --- | --- | --- |
| `range` | string | Time range: `week`, `month`, or `all` (default: `week`) |

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token
