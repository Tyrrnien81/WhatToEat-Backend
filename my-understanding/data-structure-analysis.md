# Gordon Avenue Market JSON Structure Analysis

Source analyzed: `Gordon_Avenue_Market_03-15-2026.json`

## 1. What the file represents

This file is a single exported menu snapshot for one restaurant, one service date, and one meal type.

- `restaurant`: one location
- `meal_type`: one service period (`Dinner`)
- `date`: one menu date (`2026-03-15`)
- `exported_at`: one extraction timestamp (`2026-03-15T00:04:52`)
- `menu`: the actual published menu payload for that restaurant/date/meal

So structurally, this is not a catalog of many restaurants or many days. It is one menu instance with nested sections and items.

## 2. Top-level shape

Top-level keys:

- `exported_at`: string timestamp
- `restaurant`: object
- `meal_type`: object
- `date`: string date
- `menu`: object

Top-level reference objects are very small:

- `restaurant`: `{ id, name }`
- `meal_type`: `{ id, name }`

## 3. Menu object shape

`menu` contains four fields:

- `date`: repeated menu date
- `has_unpublished_menus`: boolean
- `menu_info`: object keyed by `menu_id`
- `menu_items`: array of rows

### `menu_info`

`menu_info` is not a list. It is a dictionary keyed by menu section IDs such as `146701`, `146703`, and `327204`.

Each entry contains:

- `position`: display order of the section
- `section_options.display_name`: human-readable section name
- `section_options.use_section_title`: whether the section has a title row
- `section_options.section_title_can_expand_collapse`: UI behavior flag

In this file there are 8 menu sections:

1. `146701` -> `1849`
2. `146703` -> `Gordon Buona Cucina`
3. `146706` -> `Gordon Capital City Pizza`
4. `146727` -> `Gordon Que Rico`
5. `181805` -> `Fired Up`
6. `327206` -> `Buckingham Bakery`
7. `311855` -> `Gordon Delicious`
8. `327204` -> `Great Greens`

### `menu_items`

`menu_items` is the main array. It contains 76 rows.

Important distinction:

- 18 rows are structural/header rows
- 58 rows contain a populated `food` object

This means the array mixes two concepts:

1. Presentation rows used to render menu sections/stations
2. Actual food offerings

That is the main thing to normalize in the database.

## 4. Menu item row shape

Each `menu_items[]` row has display-level metadata plus optional food content.

Common fields:

- `id`: menu item row ID
- `menu_id`: section ID that links to `menu_info`
- `position`: sort order within the section
- `station_id`: optional station/subsection ID
- `text`: header/label text
- `category`: display category like `entree`, `side`, `dessert`
- `price`
- `serving_size_amount`
- `serving_size_unit`
- `food_variation_id`
- presentation flags such as:
  - `is_section_title`
  - `is_station_header`
  - `bold`
  - `featured`
  - `blank_line`
  - `no_line_break`
  - `station_is_collapsible`

Media/UI fields also appear on the row:

- `image`
- `image_thumbnail`
- `image_alt`
- `image_description`
- station image/logo fields

## 5. Structural rows vs food rows

Header rows usually look like this:

- `food = null`
- `is_section_title = true`
- `is_station_header = true`
- `text` contains labels such as `Entree`, `Sides`, `Breads`, `Build Your Own`

Examples of station/header labels found in this file:

- `Entree`
- `Sides`
- `Breads`
- `Choose your Filling`
- `Choose your Protein`
- `Varies by Day`
- `Build Your Own`

Food rows usually look like this:

- `food` is populated
- `food.id` is the reusable food entity ID
- row-level fields still carry placement info like `menu_id`, `station_id`, `position`

This suggests that `menu_items` should not be stored as a single flat `foods` table. It is closer to a join table plus optional presentation rows.

## 6. Food object shape

The nested `food` object is rich and looks reusable across menus.

Core food fields:

- `id`
- `name`
- `description`
- `price`
- `food_category`
- `smart_recipe_id`
- `meal_plan_price`
- `digest`
- `synced_id`
- `pos_item_id`

Content/detail fields:

- `ingredients`
- `synced_ingredients`
- `subtext`
- `download_label`
- `file_url`

Behavior/state fields:

- `has_nutrition_info`
- `has_options_or_sides`
- `has_subfoods`
- `ordering_enabled`
- `use_custom_sizes`
- several `*_unlocked` fields

Nested food substructures:

- `rounded_nutrition_info`: nutrition metrics
- `serving_size_info`: serving amount + unit
- `icons.food_icons`: dietary/allergen/label icons
- `icons.myplate_icons`: empty in sampled items, but structurally supported
- `food_sizes`: array, empty in sampled items
- `tags`: array, empty in sampled items
- `nested_foods`: array, empty in sampled items
- `synced_nested_foods`: array, empty in sampled items
- `aggregated_data`: derived summary values

## 7. Observed distributions

### Section and station counts

- 8 distinct `menu_id` values
- 8 non-null `station_id` values were observed, plus many rows with `station_id = null`
- `station_id = null` appears on 26 rows, so station is optional in practice

### Content counts

- total `menu_items`: 76
- rows with `food`: 58
- rows with `price`: 53
- rows with `food_variation_id`: 53
- rows with `food_list`: 0 in this file

### Display categories

Observed `category` values on item rows:

- `other`: 17
- `side`: 13
- `entree`: 10
- `dessert`: 5
- `condiment`: 5
- `meat`: 1

