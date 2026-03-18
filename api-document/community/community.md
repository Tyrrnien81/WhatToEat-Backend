# 6. Community

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/community/posts` | 다이닝 홀들에 관련된 포스트, 음식 사진들을 불러옵니다. | No |
| POST | `/community/posts` | 사용자가 사진을 찍고 글을 올리면, 올린 사진과 글을 DB에 보냅니다. | Yes |
| GET | `/community/posts/:postId` | 모든 포스트가 아닌, 한 개의 포스트를 불러옵니다. (검색하면?) | No |
| DELETE | `/community/posts/:postId` | 본인이 올린 포스트 (사진, 글) 을 삭제합니다 | Yes |
