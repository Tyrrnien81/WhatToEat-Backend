# DB Documentation
# Database Documentation

## Overview

이 문서는 현재 음식, 영양 정보, 플래그, 메뉴 항목 관련 테이블 구조를 정리합니다.

---

## Table: `foods`

기본 음식 마스터 데이터를 저장합니다.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key | 음식 고유 키 |
| `name` | `VARCHAR(255)` | - | 음식 이름 |

---

## Table: `food_nutrition`

음식별 영양 정보를 저장합니다.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `food_id` | `INT` | Reference to `foods.id` | 음식 고유 키 |
| `calories` | `DECIMAL(10,2)` | - | 칼로리 |
| `g_fat` | `DECIMAL(10,2)` | - | 총 지방(g) |
| `g_saturated_fat` | `DECIMAL(10,2)` | - | 포화지방(g) |
| `g_trans_fat` | `DECIMAL(10,2)` | - | 트랜스지방(g) |
| `mg_cholesterol` | `DECIMAL(10,2)` | - | 콜레스테롤(mg) |
| `g_carbs` | `DECIMAL(10,2)` | - | 탄수화물(g) |
| `g_added_sugar` | `DECIMAL(10,2)` | - | 첨가당(g) |
| `g_sugar` | `DECIMAL(10,2)` | - | 총 당류(g) |
| `mg_potassium` | `DECIMAL(10,2)` | - | 칼륨(mg) |
| `mg_sodium` | `DECIMAL(10,2)` | - | 나트륨(mg) |
| `g_fiber` | `DECIMAL(10,2)` | - | 식이섬유(g) |
| `g_protein` | `DECIMAL(10,2)` | - | 단백질(g) |
| `mg_iron` | `DECIMAL(10,2)` | - | 철분(mg) |
| `mg_calcium` | `DECIMAL(10,2)` | - | 칼슘(mg) |
| `mg_vitamin_c` | `DECIMAL(10,2)` | - | 비타민 C(mg) |
| `iu_vitamin_a` | `DECIMAL(10,2)` | - | 비타민 A(IU) |
| `re_vitamin_a` | `DECIMAL(10,2)` | - | 비타민 A(RE) |
| `mcg_vitamin_a` | `DECIMAL(10,2)` | - | 비타민 A(μg) |
| `mg_vitamin_d` | `DECIMAL(10,2)` | - | 비타민 D(mg) |
| `mcg_vitamin_d` | `DECIMAL(10,2)` | - | 비타민 D(μg) |

---

## Table: `food_flags`

음식별 알레르기 및 식단 관련 플래그를 저장합니다.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | 플래그 고유 키 |
| `type` | `VARCHAR(50)` | - | 플래그 종류 (예: allergen, dietary) |
| `value` | `VARCHAR(100)` | - | 플래그 값 (예: 땅콩, Vegan 등) |
| `food_id` | `INT` | Reference to `foods.id` | 음식 고유 키 |

---

## Table: `menu_items`

날짜별, 식당별, 스테이션별 제공 메뉴를 저장합니다.

| Column | Type | Key / Reference | Description |
| --- | --- | --- | --- |
| `id` | `INT` | Primary Key, Auto Increment | 메뉴 항목 고유 키 |
| `date` | `DATE` | - | 메뉴가 제공되는 날짜 |
| `meal` | `VARCHAR(50)` | - | 식사 구분 (예: breakfast, lunch, dinner) |
| `dining_hall` | `VARCHAR(100)` | - | 식당 이름 |
| `station_name` | `VARCHAR(100)` | - | 음식이 제공되는 스테이션 이름 |
| `food_id` | `INT` | Reference to `foods.id` | 음식 고유 키 |