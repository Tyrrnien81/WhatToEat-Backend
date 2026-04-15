#!/usr/bin/env python3
"""
1) Ensure `profiles` has columns expected by the app (e.g. avatar_url).
2) Ensure `user_preferences` has `favorite_dining_halls` (homescreen reads this via ORM).
3) Insert dev row into `public.users` for the default Expo UUID (community / FKs).
4) Insert into `profiles` only when Supabase `auth.users` already has that id (profiles
   often FK to auth.users).

Run from backend root:

  cd WhatToEat-Backend
  source .venv/bin/activate
  python scripts/sync_schema_and_seed_dev_user.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS profiles (
        id UUID PRIMARY KEY,
        email VARCHAR(255),
        name VARCHAR(255),
        avatar_url VARCHAR(500),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'avatar_url'
      ) THEN
        ALTER TABLE profiles ADD COLUMN avatar_url VARCHAR(500);
      END IF;
    END $$
    """,
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'email'
      ) THEN
        ALTER TABLE profiles ADD COLUMN email VARCHAR(255);
      END IF;
    END $$
    """,
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'name'
      ) THEN
        ALTER TABLE profiles ADD COLUMN name VARCHAR(255);
      END IF;
    END $$
    """,
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'created_at'
      ) THEN
        ALTER TABLE profiles ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
      END IF;
    END $$
    """,
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'updated_at'
      ) THEN
        ALTER TABLE profiles ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
      END IF;
    END $$
    """,
    """
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'user_preferences'
          AND column_name = 'favorite_dining_halls'
      ) THEN
        ALTER TABLE user_preferences ADD COLUMN favorite_dining_halls JSONB DEFAULT '[]'::jsonb;
      END IF;
    END $$
    """,
]


async def main() -> None:
    os.chdir(PROJECT_ROOT)

    from sqlalchemy import text

    from app.database import engine

    dev_id = uuid.UUID(
        os.environ.get("DEV_USER_ID", "2a63f492-8875-4d3c-9b72-e262c3293219")
    )
    email = f"dev-{dev_id}@whattoeat.local"
    name = "WhatToEat Dev User"

    async with engine.begin() as conn:
        for stmt in STATEMENTS:
            await conn.execute(text(stmt.strip()))

        await conn.execute(
            text(
                """
                INSERT INTO users (id, email, name)
                VALUES (:uid, :email, :name)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"uid": dev_id, "email": email, "name": name},
        )

        row = (
            await conn.execute(
                text(
                    """
                    SELECT EXISTS (
                      SELECT 1 FROM auth.users WHERE id = CAST(:uid AS uuid)
                    )
                    """
                ),
                {"uid": str(dev_id)},
            )
        ).one()
        auth_has_user = bool(row[0])

        if auth_has_user:
            await conn.execute(
                text(
                    """
                    INSERT INTO profiles (id, email, name)
                    VALUES (:uid, :email, :name)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {"uid": dev_id, "email": email, "name": name},
            )
            print(f"profiles: inserted or skipped for {dev_id} (auth.users present).")
        else:
            print(
                "profiles: skipped — no row in auth.users for this id. "
                "Create a Supabase Auth user with this UUID (Dashboard or Admin API), "
                "then re-run this script to insert profiles."
            )

    await engine.dispose()
    print(
        f"OK — public.users seeded for {dev_id} (if absent); "
        "profiles + user_preferences columns checked."
    )


if __name__ == "__main__":
    asyncio.run(main())
