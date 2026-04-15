#!/usr/bin/env python3
"""
Final review: exercise every route, assert status codes and JSON shapes, and verify auth.

Uses FastAPI TestClient (in-process; no separate server):

  cd WhatToEat-Backend && python scripts/review_all_endpoints.py

When ALLOW_QUERY_USER_ID=true, a user id is read from `profiles` / `users` for ?user_id= tests.
Override with WTE_TEST_USER_ID or --user-id.

Set WTE_ACCESS_TOKEN to a real Supabase access_token to also run Bearer /auth/me.

Exit 0 = all checks passed.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.chdir(PROJECT_ROOT)

_MIN_PNG = bytes(
    [
        0x89,
        0x50,
        0x4E,
        0x47,
        0x0D,
        0x0A,
        0x1A,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x0D,
        0x49,
        0x48,
        0x44,
        0x52,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x01,
        0x08,
        0x06,
        0x00,
        0x00,
        0x00,
        0x1F,
        0x15,
        0xC4,
        0x89,
        0x00,
        0x00,
        0x00,
        0x0A,
        0x49,
        0x44,
        0x41,
        0x54,
        0x78,
        0x9C,
        0x63,
        0x00,
        0x01,
        0x00,
        0x00,
        0x05,
        0x00,
        0x01,
        0x0D,
        0x0A,
        0x2D,
        0xDB,
        0x00,
        0x00,
        0x00,
        0x00,
        0x49,
        0x45,
        0x4E,
        0x44,
        0xAE,
        0x42,
        0x60,
        0x82,
    ]
)


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def _ok(msg: str) -> None:
    print(f"OK   {msg}")


async def _pick_test_user_id() -> uuid.UUID | None:
    """Prefer `users` (required by scan/meal log); fall back to `profiles`."""
    from sqlalchemy import select

    from app.database import async_session
    from app.models.user import Profile, User

    async with async_session() as session:
        r = await session.execute(select(User.id).limit(1))
        uid = r.scalar_one_or_none()
        if uid:
            return uid
        r2 = await session.execute(select(Profile.id).limit(1))
        return r2.scalar_one_or_none()


class ReviewRunner:
    def __init__(self, user_id: uuid.UUID | None, bearer: str | None):
        self.user_id = user_id
        self.bearer = bearer
        from app.config import settings

        self.settings = settings
        self.allow_query = settings.ALLOW_QUERY_USER_ID

    def _q(self, path: str) -> str:
        if self.user_id and self.allow_query:
            sep = "&" if "?" in path else "?"
            return f"{path}{sep}user_id={self.user_id}"
        return path

    def run(self, client: TestClient) -> int:
        f = 0
        f += self._public(client)
        f += self._auth_unauthorized(client)
        if self.user_id and self.allow_query:
            f += self._protected_with_query(client)
        if self.bearer:
            f += self._protected_with_bearer(client)
        return f

    def _expect(
        self,
        client: TestClient,
        method: str,
        path: str,
        *,
        status: int = 200,
        json_keys: set[str] | None = None,
        headers: dict[str, str] | None = None,
        json_body: dict | None = None,
        files: Any = None,
    ) -> int:
        try:
            if files is not None:
                r = client.request(method, path, headers=headers or {}, files=files)
            elif json_body is not None:
                r = client.request(method, path, headers=headers or {}, json=json_body)
            else:
                r = client.request(method, path, headers=headers or {})
        except Exception as e:
            _fail(f"{method} {path} — {e}")
            return 1
        if r.status_code != status:
            _fail(f"{method} {path} — expected {status}, got {r.status_code}: {r.text[:400]}")
            return 1
        ct = r.headers.get("content-type", "")
        if json_keys is not None and "application/json" in ct:
            data = r.json()
            missing = json_keys - set(data.keys())
            if missing:
                _fail(f"{method} {path} — missing keys {missing} in {list(data.keys())}")
                return 1
        _ok(f"{method} {path} → {status}")
        return 0

    def _public(self, client: TestClient) -> int:
        f = 0
        f += self._expect(client, "GET", "/", json_keys={"message"})
        r = client.get("/health/db")
        if r.status_code not in (200, 503):
            _fail(f"GET /health/db unexpected {r.status_code}")
            f += 1
        elif "ok" not in r.json():
            _fail("GET /health/db missing ok")
            f += 1
        else:
            _ok(f"GET /health/db → {r.status_code}")

        f += self._expect(client, "GET", "/dining-halls", json_keys={"diningHalls"})
        halls = client.get("/dining-halls").json().get("diningHalls") or []
        hall_id = halls[0]["id"] if halls else 1

        f += self._expect(
            client,
            "GET",
            f"/dining-halls/{hall_id}",
            json_keys={"id", "name", "externalRestaurantId", "availableMealTypes", "availableDates"},
        )
        f += self._expect(
            client,
            "GET",
            f"/dining-halls/{hall_id}/stations",
            json_keys={"hallId", "date", "mealType", "stations"},
        )
        f += self._expect(
            client,
            "GET",
            f"/dining-halls/{hall_id}/menus",
            json_keys={"hallId", "hallName", "date", "mealType", "stationMenus"},
        )
        f += self._expect(client, "GET", "/dining-halls/full", json_keys={"diningHalls"})
        f += self._expect(
            client,
            "GET",
            "/community/posts",
            json_keys={"page", "limit", "hasMore", "posts"},
        )
        rid = str(uuid.uuid4())
        rd = client.get(f"/community/posts/{rid}")
        if rd.status_code not in (404, 200):
            _fail(f"GET /community/posts/{{id}} → {rd.status_code}")
            f += 1
        else:
            _ok(f"GET /community/posts/{{uuid}} → {rd.status_code}")
        return f

    def _auth_unauthorized(self, client: TestClient) -> int:
        f = 0
        paths = [
            ("GET", "/auth/me"),
            ("POST", "/auth/profile"),
            ("POST", "/auth/logout"),
            ("GET", "/recommendations/combo"),
            ("GET", "/goals/daily"),
            ("GET", "/menus/summary"),
            ("GET", "/recommendations/addons"),
            ("GET", "/users/me"),
            ("GET", "/users/me/preferences"),
            ("GET", "/users/me/food-log"),
            ("GET", "/users/me/food-log/summary"),
        ]
        for method, path in paths:
            if method == "GET":
                r = client.get(path)
            else:
                r = client.post(path, json={"name": "t"})
            if r.status_code != 401:
                _fail(f"{method} {path} without auth — expected 401, got {r.status_code}")
                f += 1
                continue
            det = r.json().get("detail", "")
            if "Not authenticated" not in str(det):
                _fail(f"{method} {path} detail unexpected: {det!r}")
                f += 1
            else:
                _ok(f"{method} {path} without auth → 401")

        if self.settings.SUPABASE_URL:
            r = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
            if r.status_code != 401:
                _fail(f"Invalid Bearer expected 401, got {r.status_code}")
                f += 1
            else:
                _ok("GET /auth/me with invalid Bearer → 401")
        else:
            _ok("Skip invalid-Bearer check (SUPABASE_URL unset)")
        return f

    def _protected_with_query(self, client: TestClient) -> int:
        assert self.user_id is not None
        f = 0
        f += self._expect(client, "GET", self._q("/auth/me"), json_keys={"id"})
        f += self._expect(client, "GET", self._q("/recommendations/combo"), json_keys={"combos"})
        f += self._expect(
            client,
            "GET",
            self._q("/goals/daily"),
            json_keys={"date", "calories", "protein", "carbs", "fat"},
        )
        f += self._expect(
            client,
            "GET",
            self._q("/menus/summary"),
            json_keys={"date", "diningHalls"},
        )
        f += self._expect(
            client,
            "GET",
            self._q("/recommendations/addons"),
            json_keys={"mealType", "suggestions", "quickAddons"},
        )
        f += self._expect(client, "GET", self._q("/users/me"), json_keys={"id"})
        f += self._expect(
            client,
            "GET",
            self._q("/users/me/preferences"),
            json_keys={
                "birthday",
                "gender",
                "height",
                "weight",
                "goal_weight",
                "diet_type",
                "dislikes",
                "allergens",
                "favorite_dining_halls",
                "target_calories",
                "target_protein_g",
                "target_carbs_g",
                "target_fat_g",
            },
        )
        f += self._expect(
            client,
            "GET",
            self._q("/users/me/food-log"),
            json_keys={"entries", "total", "page", "limit"},
        )
        f += self._expect(
            client,
            "GET",
            self._q("/users/me/food-log/summary"),
            json_keys={
                "range",
                "averageDailyCalories",
                "averageDailyProtein",
                "averageDailyCarbs",
                "averageDailyFat",
                "totalMealsLogged",
                "currentStreak",
                "longestStreak",
                "weightHistory",
            },
        )

        r = client.post(self._q("/scan"), files={"image": ("t.png", _MIN_PNG, "image/png")})
        if r.status_code != 200:
            _fail(f"POST /scan → {r.status_code} {r.text[:200]}")
            f += 1
        else:
            js = r.json()
            if not all(k in js for k in ("scanId", "items", "summary")):
                _fail(f"POST /scan bad keys {list(js.keys())}")
                f += 1
            else:
                _ok("POST /scan → 200")
                body = {
                    "scanId": js.get("scanId"),
                    "items": [
                        {"name": "Test", "calories": 1, "protein": 0, "carbs": 0, "fat": 0},
                    ],
                    "mealType": "Lunch",
                    "date": None,
                }
                r2 = client.post(self._q("/scan/log"), json=body)
                if r2.status_code != 201:
                    _fail(f"POST /scan/log → {r2.status_code} {r2.text[:200]}")
                    f += 1
                else:
                    _ok("POST /scan/log → 201")

        body = {
            "date": "2026-01-15",
            "mealType": "Lunch",
            "items": [
                {
                    "foodName": "Review test item",
                    "quantity": 1.0,
                    "calories": 100,
                    "protein": 10,
                    "carbs": 10,
                    "fat": 5,
                    "source": "review",
                }
            ],
        }
        r3 = client.post(self._q("/meals/log"), json=body)
        if r3.status_code != 201:
            _fail(f"POST /meals/log → {r3.status_code} {r3.text[:200]}")
            f += 1
        else:
            d = r3.json()
            if "mealLogId" not in d or "message" not in d:
                _fail(f"POST /meals/log body keys {list(d.keys())}")
                f += 1
            else:
                _ok("POST /meals/log → 201")
        return f

    def _protected_with_bearer(self, client: TestClient) -> int:
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {self.bearer}"})
        if r.status_code != 200:
            _fail(f"Bearer GET /auth/me → {r.status_code} {r.text[:300]}")
            return 1
        _ok("Bearer GET /auth/me → 200")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", default=os.environ.get("WTE_TEST_USER_ID"))
    args = parser.parse_args()

    bearer = os.environ.get("WTE_ACCESS_TOKEN")

    from app.config import settings
    from app.main import app

    print("Settings:")
    print(f"  ALLOW_QUERY_USER_ID={settings.ALLOW_QUERY_USER_ID}")
    print(f"  SUPABASE_URL set: {bool(settings.SUPABASE_URL)}")
    print("  Transport: TestClient (in-process)")

    uid: uuid.UUID | None = None
    if args.user_id:
        uid = uuid.UUID(args.user_id)
        print(f"  Test user id (from args): {uid}")
    elif settings.ALLOW_QUERY_USER_ID:
        uid = asyncio.run(_pick_test_user_id())
        if uid:
            print(f"  Test user id (from DB): {uid}")
        else:
            print(
                "  Note: No row in users/profiles — skipping ?user_id= authenticated tests "
                "(add a user or pass --user-id)",
            )

    runner = ReviewRunner(uid, bearer)

    with TestClient(app) as client:
        failures = runner.run(client)

    if failures:
        print(f"\n{failures} check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll review checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
