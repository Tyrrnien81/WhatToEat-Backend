# Database Documentation

## Overview

This document describes the table structures for the WhatToEat backend database. Tables are organized into three domains:

1. **Menu & Food Data** — Dining halls, menu snapshots, food items, nutrition, and dietary icons (sourced from Nutrislice)
2. **User Preferences & Tracking** — Onboarding questionnaire, meal logging, daily goals
3. **Favorites** — Saved meal combos

> **Note:** Auth tables (`users`, `verification_codes`, `refresh_tokens`) are documented separately in `user-table.md` and already implemented as SQLAlchemy models.

---

# Menu & Food Data

---

## Table: `restaurants`

Stores dining hall identity. One row per physical dining location.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Internal restaurant identifier |
| `external_restaurant_id` | `INT` | Unique | Nutrislice restaurant ID (e.g. 45372) |
| `name` | `VARCHAR(255)` | - | Dining hall name (e.g. "Gordon Avenue Market") |

---

## Table: `meal_types`

Reference table for meal periods.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Internal meal type identifier |
| `external_meal_type_id` | `INT` | Unique | Nutrislice meal type ID (e.g. 14944) |
| `name` | `VARCHAR(50)` | - | Meal period name (e.g. "Breakfast", "Lunch", "Dinner") |

---

## Table: `menu_snapshots`

One row per ingested menu file. Represents a single restaurant + meal + date combination.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Snapshot identifier |
| `restaurant_id` | `INT` | FK → `restaurants.id` | Which dining hall |
| `meal_type_id` | `INT` | FK → `meal_types.id` | Which meal period |
| `service_date` | `DATE` | - | Date the menu is served |
| `exported_at` | `TIMESTAMPTZ` | Nullable | When the source data was exported |

**Constraints:**
- `UNIQUE (restaurant_id, meal_type_id, service_date)`

---

## Table: `menu_sections`

Stations/sections within a menu snapshot (e.g. "1849", "Gordon Buona Cucina", "Fired Up"). Maps to the `menu_info` keys in the Nutrislice JSON.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Section identifier |
| `snapshot_id` | `INT` | FK → `menu_snapshots.id` | Parent snapshot |
| `external_menu_id` | `INT` | - | Nutrislice section key (e.g. 146701) |
| `display_name` | `VARCHAR(255)` | - | Section name (e.g. "Gordon Capital City Pizza") |
| `position` | `INT` | - | Display order within the snapshot |

---

## Table: `foods`

Stores the master list of food items. A food is a reusable entity that can appear across multiple menus/dates.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Internal food identifier |
| `external_food_id` | `INT` | Unique | Nutrislice food ID (e.g. 1303331) |
| `name` | `VARCHAR(255)` | - | Food name (e.g. "Grilled Flank Steak") |
| `description` | `TEXT` | Nullable | Food description |
| `food_category` | `VARCHAR(50)` | Nullable | Category: "entree", "side", "dessert", "condiment", "meat", "other" |
| `price` | `DECIMAL(10,2)` | Nullable | Base price |
| `ingredients` | `TEXT` | Nullable | Full ingredient list string |
| `serving_size_amount` | `VARCHAR(20)` | Nullable | Serving amount (e.g. "1", "0.25") |
| `serving_size_unit` | `VARCHAR(50)` | Nullable | Serving unit (e.g. "4 oz", "each", "slice") |

---

## Table: `food_nutrition`