Note that some valid food rows have blank `category`, especially in bakery/soft-serve style entries. So `category` should be nullable.

### Food icons

Dietary/allergen icons are common and clearly deserve normalization if this data will be queried.

Examples observed:

- `Vegan`
- `Vegetarian`
- `Halal`
- `Top 9 Free`
- `Dairy`
- `Soy`
- `Wheat`
- `Corn`
- `Egg`
- `Coconut`
- `Shellfish`
- `Sesame`
- `Disclaimer`

## 8. Best database interpretation

The cleanest model is:

1. Master/reference entities
2. One menu snapshot instance
3. One or more menu sections within that menu
4. Optional station/group headers within a section
5. Food definitions reused across menus
6. A join table that places foods into a menu section/station with ordering and price

## 9. Recommended table outline

### `restaurants`

Use for location identity.

- `id` PK
- `external_restaurant_id` unique
- `name`

### `meal_types`

Use for meal periods like breakfast/lunch/dinner.

- `id` PK
- `external_meal_type_id` unique
- `name`

### `menu_exports` or `menu_snapshots`

One row per imported JSON file / scrape event.

- `id` PK
- `restaurant_id` FK
- `meal_type_id` FK
- `service_date`
- `exported_at`
- `has_unpublished_menus`
- `source_file_name`
- raw JSON column optional for audit/debug

### `menu_sections`

Represents entries from `menu.menu_info` keyed by `menu_id`.

- `id` PK
- `snapshot_id` FK
- `external_menu_id`
- `position`
- `display_name`
- `use_section_title`
- `can_expand_collapse`

### `stations`

Represents reusable station/subsection labels such as `Entree`, `Sides`, `Build Your Own`.

- `id` PK
- `external_station_id` nullable unique
- `name`

Notes:

- Some station labels are only discoverable from header rows (`text`)
- You may want station identity scoped by source system if station IDs are not globally stable

### `foods`

Canonical food entity from `menu_items[].food`.

- `id` PK
- `external_food_id` unique
- `name`
- `description`
- `food_category`
- `base_price`
- `smart_recipe_id` nullable
- `digest`
- `synced_id`
- `pos_item_id`
- `ingredients`
- `synced_ingredients`
- `subtext`
- `has_nutrition_info`
- `has_options_or_sides`
- `has_subfoods`
- `ordering_enabled`
- `use_custom_sizes`

### `food_nutrition`

One-to-one or one-to-many depending on whether nutrition can vary by size/version.

- `id` PK
- `food_id` FK
- `calories`
- `g_fat`
- `g_saturated_fat`
- `g_trans_fat`
- `mg_cholesterol`
- `g_carbs`
- `g_added_sugar`
- `g_sugar`
- `mg_potassium`
- `mg_sodium`
- `g_fiber`
- `g_protein`
- `mg_iron`
- `mg_calcium`
- `mg_vitamin_c`
- `mg_vitamin_d`
- `mcg_vitamin_d`
- other vitamin A fields as nullable columns

### `food_serving_sizes`

If serving size is worth querying independently.

- `id` PK
- `food_id` FK
- `serving_size_amount`
- `serving_size_unit`

### `food_icons`

Canonical icon definitions.

- `id` PK
- `external_icon_id` unique
- `name`
- `slug`
- `synced_name`
- `type`
- `behavior`
- `is_filter`
- `is_highlight`
- `sort_order`
- `custom_icon_url`

### `food_icon_assignments`

Join table between foods and icons.

- `food_id` FK
- `food_icon_id` FK

### `menu_section_items`

This is the most important table. It places a food into a specific menu snapshot/section/station.

- `id` PK
- `snapshot_id` FK
- `menu_section_id` FK
- `station_id` FK nullable
- `food_id` FK nullable
- `external_menu_item_id`
- `food_variation_id` nullable
- `position`
- `display_text` nullable
- `category` nullable
- `price` nullable
- `serving_size_amount` nullable
- `serving_size_unit` nullable
- `featured`
- `bold`
- `blank_line`
- `no_line_break`
- `is_section_title`
- `is_station_header`

This table can store both:

- actual food placements
- structural rows that have no food

If you want a stricter relational model, split this into:

- `menu_headers`
- `menu_food_items`

But for ingestion simplicity, one table is often enough.

## 10. Practical design advice

If your goal is product features like:

- show today’s menu
- filter by dietary icons
- view nutrition per food
- compare the same food across days
- see which stations a food appears in

then normalize at least these parts:

- restaurants
- meal_types
- menu_snapshots
- menu_sections
- foods
- menu_section_items
- food_icons
- food_icon_assignments

Everything else can be added later.

## 11. Minimal MVP schema

If you want the smallest useful version first, start with only:

1. `restaurants`
2. `meal_types`
3. `menu_snapshots`
4. `menu_sections`
5. `foods`
6. `menu_section_items`
7. `food_icons`
8. `food_icon_assignments`

That gives you enough to preserve:

- restaurant + meal + date context
- section grouping
- ordering
- station grouping when available
- reusable food records
- dietary/allergen filters

## 12. Main takeaway

The JSON is best understood as a single menu snapshot containing:

- one restaurant
- one meal type
- multiple menu sections
- mixed header rows and food placement rows
- reusable food entities with rich nutrition/icon metadata

For database design, the key move is to separate:

- menu snapshot context
- section/station presentation structure
- canonical food data
- food placement within a specific menu