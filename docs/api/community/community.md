# 6. Community

A social feed where users can share and browse dining hall food photos and posts.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a feed of community posts (food photos, reviews) related to dining halls | No |
| POST | `/community/posts` | Create a new community post with a photo and text | Yes |
| GET | `/community/posts/:postId` | Retrieve a single community post by ID | No |
| DELETE | `/community/posts/:postId` | Delete a post authored by the current user | Yes |
| POST | `/community/posts/:postId/likes` | Like a post | Yes |
| DELETE | `/community/posts/:postId/likes` | Unlike a post | Yes |
| POST | `/community/posts/:postId/replies` | Add a top-level reply to a post | Yes |
| POST | `/community/replies/:replyId/replies` | Add a nested reply to an existing reply | Yes |
| POST | `/community/replies/:replyId/likes` | Like a reply | Yes |
| DELETE | `/community/replies/:replyId/likes` | Unlike a reply | Yes |
