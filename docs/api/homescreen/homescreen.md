# 3. Homescreen (홈화면)

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/recommendations/combos` | 유저의 preferences에 맞춘 알고리즘을 통해, 추천 메뉴를 DB > 프론트 | Yes |
| GET | `/goals/daily` | 오늘의 nutrition goal status 바를 위한 데이터를 가져옵니다 | Yes |
| GET | `/menus/summary` | 각 식당의 오늘의 추천 메뉴들을 유저 프레퍼런스에 맞추어 제공합니다 - 여기서 식당별로 나눠질 수도 있음. | Yes |
| POST | `/favorites` | 제공된 콤보들 중 유저가 좋아요 클릭 시, 즐겨찾기에 저장됩니다. | Yes |
| DELETE | `/favorites/:favoriteId` | 유저가 좋아요 한 메뉴를 취소하고 싶을 경우, 즐겨찾기에서 제거됩니다. | Yes |
