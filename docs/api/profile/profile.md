# 7. Profile

User로 대체할 수 있지 않나? user id에 따른 테이블 생성해서... 사용자 맞춤형 DB 만들어나가기

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/users/me` | 유저의 프로필을 불러옵니다 | Yes |
| GET | `/users/me/meal-logs` | 지금까지 유저가 먹은 음식들... 리스트를 불러옵니다. | Yes |
| POST | `/users/me/meal-logs` | 과거에 추가하지 않았다면, 추가하고 싶은 (기재하고 싶은) 메뉴들을 추가할 수 있게 해줍니다. | Yes |
| PATCH | `/users/me` | 유저의 프로필 정보를 수정하고 싶다면, 수정합니다. | Yes |
