from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # Dev-only: allow ?user_id= when JWT is omitted (never enable in production).
    ALLOW_QUERY_USER_ID: bool = False

    SUPABASE_URL: Optional[str] = None
    SUPABASE_ISSUER: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    FRONTEND_URL: Optional[str] = "http://localhost:3000"

    @property
    def supabase_issuer(self) -> Optional[str]:
        """Prefer explicit issuer; fall back to SUPABASE_URL/auth/v1 for safer defaults."""
        if self.SUPABASE_ISSUER:
            return self.SUPABASE_ISSUER.rstrip("/")
        if self.SUPABASE_URL:
            return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1"
        return None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
