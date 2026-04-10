# 6. Community

A social feed where users can share and browse dining hall food posts and interact through threaded replies and likes.

## Endpoints

| Method | Endpoint | Description | Auth | Docs |
| --- | --- | --- | --- | --- |
| GET | `/community/posts` | Retrieve a paginated feed of community posts | Optional JWT | [list-posts.md](list-posts.md) |
| POST | `/community/posts` | Create a new post | JWT | [create-post.md](create-post.md) |
| GET | `/community/posts/:postId` | Retrieve a post with threaded replies | Optional JWT | [get-post.md](get-post.md) |
| DELETE | `/community/posts/:postId` | Delete your own post | JWT | [delete-post.md](delete-post.md) |
| POST | `/community/posts/:postId/likes` | Like a post | JWT | [like-post.md](like-post.md) |
| DELETE | `/community/posts/:postId/likes` | Unlike a post | JWT | [unlike-post.md](unlike-post.md) |
| POST | `/community/posts/:postId/replies` | Create a top-level reply on a post | JWT | [create-reply.md](create-reply.md) |
| POST | `/community/replies/:replyId/replies` | Create a nested reply on a reply | JWT | [create-nested-reply.md](create-nested-reply.md) |
| POST | `/community/replies/:replyId/likes` | Like a reply | JWT | [like-reply.md](like-reply.md) |
| DELETE | `/community/replies/:replyId/likes` | Unlike a reply | JWT | [unlike-reply.md](unlike-reply.md) |

## Implementation Notes

- Posts are stored in the `community_posts` table with references to the author (`users`) and optionally a dining hall.
- Post images are saved as URLs (`imageUrl`) and not uploaded through this endpoint directly.
- Replies are stored in `community_replies` and support nesting using `parent_reply_id`.
- Likes are tracked separately in `community_post_likes` and `community_reply_likes`.
- Pagination uses `page` and `limit`, with `hasMore` returned instead of `total`.
- Writes require `Authorization: Bearer`. Optional JWT on public reads enables `likedByMe` and related flags. Dev-only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` when the header is omitted (never in production).
