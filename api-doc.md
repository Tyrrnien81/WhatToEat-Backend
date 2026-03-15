# API Documentation
# by Everyone

## HTTP Method Guide

- `GET` = 데이터 가져오기
- `POST` = 데이터 만들기
- `PATCH` = 데이터 수정하기
- `DELETE` = 데이터 삭제하기

## Authentication Header

개인화된 정보가 필요한 API들은 요청 헤더에 JWT token이 있어야 합니다.

```http
Authorization: Bearer <JWT token>
```

---

## 1. User Service (로그인/회원가입)

This API handles user signin, signup, find password, google login

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/auth/signin` | 로그인 (이메일, 비밀번호 이용), JWT 토큰 돌려주기 | No |
| POST | `/auth/signup` | 회원가입 | No |
| POST | `/auth/google` | 구글 로그인. | No |
| POST | `/auth/forgot-pw` | mail 에 인증번호 보내서 확인 후 reset-pw 로 넘어가는걸로 | No |
| POST | `/auth/reset-pw` | 이메일 인증 이후 비밀번호를 리셋한다 | No |
| POST | `/auth/logout` | 메인화면에서 하는 것이 아닌, 나중에 환경 설정에 들어가서 | Yes |
| GET | `/auth/me` | 사용자 정보를 JWT로부터 돌려받는다 | Yes |

---

## 2. Questionnaire

이 API는 유저가 제공하는 정보를 DB에 저장합니다.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/questionnaire` | 유저가 제공한 birthday, gender, height, weight, goal_weight, diet_type, dislikes, allergens를 1차적으로 저장합니다. | Yes |
| GET | `/users/me/preferences` | 현재 유저 (JWT 토큰을 사용해) 유저의 preferences들을 가져옵니다 | Yes |
| PATCH | `/users/me/preferences` | 유저의 preferences 수정 시, DB 업데이트 | Yes |

---

## 3. Homescreen (홈화면)

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/recommendations/combo` | 유저의 preferences에 맞춘 알고리즘을 통해, 추천 메뉴를 DB > 프론트 | Yes |
| GET | `/goals/today` | 오늘의 nutrition goal status 바를 위한 데이터를 가져옵니다 | Yes |
| GET | `/menus/summary` | 각 식당의 오늘의 추천 메뉴들을 유저 프레퍼런스에 맞추어 제공합니다 - 여기서 식당별로 나눠질 수도 있음. | Yes |
| POST | `/save-menu` | 제공된 콤보들 중 유저가 좋아요 클릭 시, 오늘의 메뉴에 저장됩니다. | Yes |
| DELETE | `/delete-menu` | 유저가 좋아요 한 메뉴를 취소하고 싶을 경우, 오늘의 메뉴에서 제거됩니다. | Yes |
| PATCH | `TBD` | 필요한가? | TBD |

---

## 4. Dining Hall

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/dining-hall` | 모든 다이닝 홀들을 불러옵니다 | No |
| GET | `/dining-hall/:hallId` | 구체적인 다이닝 홀을 불러옵니다 | No |
| GET | `/dining-hall/:hallId/stations` | 구체적인 다이닝 홀에서 다양한 스테이션들을 불러옵니다 | No |
| GET | `/dining-hall/:hallId/stations/menu` | 스테이션 별로 제공되는 메뉴들을 불러옵니다. | No |

---

## 5. Scan

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/scan` | 찍은 음식 사진을 DB로 바로, 혹은 OCR? 을 통해, 음식을 인식하고, 음식, 칼로리, 그리고 영양소를 돌려줍니다. | Yes |
| POST | `/scan/log` | 리턴된 음식, 칼로리, 영양소들을 DB에 저장합니다. | Yes |

---

## 6. Community

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/community/posts` | 다이닝 홀들에 관련된 포스트, 음식 사진들을 불러옵니다. | No |
| POST | `/community/posts` | 사용자가 사진을 찍고 글을 올리면, 올린 사진과 글을 DB에 보냅니다. | Yes |
| GET | `/community/posts/:postId` | 모든 포스트가 아닌, 한 개의 포스트를 불러옵니다. (검색하면?) | No |
| DELETE | `/community/posts/:postId` | 본인이 올린 포스트 (사진, 글) 을 삭제합니다 | Yes |

---

## 7. Profile

User로 대체할 수 있지 않나? user id에 따른 테이블 생성해서... 사용자 맞춤형 DB 만들어나가기

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/users/me` | 유저의 프로필을 불러옵니다 | Yes |
| GET | `/users/me/food-log` | 지금까지 유저가 먹은 음식들... 리스트를 불러옵니다. | Yes |
| POST | `/users/me/food-log` | 과거에 추가하지 않았다면, 추가하고 싶은 (기재하고 싶은) 메뉴들을 추가할 수 있게 해줍니다. | Yes |
| PATCH | `/users/me` | 유저의 프로필 정보를 수정하고 싶다면, 수정합니다. | Yes |
