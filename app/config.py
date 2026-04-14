from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # Dev-only: allow ?user_id= when JWT is omitted (never enable in production).
    ALLOW_QUERY_USER_ID: bool = False

    SUPABASE_URL: Optional[str] = None
    SUPABASE_ISSUER: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
