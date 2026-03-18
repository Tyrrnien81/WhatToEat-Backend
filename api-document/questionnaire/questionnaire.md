# 2. Questionnaire

이 API는 유저가 제공하는 정보를 DB에 저장합니다.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/questionnaire` | 유저가 제공한 birthday, gender, height, weight, goal_weight, diet_type, dislikes, allergens를 1차적으로 저장합니다. | Yes |
| GET | `/users/me/preferences` | 현재 유저 (JWT 토큰을 사용해) 유저의 preferences들을 가져옵니다 | Yes |
| PATCH | `/users/me/preferences` | 유저의 preferences 수정 시, DB 업데이트 | Yes |
