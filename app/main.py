import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db
from app.routers import auth, community, dining_hall, homescreen, profile, questionnaire, scan

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Apply idempotent DDL so local / older Supabase DBs match the ORM without a manual migration."""
    async with async_session() as session:
        try:
            await session.execute(
                text(
                    """
                    ALTER TABLE user_preferences
                    ADD COLUMN IF NOT EXISTS favorite_dining_halls JSONB DEFAULT '[]'::jsonb
                    """
                )
            )
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.warning("Startup schema check failed (add favorite_dining_halls): %s", exc)
    yield

app = FastAPI(title="WhatToEat API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(homescreen.router)
app.include_router(dining_hall.router)
app.include_router(community.router)
app.include_router(scan.router)
app.include_router(profile.router)
app.include_router(questionnaire.router)

@app.get("/")
async def root():
    return {"message": "WhatToEat API is running"}


@app.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    """Verify `DATABASE_URL` from `.env` — same pool/session as all other routes."""
    try:
        await db.execute(text("SELECT 1"))
        row = (await db.execute(text("SELECT COUNT(*)::int FROM restaurants"))).one()
        n = int(row[0])
        return {"ok": True, "database": "connected", "restaurant_count": n}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "database": "error",
                "detail": str(exc)[:500],
            },
        )
