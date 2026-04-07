#!/usr/bin/env python3
"""Integration tester for homescreen API endpoints.

This script calls homescreen endpoints and verifies that response data
matches what is stored in PostgreSQL.

Usage:
  python scripts/test_homescreen_api.py --base-url http://127.0.0.1:8000
  python scripts/test_homescreen_api.py --user-id <uuid> --date 2026-04-03 --meal-type Lunch
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import date
import json
import math
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
    user_id: uuid.UUID
    target_date: date
    meal_type: str


class HomeScreenApiTester:
    def __init__(self, base_url: str, timeout: float = 20.0, max_response_chars: int = 2000) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_response_chars = max_response_chars
        self.engine: AsyncEngine = create_async_engine(resolve_database_url(), echo=False)
        self._server_process: subprocess.Popen | None = None

    async def close(self) -> None:
        await self.engine.dispose()

    async def _fetch_scalar(self, sql: str, params: dict | None = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.scalar()

    async def _fetch_one(self, sql: str, params: dict | None = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.one_or_none()

    async def _fetch_all(self, sql: str, params: dict | None = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return result.fetchall()

    async def resolve_context(
        self,
        user_id: str | None,
        date_str: str | None,
        meal_type: str | None,
    ) -> TestContext:
        if user_id:
            resolved_user_id = uuid.UUID(user_id)
        else:
            user_row = await self._fetch_one(
                """
                SELECT id
                FROM users
                ORDER BY created_at ASC
                LIMIT 1
                """
            )
            if user_row:
                resolved_user_id = user_row[0]
            else:
                resolved_user_id = uuid.uuid4()
                async with self.engine.begin() as conn:
                    await conn.execute(
                        text(
                            """
                            INSERT INTO users (id, email, name)
                            VALUES (:id, :email, :name)
                            """
                        ),
                        {
                            "id": resolved_user_id,
                            "email": f"homescreen-test-{resolved_user_id}@local.test",
                            "name": "Homescreen Test User",
                        },
                    )
                print(f"Created test user: {resolved_user_id}")

        if date_str:
            resolved_date = date.fromisoformat(date_str)
        else:
            date_row = await self._fetch_one(
                """
                SELECT service_date
                FROM menu_snapshots
                WHERE service_date <= CURRENT_DATE
                ORDER BY service_date DESC
                LIMIT 1
                """
            )
            if not date_row:
                date_row = await self._fetch_one(
                    """
                    SELECT service_date
                    FROM menu_snapshots
                    ORDER BY service_date DESC
                    LIMIT 1
                    """
                )
            if not date_row:
                raise RuntimeError("No menu_snapshots found in DB. Ingest menu data first.")
            resolved_date = date_row[0]

        if meal_type:
            resolved_meal_type = meal_type.capitalize()
        else:
            meal_row = await self._fetch_one(
                """
                SELECT mt.name
                FROM menu_snapshots ms
                JOIN meal_types mt ON mt.id = ms.meal_type_id
                WHERE ms.service_date = :service_date
                ORDER BY CASE mt.name
                    WHEN 'Breakfast' THEN 1
                    WHEN 'Lunch' THEN 2
                    WHEN 'Dinner' THEN 3
                    ELSE 9
                END
                LIMIT 1
                """,
                {"service_date": resolved_date},
            )
            if not meal_row:
                raise RuntimeError(f"No meal type found for service date {resolved_date}.")
            resolved_meal_type = meal_row[0]

        return TestContext(
            user_id=resolved_user_id,
            target_date=resolved_date,
            meal_type=resolved_meal_type,
        )

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            return requests.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise RuntimeError(f"HTTP request failed for {method} {url}: {exc}") from exc

    def _print_payload(self, endpoint: str, payload: dict) -> None:
        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
        if len(rendered) > self.max_response_chars:
            rendered = (
                rendered[: self.max_response_chars]
                + "\n... [truncated]"
            )
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

    async def test_get_combos(self, ctx: TestContext) -> None:
        response = self._request(
            "GET",
            "/recommendations/combo",
            params={
                "user_id": str(ctx.user_id),
                "date": ctx.target_date.isoformat(),
                "mealType": ctx.meal_type,
            },
        )
        assert response.status_code == 200, f"GET /recommendations/combo failed: {response.status_code} {response.text}"

        payload = response.json()
        assert isinstance(payload, dict) and "combos" in payload, "Combos response missing combos key"
        self._print_payload("GET /recommendations/combo", payload)

        valid_food_rows = await self._fetch_all(
            """
            SELECT DISTINCT msi.food_id
            FROM menu_snapshots ms
            JOIN meal_types mt ON mt.id = ms.meal_type_id
            JOIN menu_sections sec ON sec.snapshot_id = ms.id
            JOIN menu_section_items msi ON msi.section_id = sec.id
            WHERE ms.service_date = :service_date
              AND mt.name = :meal_type
              AND msi.food_id IS NOT NULL
            """,
            {
                "service_date": ctx.target_date,
                "meal_type": ctx.meal_type,
            },
        )
        valid_food_ids = {row[0] for row in valid_food_rows}

        combos = payload["combos"]
        assert isinstance(combos, list), "Combos should be a list"
        for combo in combos:
            assert "items" in combo and isinstance(combo["items"], list), "Combo items missing or invalid"
            for item in combo["items"]:
                assert item["id"] in valid_food_ids, (
                    f"Combo item food_id={item['id']} is not present in DB for "
                    f"date={ctx.target_date} mealType={ctx.meal_type}"
                )

        print(f"[PASS] GET /recommendations/combo ({len(combos)} combos)")

    async def test_get_daily_goals(self, ctx: TestContext) -> None:
        response = self._request(
            "GET",
            "/goals/daily",
            params={
                "user_id": str(ctx.user_id),
                "date": ctx.target_date.isoformat(),
            },
        )
        assert response.status_code == 200, f"GET /goals/daily failed: {response.status_code} {response.text}"

        payload = response.json()
        assert payload.get("date") == ctx.target_date.isoformat(), "Daily goals date mismatch"
        self._print_payload("GET /goals/daily", payload)

        db_row = await self._fetch_one(
            """
            SELECT
                COALESCE(SUM(mli.calories), 0) AS calories,
                COALESCE(SUM(mli.g_protein), 0) AS protein,
                COALESCE(SUM(mli.g_carbs), 0) AS carbs,
                COALESCE(SUM(mli.g_fat), 0) AS fat
            FROM meal_logs ml
            JOIN meal_log_items mli ON mli.meal_log_id = ml.id
            WHERE ml.user_id = :user_id
              AND ml.date = :target_date
            """,
            {
                "user_id": ctx.user_id,
                "target_date": ctx.target_date,
            },
        )

        db_cal = float(db_row[0] or 0)
        db_pro = float(db_row[1] or 0)
        db_carb = float(db_row[2] or 0)
        db_fat = float(db_row[3] or 0)

        api_cal = float(payload["calories"]["consumed"])
        api_pro = float(payload["protein"]["consumed"])
        api_carb = float(payload["carbs"]["consumed"])
        api_fat = float(payload["fat"]["consumed"])

        assert math.isclose(api_cal, db_cal, rel_tol=0.0, abs_tol=0.01), f"Calories mismatch API={api_cal} DB={db_cal}"
        assert math.isclose(api_pro, db_pro, rel_tol=0.0, abs_tol=0.01), f"Protein mismatch API={api_pro} DB={db_pro}"
        assert math.isclose(api_carb, db_carb, rel_tol=0.0, abs_tol=0.01), f"Carbs mismatch API={api_carb} DB={db_carb}"
        assert math.isclose(api_fat, db_fat, rel_tol=0.0, abs_tol=0.01), f"Fat mismatch API={api_fat} DB={db_fat}"

        print("[PASS] GET /goals/daily (consumed macros match DB sums)")

    async def test_get_menu_summary(self, ctx: TestContext) -> None:
        response = self._request(
            "GET",
            "/menus/summary",
            params={
                "user_id": str(ctx.user_id),
                "date": ctx.target_date.isoformat(),
            },
        )
        assert response.status_code == 200, f"GET /menus/summary failed: {response.status_code} {response.text}"

        payload = response.json()
        halls = payload.get("diningHalls", [])
        assert isinstance(halls, list), "diningHalls should be a list"
        self._print_payload("GET /menus/summary", payload)

        hall_food_rows = await self._fetch_all(
            """
            SELECT DISTINCT r.id AS hall_id, msi.food_id
            FROM menu_snapshots ms
            JOIN restaurants r ON r.id = ms.restaurant_id
            JOIN menu_sections sec ON sec.snapshot_id = ms.id
            JOIN menu_section_items msi ON msi.section_id = sec.id
            WHERE ms.service_date = :service_date
              AND msi.food_id IS NOT NULL
            """,
            {"service_date": ctx.target_date},
        )

        valid_by_hall: dict[int, set[int]] = {}
        for hall_id, food_id in hall_food_rows:
            valid_by_hall.setdefault(hall_id, set()).add(food_id)

        for hall in halls:
            hall_id = hall["id"]
            recommended_items = hall.get("recommendedItems", [])
            for item in recommended_items:
                assert item["id"] in valid_by_hall.get(hall_id, set()), (
                    f"Hall {hall_id} returned food_id={item['id']} not found in DB snapshots "
                    f"for date={ctx.target_date}"
                )

        print(f"[PASS] GET /menus/summary ({len(halls)} halls)")

    async def test_post_log_meal(self, ctx: TestContext, keep_data: bool) -> None:
        sample_food = await self._fetch_one(
            """
            SELECT f.id, f.name
            FROM menu_snapshots ms
            JOIN meal_types mt ON mt.id = ms.meal_type_id
            JOIN menu_sections sec ON sec.snapshot_id = ms.id
            JOIN menu_section_items msi ON msi.section_id = sec.id
            JOIN foods f ON f.id = msi.food_id
            WHERE ms.service_date = :service_date
              AND mt.name = :meal_type
            ORDER BY msi.id ASC
            LIMIT 1
            """,
            {
                "service_date": ctx.target_date,
                "meal_type": ctx.meal_type,
            },
        )

        if not sample_food:
            raise RuntimeError(
                f"Could not find a food item for date={ctx.target_date}, mealType={ctx.meal_type}."
            )

        food_id, food_name = sample_food
        payload = {
            "date": ctx.target_date.isoformat(),
            "mealType": ctx.meal_type,
            "items": [
                {
                    "foodId": int(food_id),
                    "foodName": str(food_name),
                    "quantity": 1.0,
                    "source": "homescreen-test",
                }
            ],
        }

        response = self._request(
            "POST",
            "/meals/log",
            params={"user_id": str(ctx.user_id)},
            json=payload,
        )
        assert response.status_code == 201, f"POST /meals/log failed: {response.status_code} {response.text}"

        body = response.json()
        meal_log_id = body.get("mealLogId")
        assert meal_log_id is not None, "POST /meals/log response missing mealLogId"
        self._print_payload("POST /meals/log", body)

        log_row = await self._fetch_one(
            """
            SELECT id, user_id, date, meal_type
            FROM meal_logs
            WHERE id = :meal_log_id
            """,
            {"meal_log_id": meal_log_id},
        )
        assert log_row is not None, f"Meal log id={meal_log_id} not found in DB"
        assert str(log_row[1]) == str(ctx.user_id), "Meal log user_id mismatch"
        assert log_row[2] == ctx.target_date, "Meal log date mismatch"
        assert log_row[3] == ctx.meal_type, "Meal log meal_type mismatch"

        item_row = await self._fetch_one(
            """
            SELECT food_id, food_name, source
            FROM meal_log_items
            WHERE meal_log_id = :meal_log_id
              AND source = 'homescreen-test'
            ORDER BY id DESC
            LIMIT 1
            """,
            {"meal_log_id": meal_log_id},
        )
        assert item_row is not None, "No inserted meal_log_items row found"
        assert int(item_row[0]) == int(food_id), "Logged item food_id mismatch"
        assert item_row[1] == food_name, "Logged item food_name mismatch"

        if not keep_data:
            async with self.engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                        DELETE FROM meal_log_items
                        WHERE meal_log_id = :meal_log_id
                          AND source = 'homescreen-test'
                        """
                    ),
                    {"meal_log_id": meal_log_id},
                )

                remaining = await conn.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM meal_log_items
                        WHERE meal_log_id = :meal_log_id
                        """
                    ),
                    {"meal_log_id": meal_log_id},
                )
                remaining_count = int(remaining.scalar_one())
                if remaining_count == 0:
                    await conn.execute(
                        text("DELETE FROM meal_logs WHERE id = :meal_log_id"),
                        {"meal_log_id": meal_log_id},
                    )

        print("[PASS] POST /meals/log (DB insert verified)")

    async def test_get_menu_summary_with_meal_type(self, ctx: TestContext) -> None:
        """Test that GET /menus/summary accepts mealType filter."""
        response = self._request(
            "GET",
            "/menus/summary",
            params={
                "user_id": str(ctx.user_id),
                "date": ctx.target_date.isoformat(),
                "mealType": ctx.meal_type,
            },
        )
        assert response.status_code == 200, (
            f"GET /menus/summary?mealType failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        assert payload.get("date") == ctx.target_date.isoformat(), "Menu summary date mismatch"
        halls = payload.get("diningHalls", [])
        assert isinstance(halls, list), "diningHalls should be a list"
        self._print_payload("GET /menus/summary?mealType", payload)

        print(f"[PASS] GET /menus/summary?mealType={ctx.meal_type} ({len(halls)} halls)")

    async def test_save_and_delete_favorite(self, ctx: TestContext) -> None:
        """Test POST /favorites and DELETE /favorites/{id} round-trip."""

        # First, get a combo to favorite
        combos_resp = self._request(
            "GET",
            "/recommendations/combo",
            params={
                "user_id": str(ctx.user_id),
                "date": ctx.target_date.isoformat(),
                "mealType": ctx.meal_type,
            },
        )
        assert combos_resp.status_code == 200, f"Combo fetch failed: {combos_resp.status_code}"
        combos = combos_resp.json().get("combos", [])
        if not combos:
            print("[SKIP] POST /favorites — no combos available to favorite")
            return

        combo_id = combos[0]["id"]

        # Keep this test idempotent across repeated runs.
        existing_fav = await self._fetch_one(
            """
            SELECT id
            FROM favorites
            WHERE user_id = CAST(:user_id AS uuid)
              AND combo_id = CAST(:combo_id AS uuid)
            LIMIT 1
            """,
            {"user_id": str(ctx.user_id), "combo_id": combo_id},
        )
        if existing_fav:
            existing_fav_id = str(existing_fav[0])
            cleanup_resp = self._request(
                "DELETE",
                f"/favorites/{existing_fav_id}",
                params={"user_id": str(ctx.user_id)},
            )
            assert cleanup_resp.status_code == 200, (
                "Failed to clean up pre-existing favorite "
                f"{existing_fav_id}: {cleanup_resp.status_code} {cleanup_resp.text}"
            )

        # Save favorite
        save_resp = self._request(
            "POST",
            "/favorites",
            params={"user_id": str(ctx.user_id)},
            json={"comboId": combo_id},
        )
        assert save_resp.status_code == 201, (
            f"POST /favorites failed: {save_resp.status_code} {save_resp.text}"
        )

        save_body = save_resp.json()
        favorite_id = save_body.get("id")
        assert favorite_id is not None, "POST /favorites response missing id"
        self._print_payload("POST /favorites", save_body)

        # Verify in DB
        fav_row = await self._fetch_one(
            "SELECT id, user_id, combo_id FROM favorites WHERE id = CAST(:fav_id AS uuid)",
            {"fav_id": favorite_id},
        )
        assert fav_row is not None, f"Favorite id={favorite_id} not found in DB"
        assert str(fav_row[1]) == str(ctx.user_id), "Favorite user_id mismatch"

        print("[PASS] POST /favorites (DB insert verified)")

        # Test duplicate (should 409)
        dup_resp = self._request(
            "POST",
            "/favorites",
            params={"user_id": str(ctx.user_id)},
            json={"comboId": combo_id},
        )
        assert dup_resp.status_code == 409, (
            f"Duplicate POST /favorites should return 409, got {dup_resp.status_code}"
        )
        print("[PASS] POST /favorites duplicate returns 409")

        # Delete favorite
        del_resp = self._request(
            "DELETE",
            f"/favorites/{favorite_id}",
            params={"user_id": str(ctx.user_id)},
        )
        assert del_resp.status_code == 200, (
            f"DELETE /favorites/{favorite_id} failed: {del_resp.status_code} {del_resp.text}"
        )
        self._print_payload(f"DELETE /favorites/{favorite_id}", del_resp.json())

        # Verify deletion
        fav_row_after = await self._fetch_one(
            "SELECT id FROM favorites WHERE id = CAST(:fav_id AS uuid)",
            {"fav_id": favorite_id},
        )
        assert fav_row_after is None, "Favorite should be deleted from DB"

        print("[PASS] DELETE /favorites (DB deletion verified)")

    async def test_get_addons(self, ctx: TestContext) -> None:
        """Test GET /recommendations/addons returns suggestions and quick add-ons."""
        response = self._request(
            "GET",
            "/recommendations/addons",
            params={
                "user_id": str(ctx.user_id),
                "date": ctx.target_date.isoformat(),
                "mealType": ctx.meal_type,
            },
        )
        assert response.status_code == 200, (
            f"GET /recommendations/addons failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        assert "mealType" in payload, "Addons response missing mealType"
        assert "suggestions" in payload, "Addons response missing suggestions"
        assert "quickAddons" in payload, "Addons response missing quickAddons"
        assert isinstance(payload["suggestions"], list), "suggestions should be a list"
        assert isinstance(payload["quickAddons"], list), "quickAddons should be a list"
        self._print_payload("GET /recommendations/addons", payload)

        # Verify suggestion items have expected fields
        for item in payload["suggestions"]:
            assert "id" in item and "name" in item, "Suggestion item missing id or name"
            assert "calories" in item, "Suggestion item missing calories"

        # Verify quick add-ons are low-calorie
        for item in payload["quickAddons"]:
            assert "id" in item and "name" in item, "Quick addon item missing id or name"
            if item.get("calories") is not None:
                assert item["calories"] < 150, (
                    f"Quick addon '{item['name']}' has {item['calories']} cal (expected <150)"
                )

        print(
            f"[PASS] GET /recommendations/addons "
            f"({len(payload['suggestions'])} suggestions, {len(payload['quickAddons'])} quick add-ons)"
        )


async def run_tests(args: argparse.Namespace) -> int:
    tester = HomeScreenApiTester(
        base_url=args.base_url,
        timeout=args.timeout,
        max_response_chars=args.max_response_chars,
    )
    try:
        tester.ensure_local_server()
        context = await tester.resolve_context(args.user_id, args.date, args.meal_type)
        print(
            "Running homescreen integration checks with "
            f"user_id={context.user_id} date={context.target_date} mealType={context.meal_type}"
        )

        await tester.test_get_combos(context)
        await tester.test_get_daily_goals(context)
        await tester.test_get_menu_summary(context)
        await tester.test_get_menu_summary_with_meal_type(context)
        await tester.test_post_log_meal(context, keep_data=args.keep_data)
        await tester.test_save_and_delete_favorite(context)
        await tester.test_get_addons(context)

        print("\nAll homescreen API integration checks passed.")
        return 0
    except (AssertionError, RuntimeError, ValueError) as exc:
        print(f"\n[FAIL] {exc}")
        return 1
    finally:
        tester.stop_local_server()
        await tester.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Homescreen API integration tester")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of running FastAPI app (default: %(default)s)",
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help="User UUID for tests. If omitted, first user in DB is used.",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Service date YYYY-MM-DD. If omitted, latest available menu date is used.",
    )
    parser.add_argument(
        "--meal-type",
        default=None,
        help="Meal type (Breakfast/Lunch/Dinner). If omitted, one available on date is selected.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Keep inserted test meal log data (default removes test rows).",
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
