from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth, homescreen


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="WhatToEat API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(homescreen.router)


@app.get("/")
async def root():
    return {"message": "WhatToEat API is running"}
