# 2. Questionnaire

Collects and manages user preference data used for personalized meal recommendations. The questionnaire is submitted during onboarding (first login) and preferences can be edited later from the profile. Supports unit conversion (ft/lb → cm/kg) and auto-calculates nutrition targets.

## Endpoints

| Method | Endpoint | Docs | Description | JWT Required | Status |
| --- | --- | --- | --- | --- | --- |
| POST | `/questionnaire` | [submit.md](submit.md) | Save initial onboarding preferences (body metrics, diet, dislikes, allergens, favorite dining halls) | Yes | ✅ Built |
| GET | `/users/me/preferences` | [get-preferences.md](get-preferences.md) | Retrieve saved dietary preferences and computed nutrition targets | Yes | ✅ Built |
| PATCH | `/users/me/preferences` | [update-preferences.md](update-preferences.md) | Partially update dietary preferences; auto-recalculates targets | Yes | ✅ Built |

## Implementation Notes

- Height supports cm/ft units; weight supports kg/lb units. The backend stores all values in metric (cm, kg) and converts on submission.
- `gender` values: `male`, `female`, `other`, `prefer`.
- `diet_type` values: `balanced`, `high_protein`, `vegan`, `vegetarian`. The alias `highprotein` is also accepted and normalized to `high_protein`.
- Dislikes are human-readable food names organized by category: Vegetables, Proteins, Dairy, Herbs & Spices, Grains.
- Allergens are stored as an ID array. Valid IDs: `soy`, `peanuts`, `treenuts`, `halal`, `kosher`, `dairy`, `gluten`, `shellfish`, `fish`, `egg`, `other`. Sending `["none"]` stores an empty array.
- `favorite_dining_halls` is an ordered array of up to 3 dining hall IDs: `gordon`, `fourlakes`, `liz`, `rheta`, `carson`, `lowell`.
- Nutrition targets (calories, protein, carbs, fat) are auto-calculated using the Mifflin-St Jeor equation with a 1.55 activity multiplier.

## Project Structure (Questionnaire)

```
app/
├── routers/
│   └── questionnaire.py
├── schemas/
│   └── questionnaire.py
├── services/
│   └── questionnaire_service.py
└── models/
    └── tracking.py          # UserPreference model
```

| File | Responsibility |
| --- | --- |
| `app/routers/questionnaire.py` | Defines `/questionnaire` and `/users/me/preferences` route handlers |
| `app/schemas/questionnaire.py` | Pydantic request/response models with validation |
| `app/services/questionnaire_service.py` | Business logic: unit conversion, nutrition calculation, CRUD |
| `app/models/tracking.py` | `UserPreference` SQLAlchemy model (shared with other services) |
