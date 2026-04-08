# 6. Community

A social feed where users can share and browse dining hall food posts and interact through threaded replies and likes.

## Endpoints

| Method | Endpoint | Description | Auth | Docs |
| --- | --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a paginated feed of community posts | No | [list-posts.md](list-posts.md) |
| POST | `/community/posts` | Create a new post | Yes (`user_id` query) | [create-post.md](create-post.md) |
| GET | `/community/posts/:postId` | Retrieve a post with threaded replies | No | [get-post.md](get-post.md) |
| DELETE | `/community/posts/:postId` | Delete your own post | Yes (`user_id` query) | [delete-post.md](delete-post.md) |
| POST | `/community/posts/:postId/likes` | Like a post | Yes (`user_id` query) | [like-post.md](like-post.md) |
| DELETE | `/community/posts/:postId/likes` | Unlike a post | Yes (`user_id` query) | [unlike-post.md](unlike-post.md) |
| POST | `/community/posts/:postId/replies` | Create a top-level reply on a post | Yes (`user_id` query) | [create-reply.md](create-reply.md) |
| POST | `/community/replies/:replyId/replies` | Create a nested reply on a reply | Yes (`user_id` query) | [create-nested-reply.md](create-nested-reply.md) |
| POST | `/community/replies/:replyId/likes` | Like a reply | Yes (`user_id` query) | [like-reply.md](like-reply.md) |
| DELETE | `/community/replies/:replyId/likes` | Unlike a reply | Yes (`user_id` query) | [unlike-reply.md](unlike-reply.md) |

## Implementation Notes

- Posts are stored in the `community_posts` table with references to the author (`users`) and optionally a dining hall.
- Post images are saved as URLs (`imageUrl`) and not uploaded through this endpoint directly.
- Replies are stored in `community_replies` and support nesting using `parent_reply_id`.
- Likes are tracked separately in `community_post_likes` and `community_reply_likes`.
- Pagination uses `page` and `limit`, with `hasMore` returned instead of `total`.
- User-specific behavior currently uses `user_id` query parameters in write endpoints.