Stores per-food nutritional information (1:1 with `foods`).

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `food_id` | `INT` | FK → `foods.id`, Unique | Food reference |
| `calories` | `DECIMAL(10,2)` | Nullable | Calories |
| `g_fat` | `DECIMAL(10,2)` | Nullable | Total fat (g) |
| `g_saturated_fat` | `DECIMAL(10,2)` | Nullable | Saturated fat (g) |
| `g_trans_fat` | `DECIMAL(10,2)` | Nullable | Trans fat (g) |
| `mg_cholesterol` | `DECIMAL(10,2)` | Nullable | Cholesterol (mg) |
| `g_carbs` | `DECIMAL(10,2)` | Nullable | Carbohydrates (g) |
| `g_added_sugar` | `DECIMAL(10,2)` | Nullable | Added sugar (g) |
| `g_sugar` | `DECIMAL(10,2)` | Nullable | Total sugar (g) |
| `mg_potassium` | `DECIMAL(10,2)` | Nullable | Potassium (mg) |
| `mg_sodium` | `DECIMAL(10,2)` | Nullable | Sodium (mg) |
| `g_fiber` | `DECIMAL(10,2)` | Nullable | Dietary fiber (g) |
| `g_protein` | `DECIMAL(10,2)` | Nullable | Protein (g) |
| `mg_iron` | `DECIMAL(10,2)` | Nullable | Iron (mg) |
| `mg_calcium` | `DECIMAL(10,2)` | Nullable | Calcium (mg) |
| `mg_vitamin_c` | `DECIMAL(10,2)` | Nullable | Vitamin C (mg) |
| `iu_vitamin_a` | `DECIMAL(10,2)` | Nullable | Vitamin A (IU) |
| `re_vitamin_a` | `DECIMAL(10,2)` | Nullable | Vitamin A (RE) |
| `mcg_vitamin_a` | `DECIMAL(10,2)` | Nullable | Vitamin A (μg) |
| `mg_vitamin_d` | `DECIMAL(10,2)` | Nullable | Vitamin D (mg) |
| `mcg_vitamin_d` | `DECIMAL(10,2)` | Nullable | Vitamin D (μg) |

---

## Table: `food_icons`

Canonical icon definitions for allergens and dietary labels. Each icon is a reusable tag (e.g. "Dairy", "Vegan", "Top 9 Free").

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Internal icon identifier |
| `external_icon_id` | `INT` | Unique | Nutrislice icon ID (e.g. 26988) |
| `name` | `VARCHAR(100)` | - | Display name (e.g. "Dairy", "Vegan") |
| `slug` | `VARCHAR(100)` | - | URL-safe identifier (e.g. "dairy", "vegan") |
| `icon_type` | `INT` | - | Icon type from source (1 = food trait) |
| `behavior` | `INT` | - | 1 = allergen/filter, 2 = dietary highlight |
| `is_filter` | `BOOLEAN` | - | Whether this icon is used for filtering |
| `is_highlight` | `BOOLEAN` | - | Whether this icon is a highlight badge |
| `sort_order` | `INT` | - | Display order |

**Known icons:**

| Name | Behavior | Usage |
| --- | --- | --- |
| Dairy (Milk) | 1 – allergen | Filter |
| Egg | 1 – allergen | Filter |
| Wheat | 1 – allergen | Filter |
| Soy | 1 – allergen | Filter |
| Shellfish | 1 – allergen | Filter |
| Sesame | 1 – allergen | Filter |
| Coconut | 1 – allergen | Filter |
| Corn | 1 – allergen | Filter |
| Vegan | 2 – dietary | Highlight |
| Vegetarian | 2 – dietary | Highlight |
| Halal | 2 – dietary | Highlight |
| Top 9 Free | 2 – dietary | Highlight |

---

## Table: `food_icon_assignments`

Many-to-many join between foods and icons.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `food_id` | `INT` | FK → `foods.id` | Food reference |
| `icon_id` | `INT` | FK → `food_icons.id` | Icon reference |

**Constraints:**
- `PRIMARY KEY (food_id, icon_id)`

---

## Table: `menu_section_items`

Places a food into a specific menu snapshot / section / station. This is the main join table that reconstructs the full menu for any restaurant/date/meal.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Item identifier |
| `section_id` | `INT` | FK → `menu_sections.id` | Which section this item belongs to |
| `food_id` | `INT` | FK → `foods.id`, Nullable | Food reference (null for header rows) |
| `external_menu_item_id` | `INT` | Nullable | Nutrislice menu item ID |
| `food_variation_id` | `INT` | Nullable | Nutrislice food variation ID |
| `position` | `INT` | - | Display order within the section |
| `station_name` | `VARCHAR(100)` | Nullable | Station label (e.g. "Entree", "Sides", "Build Your Own") |
| `category` | `VARCHAR(50)` | Nullable | Display category (e.g. "entree", "side", "dessert") |
| `price` | `DECIMAL(10,2)` | Nullable | Menu-level price override |
| `serving_size_amount` | `VARCHAR(20)` | Nullable | Serving amount at menu level |
| `serving_size_unit` | `VARCHAR(50)` | Nullable | Serving unit at menu level |

