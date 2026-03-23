# Questionnaire Service

Collects and manages user preference data used for personalized meal recommendations. The questionnaire is submitted during onboarding (first login) and preferences can be edited later from the profile.

## Endpoints

| Method | Endpoint | File | Description | JWT Required |
| --- | --- | --- | --- | --- |
| POST | `/questionnaire` | [submit.md](submit.md) | Save initial onboarding preferences | Yes |
| GET | `/users/me/preferences` | [get-preferences.md](get-preferences.md) | Retrieve saved dietary preferences | Yes |
| PATCH | `/users/me/preferences` | [update-preferences.md](update-preferences.md) | Update dietary preferences | Yes |

## Implementation Notes

- Height supports cm/ft units; weight supports kg/lb units.
- `diet_type` values: `balanced`, `high_protein`, `vegan`, `vegetarian`.
- Dislikes are organized by category: Vegetables, Proteins, Dairy, Herbs & Spices, Grains.
- Allergens are stored as a text array (e.g. `["peanuts", "shellfish"]`).
