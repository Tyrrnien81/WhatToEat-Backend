from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.routers import community, homescreen, dining_hall, profile, scan


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="WhatToEat API", version="0.1.0", lifespan=lifespan)

app.include_router(homescreen.router)
app.include_router(dining_hall.router)
app.include_router(community.router)
app.include_router(profile.router)
app.include_router(scan.router)


@app.get("/")
async def root():
    return {"message": "WhatToEat API is running"}
