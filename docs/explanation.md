# db table component explanation

DECIMAL(10,2)
10 = total number of digits allowed
2 = number of digits allowed after dp "."

# extracted data explanation

  "restaurant": {
    "id": 45372,
    "name": "Gordon Avenue Market"
  },

  "meal_type": {
    "id": 14944,
    "name": "Dinner"
  }

식당들은 모두 고유의 코드가 있다.
# TODO: 모든 데이터를 크롤링해서 식당별 고유 코드 매핑 (KEY로 사용)

# menu_info
menu_info table (STATION)
IDs such as 146701, 146703...
1849, Pizza가게, Bakery...등 

# menu_items # TODO: breakdown components into DB
함정이 있음. there are header rows: which looks like:
food = null
is_section-title = true

이게 무엇을 의미하느냐?
entree, sides, breads, choose your filling... 등 선택 옵션...
DB를 가르는 지표로 해도 될듯?

## category 또한 존재...
other, side, entree, dessert... can give dessert options

## food icons
Vegan, Vegeterian, Halal... 태그로 사용 가능.

{
        "id": 180292466,
        "date": null,
        "position": 1,
        "is_section_title": false,
        "bold": false,
        "featured": false,
        "text": "",
        "no_line_break": false,
        "blank_line": false,
        "food": {
          "id": 1303331,
          "name": "Grilled Flank Steak",
          "description": "",
          "image_url": null,
          "image_alt_text": null,
          "hoverpic_url": null,
          "price": 6.99,
          "food_category": "entree",
          "food_highlight_message": null,
          "file_url": "",
          "rounded_nutrition_info": {
            "calories": 187.0,
            "g_fat": 9.0,
            "g_saturated_fat": 3.9,
            "g_trans_fat": 0.0,
            "mg_cholesterol": 46.0,
            "g_carbs": 0.0,
            "g_added_sugar": null,
            "g_sugar": 0.0,
            "mg_potassium": 374.0,
            "mg_sodium": 139.0,
            "g_fiber": 0.0,
            "g_protein": 24.0,
            "mg_iron": 1.7,
            "mg_calcium": 31.0,
            "mg_vitamin_c": null,
            "iu_vitamin_a": null,
            "re_vitamin_a": null,
            "mcg_vitamin_a": null,
            "mg_vitamin_d": 0.1,
            "mcg_vitamin_d": null
          },





