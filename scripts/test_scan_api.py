#!/usr/bin/env python3
"""Integration tester for scan API endpoints.

This script calls scan endpoints and verifies that logging persists
into meal_logs / meal_log_items in PostgreSQL.

Usage:
  python scripts/test_scan_api.py --base-url http://127.0.0.1:8000
  python scripts/test_scan_api.py --user-id <uuid>
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import date
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
    user_id: uuid.UUID
    target_date: date
    meal_type: str


class ScanApiTester:
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

    async def _fetch_scalar(self, sql: str, params: dict | None = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.scalar()

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

    def _server_is_ready(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/", timeout=1.5)
            return resp.status_code < 500
        except requests.RequestException:
            return False

    def ensure_local_server(self) -> None:
        if self._server_is_ready():
            return

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

    async def _create_user(self) -> uuid.UUID:
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
                    "email": f"scan-test-{user_id}@local.test",
                    "name": "Scan Test User",
                },
            )
        return user_id

    async def resolve_context(self, user_id: str | None) -> TestContext:
        if user_id:
            resolved_user = uuid.UUID(user_id)
            row = await self._fetch_one("SELECT id FROM users WHERE id = :id", {"id": resolved_user})
            if row is None:
                raise RuntimeError(f"Provided user_id={resolved_user} does not exist in users table.")
        else:
            row = await self._fetch_one("SELECT id FROM users ORDER BY created_at ASC LIMIT 1")
            resolved_user = row[0] if row else await self._create_user()

        return TestContext(user_id=resolved_user, target_date=date.today(), meal_type="scan-test")

    @staticmethod
    def _sample_png_bytes() -> bytes:
        # 1x1 transparent PNG
        return (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    def test_scan(self, ctx: TestContext) -> dict:
        files = {
            "image": ("meal.png", self._sample_png_bytes(), "image/png"),
        }
        response = self._request("POST", "/scan", params={"user_id": str(ctx.user_id)}, files=files)
        assert response.status_code == 200, f"POST /scan failed: {response.status_code} {response.text}"

        payload = response.json()
        self._print_payload("POST /scan", payload)

        assert payload.get("scanId"), "scanId missing"
        assert isinstance(payload.get("items"), list) and payload["items"], "items missing"
        assert isinstance(payload.get("summary"), dict), "summary missing"

        for item in payload["items"]:
            for key in ("name", "confidence", "calories", "protein", "carbs", "fat"):
                assert key in item, f"item missing key={key}"

        print("[PASS] POST /scan")
        return payload

    async def test_scan_log(self, ctx: TestContext, scan_payload: dict) -> None:
        before_count = await self._fetch_scalar(
            """
            SELECT COUNT(*)
            FROM meal_log_items mli
            JOIN meal_logs ml ON ml.id = mli.meal_log_id
            WHERE ml.user_id = :user_id
              AND ml.date = :target_date
              AND ml.meal_type = :meal_type
              AND mli.source = 'scan'
            """,
            {
                "user_id": ctx.user_id,
                "target_date": ctx.target_date,
                "meal_type": ctx.meal_type,
            },
        )
        before_count = int(before_count or 0)

        request_body = {
            "scanId": scan_payload["scanId"],
            "mealType": ctx.meal_type,
            "date": ctx.target_date.isoformat(),
            "items": [
                {
                    "name": item["name"],
                    "calories": item["calories"],
                    "protein": item["protein"],
                    "carbs": item["carbs"],
                    "fat": item["fat"],
                }
                for item in scan_payload["items"]
            ],
        }

        response = self._request(
            "POST",
            "/scan/log",
            params={"user_id": str(ctx.user_id)},
            json=request_body,
        )
        assert response.status_code == 201, f"POST /scan/log failed: {response.status_code} {response.text}"

        payload = response.json()
        self._print_payload("POST /scan/log", payload)

        assert int(payload.get("loggedCount", -1)) == len(scan_payload["items"]), "loggedCount mismatch"
        assert payload.get("mealLogId"), "mealLogId missing"

        after_count = await self._fetch_scalar(
            """
            SELECT COUNT(*)
            FROM meal_log_items mli
            JOIN meal_logs ml ON ml.id = mli.meal_log_id
            WHERE ml.user_id = :user_id
              AND ml.date = :target_date
              AND ml.meal_type = :meal_type
              AND mli.source = 'scan'
            """,
            {
                "user_id": ctx.user_id,
                "target_date": ctx.target_date,
                "meal_type": ctx.meal_type,
            },
        )
        after_count = int(after_count or 0)

        expected_delta = len(scan_payload["items"])
        assert after_count - before_count == expected_delta, (
            f"Scan log item count delta mismatch. before={before_count}, after={after_count}, "
            f"expected_delta={expected_delta}"
        )

        print("[PASS] POST /scan/log (DB persistence verified)")

    async def run(self, user_id: str | None) -> None:
        self.ensure_local_server()
        ctx = await self.resolve_context(user_id)

        print("\n=== Scan API Test Context ===")
        print(f"Base URL:  {self.base_url}")
        print(f"User ID:   {ctx.user_id}")
        print(f"Date:      {ctx.target_date}")
        print(f"Meal Type: {ctx.meal_type}")

        scan_payload = self.test_scan(ctx)
        await self.test_scan_log(ctx, scan_payload)

        print("\n[DONE] All scan endpoint tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Integration tester for scan API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL for the API")
    parser.add_argument("--user-id", default=None, help="Existing user UUID to use for tests")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    tester = ScanApiTester(base_url=args.base_url)
    try:
        await tester.run(args.user_id)
    finally:
        tester.stop_local_server()
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
