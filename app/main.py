from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, community, dining_hall, homescreen, profile, questionnaire, scan

@asynccontextmanager
async def lifespan(app: FastAPI):
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
