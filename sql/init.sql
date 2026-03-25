-- WhatToEat Database Initialization
-- Run in Supabase SQL Editor

-- ============================================================
-- Phase 0: Users table
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- ============================================================
-- Phase 1: Menu & Food Data (9 tables)
-- ============================================================

-- 1. restaurants (standalone)
CREATE TABLE IF NOT EXISTS restaurants (
    id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_restaurant_id INT UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL
);

-- 2. meal_types (standalone)
CREATE TABLE IF NOT EXISTS meal_types (
    id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_meal_type_id INT UNIQUE NOT NULL,
    name        VARCHAR(50) NOT NULL
);

-- 3. foods (standalone)
CREATE TABLE IF NOT EXISTS foods (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_food_id    INT UNIQUE NOT NULL,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    food_category       VARCHAR(50),
    price               NUMERIC(10,2),
    ingredients         TEXT,
    serving_size_amount VARCHAR(20),
    serving_size_unit   VARCHAR(50)
);

-- 4. food_icons (standalone)
CREATE TABLE IF NOT EXISTS food_icons (
    id               INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_icon_id INT UNIQUE NOT NULL,
    name             VARCHAR(100) NOT NULL,
    slug             VARCHAR(100) NOT NULL,
    icon_type        INT NOT NULL,
    behavior         INT NOT NULL,
    is_filter        BOOLEAN NOT NULL,
    is_highlight     BOOLEAN NOT NULL,
    sort_order       INT NOT NULL
);

-- 5. menu_snapshots (FKs → restaurants, meal_types)
CREATE TABLE IF NOT EXISTS menu_snapshots (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    restaurant_id  INT NOT NULL REFERENCES restaurants(id),
    meal_type_id   INT NOT NULL REFERENCES meal_types(id),
    service_date   DATE NOT NULL,
    exported_at    TIMESTAMPTZ,
    UNIQUE (restaurant_id, meal_type_id, service_date)
);

-- 6. menu_sections (FK → menu_snapshots)
CREATE TABLE IF NOT EXISTS menu_sections (
    id               INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    snapshot_id      INT NOT NULL REFERENCES menu_snapshots(id),
    external_menu_id INT NOT NULL,
    display_name     VARCHAR(255) NOT NULL,
    position         INT NOT NULL
);

-- 7. food_nutrition (FK → foods, 1:1 via UNIQUE)
CREATE TABLE IF NOT EXISTS food_nutrition (
    food_id        INT NOT NULL REFERENCES foods(id) UNIQUE,
    calories       NUMERIC(10,2),
    g_fat          NUMERIC(10,2),
    g_saturated_fat NUMERIC(10,2),
    g_trans_fat    NUMERIC(10,2),
    mg_cholesterol NUMERIC(10,2),
    g_carbs        NUMERIC(10,2),
    g_added_sugar  NUMERIC(10,2),
    g_sugar        NUMERIC(10,2),
    mg_potassium   NUMERIC(10,2),
    mg_sodium      NUMERIC(10,2),
    g_fiber        NUMERIC(10,2),
    g_protein      NUMERIC(10,2),
    mg_iron        NUMERIC(10,2),
    mg_calcium     NUMERIC(10,2),
    mg_vitamin_c   NUMERIC(10,2),
    iu_vitamin_a   NUMERIC(10,2),
    re_vitamin_a   NUMERIC(10,2),
    mcg_vitamin_a  NUMERIC(10,2),
    mg_vitamin_d   NUMERIC(10,2),
    mcg_vitamin_d  NUMERIC(10,2)
);

-- 8. food_icon_assignments (FKs → foods, food_icons; composite PK)
CREATE TABLE IF NOT EXISTS food_icon_assignments (
    food_id INT NOT NULL REFERENCES foods(id),
    icon_id INT NOT NULL REFERENCES food_icons(id),
    PRIMARY KEY (food_id, icon_id)
);

-- 9. menu_section_items (FKs → menu_sections, foods)
CREATE TABLE IF NOT EXISTS menu_section_items (
    id                   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    section_id           INT NOT NULL REFERENCES menu_sections(id),
    food_id              INT REFERENCES foods(id),
    external_menu_item_id INT,
    food_variation_id    INT,
    position             INT NOT NULL,
    station_name         VARCHAR(100),
    category             VARCHAR(50),
    price                NUMERIC(10,2),
    serving_size_amount  VARCHAR(20),
    serving_size_unit    VARCHAR(50)
);

-- ============================================================
-- Phase 2: User Preferences & Tracking (3 tables)
-- ============================================================

-- 10. user_preferences (FK → users, 1:1 via UNIQUE)
CREATE TABLE IF NOT EXISTS user_preferences (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) UNIQUE,
    birthday        DATE,
    gender          VARCHAR(10),
    height          NUMERIC(5,1),
    weight          NUMERIC(5,1),
    goal_weight     NUMERIC(5,1),
    diet_type       VARCHAR(30),
    allergens       JSONB DEFAULT '[]'::jsonb,
    dislikes        JSONB DEFAULT '[]'::jsonb,
    target_calories INT,
    target_protein_g INT,
    target_carbs_g  INT,
    target_fat_g    INT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 11. meal_logs (FK → users)
CREATE TABLE IF NOT EXISTS meal_logs (
    id         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id),
    date       DATE NOT NULL,
    meal_type  VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, date, meal_type)
);

-- 12. meal_log_items (FKs → meal_logs, foods)
CREATE TABLE IF NOT EXISTS meal_log_items (
    id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    meal_log_id INT NOT NULL REFERENCES meal_logs(id),
    food_id     INT REFERENCES foods(id),
    food_name   VARCHAR(255) NOT NULL,
    quantity    NUMERIC(5,2) DEFAULT 1,
    calories    NUMERIC(10,2),
    g_protein   NUMERIC(10,2),
    g_carbs     NUMERIC(10,2),
    g_fat       NUMERIC(10,2),
    source      VARCHAR(20) NOT NULL,
    logged_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Phase 3: Favorites (1 table)
-- ============================================================

-- 13. favorites (FKs → users, foods)
CREATE TABLE IF NOT EXISTS favorites (
    id                       UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id                  UUID NOT NULL REFERENCES users(id),
    combo_id                 UUID NOT NULL,
    food_id                  INT REFERENCES foods(id),
    recommendation_snapshot  JSONB NOT NULL,
    created_at               TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, combo_id)
);
