import logging
import socket
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, community, homescreen, dining_hall, profile, questionnaire, scan

logger = logging.getLogger(__name__)


def _walk_exception_chain(exc: BaseException) -> list[BaseException]:
    out: list[BaseException] = []
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        out.append(current)
        current = current.__cause__
    return out


def _log_database_startup_hint(exc: BaseException) -> None:
    chain = _walk_exception_chain(exc)
    if any(isinstance(e, socket.gaierror) for e in chain):
        logger.error(
            "Database host could not be resolved (DNS). Fix the hostname in DATABASE_URL "
            "inside .env (Supabase: Project Settings → Database → connection string)."
        )
        return
    if any(isinstance(e, ConnectionRefusedError) for e in chain):
        logger.error(
            "Database connection refused. If using localhost, start PostgreSQL or Docker; "
            "otherwise check host/port and firewall."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        _log_database_startup_hint(exc)
        raise
    yield


app = FastAPI(title="WhatToEat API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(homescreen.router)
app.include_router(dining_hall.router)
app.include_router(community.router)
app.include_router(profile.router)
app.include_router(questionnaire.router)
app.include_router(scan.router)


@app.get("/")
async def root():
    return {"message": "WhatToEat API is running"}
