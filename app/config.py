import os
from pydantic import BaseModel


class Settings(BaseModel):
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    SUPABASE_URL: str = os.environ["SUPABASE_URL"]
    SUPABASE_ISSUER: str = os.environ["SUPABASE_ISSUER"]
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")


settings = Settings()