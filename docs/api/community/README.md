# 6. Community

A social feed where users can share and browse dining hall food photos, reviews, and engage through likes and comments.

## Endpoints

| Method | Endpoint | Description | Auth | Docs |
| --- | --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a paginated feed of community posts | No | [list-posts.md](list-posts.md) |
| POST | `/community/posts` | Create a new post with a photo and text | Yes | [create-post.md](create-post.md) |
| GET | `/community/posts/:postId` | Retrieve a single post by ID | No | [get-post.md](get-post.md) |
| DELETE | `/community/posts/:postId` | Delete your own post | Yes | [delete-post.md](delete-post.md) |
| POST | `/community/posts/:postId/like` | Like a post | Yes | [like-post.md](like-post.md) |
| DELETE | `/community/posts/:postId/like` | Unlike a post | Yes | [unlike-post.md](unlike-post.md) |
| GET | `/community/posts/:postId/comments` | Retrieve comments on a post | No | [list-comments.md](list-comments.md) |
| POST | `/community/posts/:postId/comments` | Add a comment to a post | Yes | [create-comment.md](create-comment.md) |
| DELETE | `/community/posts/:postId/comments/:commentId` | Delete your own comment | Yes | [delete-comment.md](delete-comment.md) |

## Implementation Notes

- Posts are stored in the `community_posts` table with references to the author (`users`) and optionally a dining hall.
- Post images are uploaded to AWS S3 and the URL is stored in the `image_url` column.
- Likes are tracked in the `community_likes` table (unique constraint on `user_id` + `post_id`).
- Comments are stored in the `community_comments` table.
- Pagination follows cursor/offset style with `page` and `limit` query parameters.
