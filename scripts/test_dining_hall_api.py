#!/usr/bin/env python3
"""Integration tester for dining hall API endpoints.

This script calls dining hall endpoints and verifies that response data
matches what is stored in PostgreSQL.

Usage:
  python scripts/test_dining_hall_api.py --base-url http://127.0.0.1:8000
  python scripts/test_dining_hall_api.py --hall-id 1 --date 2026-04-03 --meal-type Lunch
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
    hall_id: int
    hall_name: str
    target_date: date
    meal_type: str | None


class DiningHallApiTester:
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

    async def resolve_context(
        self,
        user_id: str | None,
        hall_id: int | None,
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
                            "email": f"dining-test-{resolved_user_id}@local.test",
                            "name": "Dining Hall Test User",
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

        if hall_id is not None:
            hall_row = await self._fetch_one(
                """
                SELECT id, name
                FROM restaurants
                WHERE id = :hall_id
                LIMIT 1
                """,
                {"hall_id": hall_id},
            )
            if not hall_row:
                raise RuntimeError(f"Hall id={hall_id} does not exist in restaurants table.")
            resolved_hall_id = int(hall_row[0])
            resolved_hall_name = str(hall_row[1])
        else:
            hall_row = await self._fetch_one(
                """
                SELECT r.id, r.name
                FROM menu_snapshots ms
                JOIN restaurants r ON r.id = ms.restaurant_id
                WHERE ms.service_date = :service_date
                ORDER BY r.name ASC
                LIMIT 1
                """,
                {"service_date": resolved_date},
            )
            if not hall_row:
                hall_row = await self._fetch_one(
                    """
                    SELECT id, name
                    FROM restaurants
                    ORDER BY name ASC
                    LIMIT 1
                    """
                )
            if not hall_row:
                raise RuntimeError("No restaurants found in DB.")
            resolved_hall_id = int(hall_row[0])
            resolved_hall_name = str(hall_row[1])

        if meal_type:
            resolved_meal_type = meal_type.capitalize()
        else:
            meal_row = await self._fetch_one(
                """
                SELECT mt.name
                FROM menu_snapshots ms
                JOIN meal_types mt ON mt.id = ms.meal_type_id
                WHERE ms.service_date = :service_date
                  AND ms.restaurant_id = :restaurant_id
                ORDER BY CASE mt.name
                    WHEN 'Breakfast' THEN 1
                    WHEN 'Lunch' THEN 2
                    WHEN 'Dinner' THEN 3
                    ELSE 9
                END
                LIMIT 1
                """,
                {"service_date": resolved_date, "restaurant_id": resolved_hall_id},
            )
            resolved_meal_type = str(meal_row[0]) if meal_row else None

        return TestContext(
            user_id=resolved_user_id,
            hall_id=resolved_hall_id,
            hall_name=resolved_hall_name,
            target_date=resolved_date,
            meal_type=resolved_meal_type,
        )

    async def test_list_dining_halls(self) -> None:
        response = self._request("GET", "/dining-halls")
        assert response.status_code == 200, f"GET /dining-halls failed: {response.status_code} {response.text}"

        payload = response.json()
        assert isinstance(payload, dict), "Dining halls response should be an object"
        assert "diningHalls" in payload, "Dining halls response missing diningHalls"
        halls = payload["diningHalls"]
        assert isinstance(halls, list), "diningHalls should be a list"
        self._print_payload("GET /dining-halls", payload)

        db_rows = await self._fetch_all(
            """
            SELECT id
            FROM restaurants
            ORDER BY id
            """
        )
        db_ids = {int(r[0]) for r in db_rows}
        api_ids = {int(h["id"]) for h in halls}

        assert api_ids == db_ids, (
            "Dining hall ID set mismatch between API and DB. "
            f"API={sorted(api_ids)} DB={sorted(db_ids)}"
        )

        print(f"[PASS] GET /dining-halls ({len(halls)} halls)")

    async def test_get_dining_hall_detail(self, ctx: TestContext) -> None:
        response = self._request("GET", f"/dining-halls/{ctx.hall_id}")
        assert response.status_code == 200, (
            f"GET /dining-halls/{ctx.hall_id} failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        self._print_payload(f"GET /dining-halls/{ctx.hall_id}", payload)

        assert int(payload["id"]) == ctx.hall_id, "Hall detail id mismatch"
        assert isinstance(payload.get("availableMealTypes"), list), "availableMealTypes should be a list"
        assert isinstance(payload.get("availableDates"), list), "availableDates should be a list"

        db_row = await self._fetch_one(
            """
            SELECT name, external_restaurant_id
            FROM restaurants
            WHERE id = :hall_id
            """,
            {"hall_id": ctx.hall_id},
        )
        assert db_row is not None, "Hall not found in DB during detail check"
        assert payload["name"] == db_row[0], "Hall name mismatch"
        assert int(payload["externalRestaurantId"]) == int(db_row[1]), "externalRestaurantId mismatch"

        print(f"[PASS] GET /dining-halls/{ctx.hall_id}")

    async def test_get_stations(self, ctx: TestContext) -> None:
        params = {"date": ctx.target_date.isoformat()}
        if ctx.meal_type:
            params["mealType"] = ctx.meal_type

        response = self._request("GET", f"/dining-halls/{ctx.hall_id}/stations", params=params)
        assert response.status_code == 200, (
            f"GET /dining-halls/{ctx.hall_id}/stations failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        self._print_payload(f"GET /dining-halls/{ctx.hall_id}/stations", payload)

        assert int(payload["hallId"]) == ctx.hall_id, "Stations hallId mismatch"
        assert payload["date"] == ctx.target_date.isoformat(), "Stations date mismatch"
        assert isinstance(payload.get("stations"), list), "stations should be a list"

        db_sql = """
            SELECT
                msi.station_name,
                COUNT(msi.id) AS item_count
            FROM menu_snapshots ms
            JOIN meal_types mt ON mt.id = ms.meal_type_id
            JOIN menu_sections sec ON sec.snapshot_id = ms.id
            JOIN menu_section_items msi ON msi.section_id = sec.id
            WHERE ms.restaurant_id = :hall_id
              AND ms.service_date = :service_date
              AND msi.food_id IS NOT NULL
              AND msi.station_name IS NOT NULL
        """
        db_params: dict[str, object] = {
            "hall_id": ctx.hall_id,
            "service_date": ctx.target_date,
        }
        if ctx.meal_type:
            db_sql += " AND mt.name = :meal_type"
            db_params["meal_type"] = ctx.meal_type

        db_sql += " GROUP BY msi.station_name ORDER BY msi.station_name"

        db_rows = await self._fetch_all(db_sql, db_params)
        db_counts = {str(row[0]): int(row[1]) for row in db_rows}
        api_counts = {str(item["station"]): int(item["itemCount"]) for item in payload["stations"]}

        assert api_counts == db_counts, (
            "Station item counts mismatch between API and DB. "
            f"API={api_counts} DB={db_counts}"
        )

        print(f"[PASS] GET /dining-halls/{ctx.hall_id}/stations ({len(payload['stations'])} stations)")

    async def test_get_menus(self, ctx: TestContext) -> None:
        params = {"date": ctx.target_date.isoformat()}
        if ctx.meal_type:
            params["mealType"] = ctx.meal_type

        response = self._request("GET", f"/dining-halls/{ctx.hall_id}/menus", params=params)
        assert response.status_code == 200, (
            f"GET /dining-halls/{ctx.hall_id}/menus failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        self._print_payload(f"GET /dining-halls/{ctx.hall_id}/menus", payload)

        assert int(payload["hallId"]) == ctx.hall_id, "Menus hallId mismatch"
        assert payload["date"] == ctx.target_date.isoformat(), "Menus date mismatch"
        assert isinstance(payload.get("stationMenus"), list), "stationMenus should be a list"

        db_sql = """
            SELECT DISTINCT f.id
            FROM menu_snapshots ms
            JOIN meal_types mt ON mt.id = ms.meal_type_id
            JOIN menu_sections sec ON sec.snapshot_id = ms.id
            JOIN menu_section_items msi ON msi.section_id = sec.id
            JOIN foods f ON f.id = msi.food_id
            WHERE ms.restaurant_id = :hall_id
              AND ms.service_date = :service_date
        """
        db_params: dict[str, object] = {
            "hall_id": ctx.hall_id,
            "service_date": ctx.target_date,
        }
        if ctx.meal_type:
            db_sql += " AND mt.name = :meal_type"
            db_params["meal_type"] = ctx.meal_type

        db_rows = await self._fetch_all(db_sql, db_params)
        valid_food_ids = {int(row[0]) for row in db_rows}

        api_item_count = 0
        for station_group in payload["stationMenus"]:
            assert "station" in station_group, "Station group missing station"
            assert isinstance(station_group.get("items"), list), "Station group items should be a list"
            for item in station_group["items"]:
                api_item_count += 1
                assert int(item["id"]) in valid_food_ids, (
                    f"Menu item id={item['id']} not found in DB for hall={ctx.hall_id} date={ctx.target_date}"
                )

        print(
            f"[PASS] GET /dining-halls/{ctx.hall_id}/menus "
            f"({len(payload['stationMenus'])} station groups, {api_item_count} items)"
        )

    async def test_get_menus_with_meal_alias(self, ctx: TestContext) -> None:
        if not ctx.meal_type:
            print("[SKIP] GET /dining-halls/{hall_id}/menus?meal=... — no meal type resolved for context")
            return

        response = self._request(
            "GET",
            f"/dining-halls/{ctx.hall_id}/menus",
            params={
                "date": ctx.target_date.isoformat(),
                "meal": ctx.meal_type,
            },
        )
        assert response.status_code == 200, (
            f"GET /dining-halls/{ctx.hall_id}/menus?meal failed: {response.status_code} {response.text}"
        )

        payload = response.json()
        self._print_payload(f"GET /dining-halls/{ctx.hall_id}/menus?meal=...", payload)

        assert payload.get("mealType") == ctx.meal_type, (
            f"Expected mealType={ctx.meal_type} in response, got {payload.get('mealType')}"
        )

        print(f"[PASS] GET /dining-halls/{ctx.hall_id}/menus with meal alias")

    async def test_get_dining_halls_full(self, ctx: TestContext) -> None:
        response = self._request(
            "GET",
            "/dining-halls/full",
            params={
                "date": ctx.target_date.isoformat(),
                "user_id": str(ctx.user_id),
            },
        )
        assert response.status_code == 200, f"GET /dining-halls/full failed: {response.status_code} {response.text}"

        payload = response.json()
        self._print_payload("GET /dining-halls/full", payload)

        halls = payload.get("diningHalls")
        assert isinstance(halls, list), "diningHalls should be a list in full response"

        matching = [h for h in halls if h.get("name") == ctx.hall_name]
        assert matching, f"Hall '{ctx.hall_name}' not found in /dining-halls/full response"
        hall = matching[0]

        assert "days" in hall and isinstance(hall["days"], dict), "Full hall response missing days map"
        day_key = ctx.target_date.isoformat()
        assert day_key in hall["days"], f"Full response missing date key {day_key} in hall days"

        day = hall["days"][day_key]
        assert "menus" in day and isinstance(day["menus"], dict), "Full day response missing menus map"
        for meal_key in ["breakfast", "lunch", "dinner"]:
            assert meal_key in day["menus"], f"Missing meal bucket '{meal_key}' in full response"
            meal_obj = day["menus"][meal_key]
            assert isinstance(meal_obj.get("count"), int), f"menus.{meal_key}.count should be int"
            assert isinstance(meal_obj.get("categories"), list), f"menus.{meal_key}.categories should be list"
            for category in meal_obj["categories"]:
                assert "category" in category, "Category item missing category name"
                assert isinstance(category.get("items"), list), "Category items should be a list"
                for item in category["items"]:
                    assert isinstance(item.get("favorited"), bool), "favorited flag should be boolean"

        print(f"[PASS] GET /dining-halls/full ({len(halls)} halls)")


async def run_tests(args: argparse.Namespace) -> int:
    tester = DiningHallApiTester(
        base_url=args.base_url,
        timeout=args.timeout,
        max_response_chars=args.max_response_chars,
    )
    try:
        tester.ensure_local_server()
        context = await tester.resolve_context(
            args.user_id,
            args.hall_id,
            args.date,
            args.meal_type,
        )
        print(
            "Running dining hall integration checks with "
            f"user_id={context.user_id} hall_id={context.hall_id} hall_name='{context.hall_name}' "
            f"date={context.target_date} mealType={context.meal_type}"
        )

        await tester.test_list_dining_halls()
        await tester.test_get_dining_hall_detail(context)
        await tester.test_get_stations(context)
        await tester.test_get_menus(context)
        await tester.test_get_menus_with_meal_alias(context)
        await tester.test_get_dining_halls_full(context)

        print("\nAll dining hall API integration checks passed.")
        return 0
    except (AssertionError, RuntimeError, ValueError) as exc:
        print(f"\n[FAIL] {exc}")
        return 1
    finally:
        tester.stop_local_server()
        await tester.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dining Hall API integration tester")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of running FastAPI app (default: %(default)s)",
    )
    parser.add_argument(
        "--user-id",
        default=None,
        help="User UUID for /dining-halls/full favorite flag checks. If omitted, first user in DB is used.",
    )
    parser.add_argument(
        "--hall-id",
        type=int,
        default=None,
        help="Dining hall ID to test. If omitted, one hall with data on selected date is chosen.",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Service date YYYY-MM-DD. If omitted, latest available menu date is used.",
    )
    parser.add_argument(
        "--meal-type",
        default=None,
        help="Meal type (Breakfast/Lunch/Dinner). If omitted, one available for hall/date is selected.",
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
