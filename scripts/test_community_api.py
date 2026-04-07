#!/usr/bin/env python3
"""Integration tester for community API endpoints.

This script calls community endpoints and verifies that response data
matches what is stored in PostgreSQL.

Usage:
  python scripts/test_community_api.py --base-url http://127.0.0.1:8000
  python scripts/test_community_api.py --user-id <uuid> --other-user-id <uuid>
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

# Ensure project root is importable when executing this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_project_python() -> Path | None:
    candidates = [
        PROJECT_ROOT / ".venv" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "bin" / "python3",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def ensure_project_python() -> None:
    """Re-exec with project .venv python when launched from system Python."""
    venv_python = get_project_python()
    if venv_python is None:
        return

    target_python = venv_python
    target_venv = target_python.parent.parent.resolve()

    # Prefer environment identity over executable identity because
    # .venv/bin/python can be a symlink to system python.
    in_target_venv = Path(sys.prefix).resolve() == target_venv

    if not in_target_venv and os.getenv("WTE_SKIP_REEXEC") != "1":
        os.execve(
            str(target_python),
            [str(target_python), *sys.argv],
            {**os.environ, "WTE_SKIP_REEXEC": "1"},
        )


ensure_project_python()

import requests
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def resolve_database_url() -> str:
    from_env = os.getenv("DATABASE_URL")
    if from_env:
        return from_env

    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return value.strip().strip('"').strip("'")

    return "postgresql+asyncpg://postgres:password@localhost:5432/whattoeat"


@dataclass
class TestContext:
    author_user_id: uuid.UUID
    actor_user_id: uuid.UUID


class CommunityApiTester:
    def __init__(self, base_url: str, timeout: float = 20.0, max_response_chars: int = 2000) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_response_chars = max_response_chars
        self.engine: AsyncEngine = create_async_engine(resolve_database_url(), echo=False)
        self._server_process: subprocess.Popen | None = None

    async def close(self) -> None:
        await self.engine.dispose()

    async def _fetch_one(self, sql: str, params: dict | None = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.one_or_none()

    async def _fetch_all(self, sql: str, params: dict | None = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.fetchall()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            return requests.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise RuntimeError(f"HTTP request failed for {method} {url}: {exc}") from exc

    def _print_payload(self, endpoint: str, payload: dict) -> None:
        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
        if len(rendered) > self.max_response_chars:
            rendered = rendered[: self.max_response_chars] + "\n... [truncated]"
        print(f"\n[API] {endpoint} response:\n{rendered}\n")

    @staticmethod
    def _announce(purpose: str) -> None:
        print(f"[INFO] API purpose: {purpose}")

    def _server_is_ready(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/", timeout=1.5)
            return resp.status_code < 500
        except requests.RequestException:
            return False

    def ensure_local_server(self) -> None:
        if self._server_is_ready():
            return

        # Start local uvicorn only when default local host is used.
        if not self.base_url.startswith("http://127.0.0.1:"):
            raise RuntimeError(
                f"API is unreachable at {self.base_url}. Start the server manually for non-local base URLs."
            )

        host_port = self.base_url.removeprefix("http://")
        host, port = host_port.split(":", 1)
        project_python = get_project_python()
        python_bin = str(project_python) if project_python else sys.executable

        self._server_process = subprocess.Popen(
            [
                python_bin,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                host,
                "--port",
                port,
            ],
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "WTE_SKIP_REEXEC": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        deadline = time.time() + 25
        while time.time() < deadline:
            if self._server_process.poll() is not None:
                output = ""
                if self._server_process.stdout is not None:
                    output = (self._server_process.stdout.read() or "").strip()
                # If startup was interrupted (e.g., Ctrl+C), surface a clean cancellation.
                if "KeyboardInterrupt" in output or "CancelledError" in output:
                    raise KeyboardInterrupt("Interrupted during local server startup")
                msg = "Auto-started uvicorn exited early."
                if output:
                    msg = f"{msg} Output: {output}"
                raise RuntimeError(msg)
            if self._server_is_ready():
                print("Auto-started local API server for integration test.")
                return
            time.sleep(0.5)

        raise RuntimeError("Timed out waiting for local API server startup.")

    def stop_local_server(self) -> None:
        if self._server_process is None:
            return
        if self._server_process.poll() is None:
            self._server_process.terminate()
            try:
                self._server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_process.kill()
        self._server_process = None

    async def _create_user(self, label: str) -> uuid.UUID:
        user_id = uuid.uuid4()
        async with self.engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    INSERT INTO users (id, email, name)
                    VALUES (:id, :email, :name)
                    """
                ),
                {
                    "id": user_id,
                    "email": f"community-{label}-{user_id}@local.test",
                    "name": f"Community {label.title()} User",
                },
            )
        return user_id

    async def _ensure_user(self, user_id: str | None, label: str) -> uuid.UUID:
        if user_id:
            resolved = uuid.UUID(user_id)
            row = await self._fetch_one("SELECT id FROM users WHERE id = :id", {"id": resolved})
            if row is None:
                raise RuntimeError(f"Provided user_id={resolved} does not exist in users table.")
            return resolved

        row = await self._fetch_one("SELECT id FROM users ORDER BY created_at ASC LIMIT 1")
        if row:
            return row[0]
        return await self._create_user(label)

    async def resolve_context(self, user_id: str | None, other_user_id: str | None) -> TestContext:
        author = await self._ensure_user(user_id, "author")

        if other_user_id:
            actor = uuid.UUID(other_user_id)
            row = await self._fetch_one("SELECT id FROM users WHERE id = :id", {"id": actor})
            if row is None:
                raise RuntimeError(f"Provided other_user_id={actor} does not exist in users table.")
            if actor == author:
                raise RuntimeError("other_user_id must be different from user_id.")
            return TestContext(author_user_id=author, actor_user_id=actor)

        rows = await self._fetch_all("SELECT id FROM users ORDER BY created_at ASC LIMIT 5")
        actor: uuid.UUID | None = None
        for row in rows:
            candidate = row[0]
            if candidate != author:
                actor = candidate
                break
        if actor is None:
            actor = await self._create_user("actor")

        return TestContext(author_user_id=author, actor_user_id=actor)

    async def test_get_posts_feed(self) -> None:
        self._announce("Load the public community feed so users can browse recent dining posts.")
        response = self._request("GET", "/community/posts", params={"page": 1, "limit": 10})
        assert response.status_code == 200, f"GET /community/posts failed: {response.status_code} {response.text}"

        payload = response.json()
        assert isinstance(payload, dict), "Feed response should be an object"
        assert isinstance(payload.get("posts"), list), "Feed response missing posts list"
        self._print_payload("GET /community/posts", payload)
        print(f"[PASS] GET /community/posts ({len(payload['posts'])} posts)")

    async def test_create_post(self, ctx: TestContext) -> uuid.UUID:
        self._announce("Create a new community post so users can share dining hall food reviews.")
        body = {
            "content": "Roasted turkey plate was amazing tonight. Highly recommend.",
            "hallTag": "Gordon",
            "imageUrl": "https://example.com/community/turkey-plate.jpg",
        }
        response = self._request(
            "POST",
            "/community/posts",
            params={"user_id": str(ctx.author_user_id)},
            json=body,
        )
        assert response.status_code == 201, f"POST /community/posts failed: {response.status_code} {response.text}"

        payload = response.json()
        self._print_payload("POST /community/posts", payload)

        post_id = payload.get("id")
        assert post_id, "POST /community/posts response missing id"

        db_row = await self._fetch_one(
            """
            SELECT id, user_id, content, hall_tag, image_url, like_count, reply_count
            FROM community_posts
            WHERE id = CAST(:post_id AS uuid)
            """,
            {"post_id": post_id},
        )
        assert db_row is not None, "Inserted community post not found in DB"
        assert str(db_row[1]) == str(ctx.author_user_id), "Post user_id mismatch"
        assert db_row[2] == body["content"], "Post content mismatch"
        assert (db_row[3] or "") == body["hallTag"], "Post hall_tag mismatch"
        assert (db_row[4] or "") == body["imageUrl"], "Post image_url mismatch"
        assert int(db_row[5]) == 0, "Initial like_count should be 0"
        assert int(db_row[6]) == 0, "Initial reply_count should be 0"

        print("[PASS] POST /community/posts (DB insert verified)")
        return uuid.UUID(post_id)

    async def test_get_post_detail(self, post_id: uuid.UUID, viewer_user_id: uuid.UUID) -> None:
        self._announce("Open post detail so users can read one post and its full discussion thread.")
        response = self._request(
            "GET",
            f"/community/posts/{post_id}",
            params={"user_id": str(viewer_user_id)},
        )
        assert response.status_code == 200, (
            f"GET /community/posts/{post_id} failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        self._print_payload(f"GET /community/posts/{post_id}", payload)

        post = payload.get("post")
        assert isinstance(post, dict), "Post detail response missing post object"
        assert post.get("id") == str(post_id), "Post detail id mismatch"
        assert isinstance(payload.get("replies"), list), "Post detail replies should be a list"

        print(f"[PASS] GET /community/posts/{post_id}")

    async def test_like_and_unlike_post(self, post_id: uuid.UUID, actor_user_id: uuid.UUID) -> None:
        pre = await self._fetch_one(
            "SELECT like_count FROM community_posts WHERE id = CAST(:post_id AS uuid)",
            {"post_id": str(post_id)},
        )
        pre_count = int(pre[0]) if pre else 0

        self._announce("Like a post so the post like count increases by 1 and reflects user engagement.")
        like_resp = self._request(
            "POST",
            f"/community/posts/{post_id}/likes",
            params={"user_id": str(actor_user_id)},
        )
        assert like_resp.status_code == 200, (
            f"POST /community/posts/{post_id}/likes failed: {like_resp.status_code} {like_resp.text}"
        )
        like_payload = like_resp.json()
        self._print_payload(f"POST /community/posts/{post_id}/likes", like_payload)
        assert like_payload.get("liked") is True, "Like response should return liked=true"
        assert int(like_payload.get("likeCount", -1)) == pre_count + 1, "Like count should increase by 1"

        like_row = await self._fetch_one(
            """
            SELECT id
            FROM community_post_likes
            WHERE post_id = CAST(:post_id AS uuid)
              AND user_id = CAST(:user_id AS uuid)
            """,
            {"post_id": str(post_id), "user_id": str(actor_user_id)},
        )
        assert like_row is not None, "Post like row should exist after like"
        print("[PASS] POST /community/posts/{postId}/likes (count increment + DB row verified)")

        self._announce("Unlike a post so the post like count decreases by 1 when user removes their like.")
        unlike_resp = self._request(
            "DELETE",
            f"/community/posts/{post_id}/likes",
            params={"user_id": str(actor_user_id)},
        )
        assert unlike_resp.status_code == 200, (
            f"DELETE /community/posts/{post_id}/likes failed: {unlike_resp.status_code} {unlike_resp.text}"
        )
        unlike_payload = unlike_resp.json()
        self._print_payload(f"DELETE /community/posts/{post_id}/likes", unlike_payload)
        assert unlike_payload.get("liked") is False, "Unlike response should return liked=false"
        assert int(unlike_payload.get("likeCount", -1)) == pre_count, "Like count should return to previous value"

        like_row_after = await self._fetch_one(
            """
            SELECT id
            FROM community_post_likes
            WHERE post_id = CAST(:post_id AS uuid)
              AND user_id = CAST(:user_id AS uuid)
            """,
            {"post_id": str(post_id), "user_id": str(actor_user_id)},
        )
        assert like_row_after is None, "Post like row should be removed after unlike"
        print("[PASS] DELETE /community/posts/{postId}/likes (count decrement + DB row removal verified)")

    async def test_create_replies(
        self,
        post_id: uuid.UUID,
        root_reply_user_id: uuid.UUID,
        nested_reply_user_id: uuid.UUID,
    ) -> tuple[uuid.UUID, uuid.UUID]:
        self._announce("Add a top-level reply so users can comment directly on a community post.")
        root_resp = self._request(
            "POST",
            f"/community/posts/{post_id}/replies",
            params={"user_id": str(root_reply_user_id)},
            json={"content": "Tried it too, super flavorful and filling."},
        )
        assert root_resp.status_code == 201, (
            f"POST /community/posts/{post_id}/replies failed: {root_resp.status_code} {root_resp.text}"
        )
        root_payload = root_resp.json()
        self._print_payload(f"POST /community/posts/{post_id}/replies", root_payload)

        root_reply_id = root_payload.get("id")
        assert root_reply_id, "Root reply response missing id"

        root_db = await self._fetch_one(
            """
            SELECT id, post_id, parent_reply_id, user_id
            FROM community_replies
            WHERE id = CAST(:reply_id AS uuid)
            """,
            {"reply_id": root_reply_id},
        )
        assert root_db is not None, "Root reply row not found in DB"
        assert str(root_db[1]) == str(post_id), "Root reply post_id mismatch"
        assert root_db[2] is None, "Root reply should have null parent_reply_id"
        assert str(root_db[3]) == str(root_reply_user_id), "Root reply user mismatch"
        print("[PASS] POST /community/posts/{postId}/replies (DB insert verified)")

        self._announce("Add a nested reply so users can reply to another comment in a thread.")
        nested_resp = self._request(
            "POST",
            f"/community/replies/{root_reply_id}/replies",
            params={"user_id": str(nested_reply_user_id)},
            json={"content": "Agree, this is my new weekly favorite."},
        )
        assert nested_resp.status_code == 201, (
            "POST /community/replies/{replyId}/replies failed: "
            f"{nested_resp.status_code} {nested_resp.text}"
        )
        nested_payload = nested_resp.json()
        self._print_payload(f"POST /community/replies/{root_reply_id}/replies", nested_payload)

        nested_reply_id = nested_payload.get("id")
        assert nested_reply_id, "Nested reply response missing id"

        nested_db = await self._fetch_one(
            """
            SELECT id, post_id, parent_reply_id, user_id
            FROM community_replies
            WHERE id = CAST(:reply_id AS uuid)
            """,
            {"reply_id": nested_reply_id},
        )
        assert nested_db is not None, "Nested reply row not found in DB"
        assert str(nested_db[1]) == str(post_id), "Nested reply post_id mismatch"
        assert str(nested_db[2]) == str(root_reply_id), "Nested reply parent_reply_id mismatch"
        assert str(nested_db[3]) == str(nested_reply_user_id), "Nested reply user mismatch"
        print("[PASS] POST /community/replies/{replyId}/replies (DB insert verified)")

        post_count_row = await self._fetch_one(
            "SELECT reply_count FROM community_posts WHERE id = CAST(:post_id AS uuid)",
            {"post_id": str(post_id)},
        )
        assert post_count_row is not None and int(post_count_row[0]) == 2, "Post reply_count should be 2"

        return uuid.UUID(root_reply_id), uuid.UUID(nested_reply_id)

    async def test_like_and_unlike_reply(self, reply_id: uuid.UUID, actor_user_id: uuid.UUID) -> None:
        pre = await self._fetch_one(
            "SELECT like_count FROM community_replies WHERE id = CAST(:reply_id AS uuid)",
            {"reply_id": str(reply_id)},
        )
        pre_count = int(pre[0]) if pre else 0

        self._announce("Like a reply so reply like count increases by 1 in threaded discussions.")
        like_resp = self._request(
            "POST",
            f"/community/replies/{reply_id}/likes",
            params={"user_id": str(actor_user_id)},
        )
        assert like_resp.status_code == 200, (
            f"POST /community/replies/{reply_id}/likes failed: {like_resp.status_code} {like_resp.text}"
        )
        like_payload = like_resp.json()
        self._print_payload(f"POST /community/replies/{reply_id}/likes", like_payload)
        assert like_payload.get("liked") is True, "Reply like response should return liked=true"
        assert int(like_payload.get("likeCount", -1)) == pre_count + 1, "Reply like count should increase by 1"

        like_row = await self._fetch_one(
            """
            SELECT id
            FROM community_reply_likes
            WHERE reply_id = CAST(:reply_id AS uuid)
              AND user_id = CAST(:user_id AS uuid)
            """,
            {"reply_id": str(reply_id), "user_id": str(actor_user_id)},
        )
        assert like_row is not None, "Reply like row should exist after like"
        print("[PASS] POST /community/replies/{replyId}/likes (count increment + DB row verified)")

        self._announce("Unlike a reply so reply like count decreases by 1 when user removes their reaction.")
        unlike_resp = self._request(
            "DELETE",
            f"/community/replies/{reply_id}/likes",
            params={"user_id": str(actor_user_id)},
        )
        assert unlike_resp.status_code == 200, (
            f"DELETE /community/replies/{reply_id}/likes failed: {unlike_resp.status_code} {unlike_resp.text}"
        )
        unlike_payload = unlike_resp.json()
        self._print_payload(f"DELETE /community/replies/{reply_id}/likes", unlike_payload)
        assert unlike_payload.get("liked") is False, "Reply unlike response should return liked=false"
        assert int(unlike_payload.get("likeCount", -1)) == pre_count, "Reply like count should return to previous value"

        like_row_after = await self._fetch_one(
            """
            SELECT id
            FROM community_reply_likes
            WHERE reply_id = CAST(:reply_id AS uuid)
              AND user_id = CAST(:user_id AS uuid)
            """,
            {"reply_id": str(reply_id), "user_id": str(actor_user_id)},
        )
        assert like_row_after is None, "Reply like row should be removed after unlike"
        print("[PASS] DELETE /community/replies/{replyId}/likes (count decrement + DB row removal verified)")

    async def test_detail_contains_nested_thread(self, post_id: uuid.UUID, viewer_user_id: uuid.UUID) -> None:
        self._announce("Fetch post detail so UI can render nested reply threads in Community Details screen.")
        response = self._request(
            "GET",
            f"/community/posts/{post_id}",
            params={"user_id": str(viewer_user_id)},
        )
        assert response.status_code == 200, (
            f"GET /community/posts/{post_id} failed: {response.status_code} {response.text}"
        )
        payload = response.json()
        self._print_payload(f"GET /community/posts/{post_id} (thread check)", payload)

        roots = payload.get("replies", [])
        assert len(roots) >= 1, "Expected at least one top-level reply"
        assert isinstance(roots[0].get("replies"), list), "Top-level reply should include nested replies list"
        assert len(roots[0]["replies"]) >= 1, "Expected at least one nested reply"

        print("[PASS] GET /community/posts/{postId} nested thread structure verified")

    async def test_delete_post_permissions(self, post_id: uuid.UUID, owner_user_id: uuid.UUID, other_user_id: uuid.UUID) -> None:
        self._announce("Enforce ownership so only the post author can delete their own post.")
        denied = self._request(
            "DELETE",
            f"/community/posts/{post_id}",
            params={"user_id": str(other_user_id)},
        )
        assert denied.status_code == 403, (
            "DELETE /community/posts/{postId} as non-owner should return 403, "
            f"got {denied.status_code} {denied.text}"
        )
        print("[PASS] DELETE /community/posts/{postId} non-owner denied")

        self._announce("Delete an owned post so users can remove their own content and its related interactions.")
        deleted = self._request(
            "DELETE",
            f"/community/posts/{post_id}",
            params={"user_id": str(owner_user_id)},
        )
        assert deleted.status_code == 200, (
            f"DELETE /community/posts/{post_id} failed: {deleted.status_code} {deleted.text}"
        )
        self._print_payload(f"DELETE /community/posts/{post_id}", deleted.json())

        post_row = await self._fetch_one(
            "SELECT id FROM community_posts WHERE id = CAST(:post_id AS uuid)",
            {"post_id": str(post_id)},
        )
        assert post_row is None, "Post should be deleted from DB"

        replies_remaining = await self._fetch_one(
            "SELECT COUNT(*) FROM community_replies WHERE post_id = CAST(:post_id AS uuid)",
            {"post_id": str(post_id)},
        )
        assert replies_remaining is not None and int(replies_remaining[0]) == 0, "Replies should be removed with post"

        likes_remaining = await self._fetch_one(
            "SELECT COUNT(*) FROM community_post_likes WHERE post_id = CAST(:post_id AS uuid)",
            {"post_id": str(post_id)},
        )
        assert likes_remaining is not None and int(likes_remaining[0]) == 0, "Post likes should be removed with post"

        print("[PASS] DELETE /community/posts/{postId} owner delete + cascade cleanup verified")


async def run_tests(args: argparse.Namespace) -> int:
    tester = CommunityApiTester(
        base_url=args.base_url,
        timeout=args.timeout,
        max_response_chars=args.max_response_chars,
    )
    try:
        tester.ensure_local_server()
        context = await tester.resolve_context(args.user_id, args.other_user_id)
        print(
            "Running community integration checks with "
            f"author_user_id={context.author_user_id} actor_user_id={context.actor_user_id}"
        )

        await tester.test_get_posts_feed()
        post_id = await tester.test_create_post(context)
        await tester.test_get_post_detail(post_id, context.author_user_id)
        await tester.test_like_and_unlike_post(post_id, context.actor_user_id)
        root_reply_id, nested_reply_id = await tester.test_create_replies(
            post_id,
            context.actor_user_id,
            context.author_user_id,
        )
        await tester.test_like_and_unlike_reply(root_reply_id, context.author_user_id)
        await tester.test_like_and_unlike_reply(nested_reply_id, context.actor_user_id)
        await tester.test_detail_contains_nested_thread(post_id, context.author_user_id)
        await tester.test_delete_post_permissions(post_id, context.author_user_id, context.actor_user_id)

        print("\nAll community API integration checks passed.")
        return 0
    except (AssertionError, RuntimeError, ValueError) as exc:
        print(f"\n[FAIL] {exc}")
        return 1
    except KeyboardInterrupt:
        print("\n[CANCELLED] Community API integration test interrupted by user.")
        return 130
    finally:
        tester.stop_local_server()
        await tester.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Community API integration tester")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of running FastAPI app (default: %(default)s)",
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help="Author user UUID for tests. If omitted, first user in DB is used.",
    )
    parser.add_argument(
        "--other-user-id",
        default=None,
        help="Second user UUID for interaction tests. If omitted, another user is selected/created.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--max-response-chars",
        type=int,
        default=2000,
        help="Maximum characters to print per API response (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return asyncio.run(run_tests(args))


if __name__ == "__main__":
    sys.exit(main())