---

# User Preferences & Tracking

---

## Table: `user_preferences`

Stores onboarding questionnaire answers and auto-calculated nutrition targets. One-to-one with `users`.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Preference record identifier |
| `user_id` | `UUID` | FK → `users.id`, Unique | User reference |
| `birthday` | `DATE` | Nullable | User's date of birth |
| `gender` | `VARCHAR(10)` | Nullable | "male", "female", or "other" |
| `height` | `DECIMAL(5,1)` | Nullable | Height in cm |
| `weight` | `DECIMAL(5,1)` | Nullable | Weight in kg |
| `goal_weight` | `DECIMAL(5,1)` | Nullable | Target weight in kg |
| `diet_type` | `VARCHAR(30)` | Nullable | "balanced", "high_protein", "vegan", "vegetarian" |
| `allergens` | `JSONB` | Default `'[]'` | Array of allergen slugs (e.g. `["dairy", "wheat"]`) |
| `dislikes` | `JSONB` | Default `'[]'` | Array of disliked food names |
| `target_calories` | `INT` | Nullable | Daily calorie target (auto-calculated) |
| `target_protein_g` | `INT` | Nullable | Daily protein target in grams |
| `target_carbs_g` | `INT` | Nullable | Daily carbs target in grams |
| `target_fat_g` | `INT` | Nullable | Daily fat target in grams |
| `created_at` | `TIMESTAMPTZ` | - | When preferences were first set |
| `updated_at` | `TIMESTAMPTZ` | - | Last update timestamp |

---

## Table: `meal_logs`

Groups a user's logged food items by date and meal period.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Log identifier |
| `user_id` | `UUID` | FK → `users.id` | User reference |
| `date` | `DATE` | - | Date of the meal |
| `meal_type` | `VARCHAR(20)` | - | "breakfast", "lunch", or "dinner" |
| `created_at` | `TIMESTAMPTZ` | - | When the log was created |

**Constraints:**
- `UNIQUE (user_id, date, meal_type)`

---

## Table: `meal_log_items`

Individual food items within a meal log. Nutrition values are denormalized (snapshotted at log time) so historical logs stay accurate even if food data is updated later.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Item identifier |
| `meal_log_id` | `INT` | FK → `meal_logs.id` | Parent log reference |
| `food_id` | `INT` | FK → `foods.id`, Nullable | Food reference (null for manual/scan entries) |
| `food_name` | `VARCHAR(255)` | - | Denormalized food name |
| `quantity` | `DECIMAL(5,2)` | Default `1` | Number of servings |
| `calories` | `DECIMAL(10,2)` | Nullable | Calories at log time |
| `g_protein` | `DECIMAL(10,2)` | Nullable | Protein (g) at log time |
| `g_carbs` | `DECIMAL(10,2)` | Nullable | Carbs (g) at log time |
| `g_fat` | `DECIMAL(10,2)` | Nullable | Fat (g) at log time |
| `source` | `VARCHAR(20)` | - | How item was logged: "menu", "scan", or "manual" |
| `logged_at` | `TIMESTAMPTZ` | - | When item was logged |

---

# Favorites

---

## Table: `favorites`

Stores user-saved meal combos with a JSONB snapshot of the recommendation at save time.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Primary Key | Favorite identifier (used in DELETE endpoint) |
| `user_id` | `UUID` | FK → `users.id` | User who saved it |
| `combo_id` | `UUID` | - | The combo that was favorited |
| `food_id` | `INT` | FK → `foods.id`, Nullable | Optional single-food favorite (null for combos) |
| `recommendation_snapshot` | `JSONB` | - | Full combo details at time of save |
| `created_at` | `TIMESTAMPTZ` | - | When the favorite was saved |

**Constraints:**
- `UNIQUE (user_id, combo_id)` — prevents duplicate favorites (drives 409 response)