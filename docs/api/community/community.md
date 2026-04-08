# 6. Community

A social feed where users can share and browse dining hall food posts.

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a feed of community posts (food photos, reviews) related to dining halls | No |
| POST | `/community/posts` | Create a new community post with text and optional `imageUrl` | Yes (`user_id` query) |
| GET | `/community/posts/:postId` | Retrieve a single post with threaded replies | No |
| DELETE | `/community/posts/:postId` | Delete a post authored by the current user | Yes (`user_id` query) |
| POST | `/community/posts/:postId/likes` | Like a post | Yes (`user_id` query) |
| DELETE | `/community/posts/:postId/likes` | Unlike a post | Yes (`user_id` query) |
| POST | `/community/posts/:postId/replies` | Add a top-level reply to a post | Yes (`user_id` query) |
| POST | `/community/replies/:replyId/replies` | Add a nested reply to an existing reply | Yes (`user_id` query) |
| POST | `/community/replies/:replyId/likes` | Like a reply | Yes (`user_id` query) |
| DELETE | `/community/replies/:replyId/likes` | Unlike a reply | Yes (`user_id` query) |
