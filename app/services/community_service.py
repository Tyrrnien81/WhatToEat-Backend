import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import CommunityPost, CommunityPostLike, CommunityReply, CommunityReplyLike
from app.models.user import User


def _to_iso(dt: datetime) -> str:
    return dt.isoformat()


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


async def _get_user_or_404(user_id: uuid.UUID, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def _get_post_or_404(post_id: uuid.UUID, db: AsyncSession) -> CommunityPost:
    result = await db.execute(select(CommunityPost).where(CommunityPost.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def _get_reply_or_404(reply_id: uuid.UUID, db: AsyncSession) -> CommunityReply:
    result = await db.execute(select(CommunityReply).where(CommunityReply.id == reply_id))
    reply = result.scalar_one_or_none()
    if reply is None:
        raise HTTPException(status_code=404, detail="Reply not found")
    return reply


def _serialize_post(post: CommunityPost, author: User, liked_by_me: bool) -> dict:
    return {
        "id": str(post.id),
        "author": {
            "id": str(author.id),
            "name": author.name,
        },
        "content": post.content,
        "hallTag": post.hall_tag,
        "imageUrl": post.image_url,
        "likeCount": int(post.like_count or 0),
        "replyCount": int(post.reply_count or 0),
        "createdAt": _to_iso(post.created_at),
        "likedByMe": liked_by_me,
    }


async def get_posts(
    page: int,
    limit: int,
    q: str | None,
    hall_tag: str | None,
    current_user_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict:
    query = (
        select(CommunityPost, User)
        .join(User, CommunityPost.user_id == User.id)
        .order_by(CommunityPost.created_at.desc(), CommunityPost.id.desc())
    )

    q_norm = _normalize_optional(q)
    hall_tag_norm = _normalize_optional(hall_tag)
    if q_norm:
        query = query.where(CommunityPost.content.ilike(f"%{q_norm}%"))
    if hall_tag_norm:
        query = query.where(CommunityPost.hall_tag == hall_tag_norm)

    offset = (page - 1) * limit
    rows = (await db.execute(query.offset(offset).limit(limit + 1))).all()
    has_more = len(rows) > limit
    rows = rows[:limit]

    post_ids = [row[0].id for row in rows]
    liked_post_ids: set[uuid.UUID] = set()
    if current_user_id and post_ids:
        liked_rows = await db.execute(
            select(CommunityPostLike.post_id).where(
                CommunityPostLike.user_id == current_user_id,
                CommunityPostLike.post_id.in_(post_ids),
            )
        )
        liked_post_ids = {row[0] for row in liked_rows.all()}

    return {
        "page": page,
        "limit": limit,
        "hasMore": has_more,
        "posts": [_serialize_post(post, author, post.id in liked_post_ids) for post, author in rows],
    }


async def create_post(
    user_id: uuid.UUID,
    content: str,
    hall_tag: str | None,
    image_url: str | None,
    db: AsyncSession,
) -> dict:
    await _get_user_or_404(user_id, db)

    content_norm = content.strip()
    if not content_norm:
        raise HTTPException(status_code=422, detail="content cannot be blank")

    post = CommunityPost(
        user_id=user_id,
        content=content_norm,
        hall_tag=_normalize_optional(hall_tag),
        image_url=_normalize_optional(image_url),
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    return {
        "id": str(post.id),
        "message": "Post created successfully",
    }


async def get_post_detail(post_id: uuid.UUID, current_user_id: uuid.UUID | None, db: AsyncSession) -> dict:
    post_row = await db.execute(
        select(CommunityPost, User)
        .join(User, CommunityPost.user_id == User.id)
        .where(CommunityPost.id == post_id)
    )
    post_author_row = post_row.one_or_none()
    if post_author_row is None:
        raise HTTPException(status_code=404, detail="Post not found")

    post, author = post_author_row

    liked_by_me = False
    if current_user_id:
        liked_result = await db.execute(
            select(CommunityPostLike.id).where(
                CommunityPostLike.user_id == current_user_id,
                CommunityPostLike.post_id == post_id,
            )
        )
        liked_by_me = liked_result.scalar_one_or_none() is not None

    reply_rows = (
        await db.execute(
            select(CommunityReply, User)
            .join(User, CommunityReply.user_id == User.id)
            .where(CommunityReply.post_id == post_id)
            .order_by(CommunityReply.created_at.asc(), CommunityReply.id.asc())
        )
    ).all()

    reply_ids = [row[0].id for row in reply_rows]
    liked_reply_ids: set[uuid.UUID] = set()
    if current_user_id and reply_ids:
        reply_like_rows = await db.execute(
            select(CommunityReplyLike.reply_id).where(
                CommunityReplyLike.user_id == current_user_id,
                CommunityReplyLike.reply_id.in_(reply_ids),
            )
        )
        liked_reply_ids = {row[0] for row in reply_like_rows.all()}

    replies_map: dict[uuid.UUID, dict] = {}
    for reply, reply_author in reply_rows:
        replies_map[reply.id] = {
            "id": str(reply.id),
            "postId": str(reply.post_id),
            "parentReplyId": str(reply.parent_reply_id) if reply.parent_reply_id else None,
            "author": {
                "id": str(reply_author.id),
                "name": reply_author.name,
            },
            "content": reply.content,
            "likeCount": int(reply.like_count or 0),
            "likedByMe": reply.id in liked_reply_ids,
            "createdAt": _to_iso(reply.created_at),
            "replies": [],
        }

    roots: list[dict] = []
    for reply, _reply_author in reply_rows:
        node = replies_map[reply.id]
        if reply.parent_reply_id and reply.parent_reply_id in replies_map:
            replies_map[reply.parent_reply_id]["replies"].append(node)
        else:
            roots.append(node)

    return {
        "post": _serialize_post(post, author, liked_by_me),
        "replies": roots,
    }


async def delete_post(post_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict:
    post = await _get_post_or_404(post_id, db)
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the author can delete this post")

    reply_ids_result = await db.execute(
        select(CommunityReply.id).where(CommunityReply.post_id == post_id)
    )
    reply_ids = [row[0] for row in reply_ids_result.all()]

    if reply_ids:
        await db.execute(delete(CommunityReplyLike).where(CommunityReplyLike.reply_id.in_(reply_ids)))
    await db.execute(delete(CommunityReply).where(CommunityReply.post_id == post_id))
    await db.execute(delete(CommunityPostLike).where(CommunityPostLike.post_id == post_id))
    await db.execute(delete(CommunityPost).where(CommunityPost.id == post_id))

    await db.commit()

    return {"message": "Post deleted successfully"}


async def like_post(post_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict:
    await _get_user_or_404(user_id, db)
    post = await _get_post_or_404(post_id, db)

    existing = await db.execute(
        select(CommunityPostLike).where(
            CommunityPostLike.post_id == post_id,
            CommunityPostLike.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return {
            "liked": True,
            "likeCount": int(post.like_count or 0),
            "message": "Post already liked",
        }

    db.add(CommunityPostLike(post_id=post_id, user_id=user_id))
    post.like_count = int(post.like_count or 0) + 1
    await db.commit()
    await db.refresh(post)

    return {
        "liked": True,
        "likeCount": int(post.like_count or 0),
        "message": "Post liked",
    }


async def unlike_post(post_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict:
    post = await _get_post_or_404(post_id, db)

    existing_result = await db.execute(
        select(CommunityPostLike).where(
            CommunityPostLike.post_id == post_id,
            CommunityPostLike.user_id == user_id,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing is None:
        return {
            "liked": False,
            "likeCount": int(post.like_count or 0),
            "message": "Post was not liked",
        }

    await db.delete(existing)
    post.like_count = max(0, int(post.like_count or 0) - 1)
    await db.commit()
    await db.refresh(post)

    return {
        "liked": False,
        "likeCount": int(post.like_count or 0),
        "message": "Post unliked",
    }


async def create_post_reply(post_id: uuid.UUID, user_id: uuid.UUID, content: str, db: AsyncSession) -> dict:
    await _get_user_or_404(user_id, db)
    post = await _get_post_or_404(post_id, db)

    content_norm = content.strip()
    if not content_norm:
        raise HTTPException(status_code=422, detail="content cannot be blank")

    reply = CommunityReply(
        post_id=post_id,
        parent_reply_id=None,
        user_id=user_id,
        content=content_norm,
    )
    db.add(reply)
    post.reply_count = int(post.reply_count or 0) + 1
    await db.commit()
    await db.refresh(reply)

    return {
        "id": str(reply.id),
        "message": "Reply created successfully",
    }


async def create_reply_reply(parent_reply_id: uuid.UUID, user_id: uuid.UUID, content: str, db: AsyncSession) -> dict:
    await _get_user_or_404(user_id, db)
    parent_reply = await _get_reply_or_404(parent_reply_id, db)
    post = await _get_post_or_404(parent_reply.post_id, db)

    content_norm = content.strip()
    if not content_norm:
        raise HTTPException(status_code=422, detail="content cannot be blank")

    reply = CommunityReply(
        post_id=parent_reply.post_id,
        parent_reply_id=parent_reply_id,
        user_id=user_id,
        content=content_norm,
    )
    db.add(reply)
    post.reply_count = int(post.reply_count or 0) + 1
    await db.commit()
    await db.refresh(reply)

    return {
        "id": str(reply.id),
        "message": "Reply created successfully",
    }


async def like_reply(reply_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict:
    await _get_user_or_404(user_id, db)
    reply = await _get_reply_or_404(reply_id, db)

    existing = await db.execute(
        select(CommunityReplyLike).where(
            CommunityReplyLike.reply_id == reply_id,
            CommunityReplyLike.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return {
            "liked": True,
            "likeCount": int(reply.like_count or 0),
            "message": "Reply already liked",
        }

    db.add(CommunityReplyLike(reply_id=reply_id, user_id=user_id))
    reply.like_count = int(reply.like_count or 0) + 1
    await db.commit()
    await db.refresh(reply)

    return {
        "liked": True,
        "likeCount": int(reply.like_count or 0),
        "message": "Reply liked",
    }


async def unlike_reply(reply_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict:
    reply = await _get_reply_or_404(reply_id, db)

    existing_result = await db.execute(
        select(CommunityReplyLike).where(
            CommunityReplyLike.reply_id == reply_id,
            CommunityReplyLike.user_id == user_id,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing is None:
        return {
            "liked": False,
            "likeCount": int(reply.like_count or 0),
            "message": "Reply was not liked",
        }

    await db.delete(existing)
    reply.like_count = max(0, int(reply.like_count or 0) - 1)
    await db.commit()
    await db.refresh(reply)

    return {
        "liked": False,
        "likeCount": int(reply.like_count or 0),
        "message": "Reply unliked",
    }