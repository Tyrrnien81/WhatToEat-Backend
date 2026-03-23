# DB Documentation
# Database Documentation

## Overview

This document describes the current table structures for foods, nutrition data, dietary/allergen flags, and daily menu items.

---

## Table: `foods`

Stores the master list of food items.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key | Unique food identifier |
| `name` | `VARCHAR(255)` | - | Food name |

---

## Table: `food_nutrition`

Stores per-food nutritional information.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `food_id` | `INT` | Reference to `foods.id` | Unique food identifier |
| `calories` | `DECIMAL(10,2)` | - | Calories |
| `g_fat` | `DECIMAL(10,2)` | - | Total fat (g) |
| `g_saturated_fat` | `DECIMAL(10,2)` | - | Saturated fat (g) |
| `g_trans_fat` | `DECIMAL(10,2)` | - | Trans fat (g) |
| `mg_cholesterol` | `DECIMAL(10,2)` | - | Cholesterol (mg) |
| `g_carbs` | `DECIMAL(10,2)` | - | Carbohydrates (g) |
| `g_added_sugar` | `DECIMAL(10,2)` | - | Added sugar (g) |
| `g_sugar` | `DECIMAL(10,2)` | - | Total sugar (g) |
| `mg_potassium` | `DECIMAL(10,2)` | - | Potassium (mg) |
| `mg_sodium` | `DECIMAL(10,2)` | - | Sodium (mg) |
| `g_fiber` | `DECIMAL(10,2)` | - | Dietary fiber (g) |
| `g_protein` | `DECIMAL(10,2)` | - | Protein (g) |
| `mg_iron` | `DECIMAL(10,2)` | - | Iron (mg) |
| `mg_calcium` | `DECIMAL(10,2)` | - | Calcium (mg) |
| `mg_vitamin_c` | `DECIMAL(10,2)` | - | Vitamin C (mg) |
| `iu_vitamin_a` | `DECIMAL(10,2)` | - | Vitamin A (IU) |
| `re_vitamin_a` | `DECIMAL(10,2)` | - | Vitamin A (RE) |
| `mcg_vitamin_a` | `DECIMAL(10,2)` | - | Vitamin A (μg) |
| `mg_vitamin_d` | `DECIMAL(10,2)` | - | Vitamin D (mg) |
| `mcg_vitamin_d` | `DECIMAL(10,2)` | - | Vitamin D (μg) |

---

## Table: `food_flags`

Stores allergen and dietary flags per food item.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Unique flag identifier |
| `type` | `VARCHAR(50)` | - | Flag category (e.g. allergen, dietary) |
| `value` | `VARCHAR(100)` | - | Flag value (e.g. Peanut, Vegan) |
| `food_id` | `INT` | Reference to `foods.id` | Unique food identifier |

---

## Table: `menu_items`

Stores daily menu offerings per dining hall and station.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | Unique menu item identifier |
| `date` | `DATE` | - | Date the menu is served |
| `meal` | `VARCHAR(50)` | - | Meal period (e.g. breakfast, lunch, dinner) |
| `dining_hall` | `VARCHAR(100)` | - | Dining hall name |
| `station_name` | `VARCHAR(100)` | - | Station where the food is served |
| `food_id` | `INT` | Reference to `foods.id` | Unique food identifier |