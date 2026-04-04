# 6. Community

A social feed where users can share and browse dining hall food photos and posts.

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a feed of community posts (food photos, reviews) related to dining halls | No |
| POST | `/community/posts` | Create a new community post with a photo and text | Yes |
| GET | `/community/posts/:postId` | Retrieve a single community post by ID | No |
| DELETE | `/community/posts/:postId` | Delete a post authored by the current user | Yes |
