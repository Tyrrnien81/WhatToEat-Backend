#!/usr/bin/env python3
"""
Load the same Settings + DB engine as the FastAPI app, then run a trivial SQL check.

Run from the backend folder (so `.env` resolves like the app):

  cd WhatToEat-Backend
  source .venv/bin/activate   # if you use venv
  python scripts/check_db_env.py

Exit code 0 only if settings load and `SELECT 1` succeeds.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _redact_database_url(url: str) -> str:
    """Hide password in postgresql-style URLs for logs."""
    return re.sub(r"(//[^:]+:)[^@]+(@)", r"\1***\2", url, count=1)


async def _check() -> None:
    # Match how uvicorn loads the app: working directory is usually project root.
    os.chdir(PROJECT_ROOT)

    # Import after chdir so pydantic_settings reads `WhatToEat-Backend/.env`.
    from sqlalchemy import text

    from app.config import settings
    from app.database import engine

    print("Working directory:", PROJECT_ROOT)
    env_file = PROJECT_ROOT / ".env"
    print(f".env file present: {env_file.is_file()}")

    db_url = getattr(settings, "DATABASE_URL", "") or ""
    if not db_url.strip():
        print("ERROR: DATABASE_URL is empty — check .env")
        sys.exit(1)

    print("DATABASE_URL (redacted):", _redact_database_url(db_url))
    print("ALLOW_QUERY_USER_ID:", settings.ALLOW_QUERY_USER_ID)
    print("SUPABASE_URL set:", bool(settings.SUPABASE_URL))
    print("SUPABASE_ISSUER set:", bool(settings.SUPABASE_ISSUER))

    async with engine.connect() as conn:
        one = (await conn.execute(text("SELECT 1 AS ok"))).scalar_one()
        if one != 1:
            print("ERROR: unexpected SELECT 1 result:", one)
            sys.exit(1)

        row = (await conn.execute(text("SELECT current_database(), current_user"))).one()
        print("Connected database:", row[0])
        print("Connected user:", row[1])

    print("\nOK — settings loaded and database responded.")


def main() -> None:
    try:
        asyncio.run(_check())
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
