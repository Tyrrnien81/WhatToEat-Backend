import os
from pydantic import BaseModel


class Settings(BaseModel):
    DATABASE_URL: str                  = os.getenv("DATABASE_URL", "")

    SECRET_KEY: str                    = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str                     = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int   = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int     = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    GOOGLE_CLIENT_ID: str              = os.getenv("GOOGLE_CLIENT_ID", "")

    SMTP_HOST: str                     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int                     = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str                     = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str                 = os.getenv("SMTP_PASSWORD", "")

    FRONTEND_URL: str                  = os.getenv("FRONTEND_URL", "http://localhost:3000")


settings = Settings()