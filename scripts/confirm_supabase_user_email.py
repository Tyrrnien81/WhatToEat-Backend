#!/usr/bin/env python3
"""Confirm a user's email via Supabase Auth Admin API (dev/support only).

Uses the same `.env` keys as the FastAPI app: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
(see `.env.example`). Does not import `app.config` so it still runs if `DATABASE_URL` is
unset (only Supabase vars are required).

Run from repo root:

  cd WhatToEat-Backend
  python scripts/confirm_supabase_user_email.py --user-id <uuid>
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_env() -> None:
    """Load `WhatToEat-Backend/.env` the same way as `scripts/ingest_json.py`."""
    load_dotenv(PROJECT_ROOT / ".env")


def main() -> int:
    os.chdir(PROJECT_ROOT)
    _load_env()

    parser = argparse.ArgumentParser(
        description=(
            "Confirm a user's email (Supabase Admin API). "
            "Needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env. "
            "Example: python scripts/confirm_supabase_user_email.py --user-id <uuid>"
        ),
    )
    parser.add_argument(
        "--user-id",
        required=True,
        help="auth.users id (UUID)",
    )
    args = parser.parse_args()

    try:
        uuid.UUID(args.user_id)
    except ValueError:
        print("--user-id must be a valid UUID", file=sys.stderr)
        return 1

    base = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not base or not key:
        print(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env (see .env.example).",
            file=sys.stderr,
        )
        return 1

    url = f"{base}/auth/v1/admin/users/{args.user_id}"
    with httpx.Client(timeout=30.0) as client:
        r = client.put(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "apikey": key,
                "Content-Type": "application/json",
            },
            json={"email_confirm": True},
        )
    print(r.status_code, r.text)
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
