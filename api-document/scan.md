# 5. Scan

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/scan` | 찍은 음식 사진을 DB로 바로, 혹은 OCR? 을 통해, 음식을 인식하고, 음식, 칼로리, 그리고 영양소를 돌려줍니다. | Yes |
| POST | `/scan/log` | 리턴된 음식, 칼로리, 영양소들을 DB에 저장합니다. | Yes |
