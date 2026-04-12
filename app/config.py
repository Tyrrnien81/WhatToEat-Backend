from pydantic import field_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import make_url


class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_URL: str = ""
    SUPABASE_ISSUER: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    # When True, personalized routes (homescreen, community writes, scan) accept
    # ?user_id=<uuid> if Authorization is absent. Never enable in production.
    ALLOW_QUERY_USER_ID: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def database_url_must_be_usable(cls, v: object) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("DATABASE_URL is required (set it in .env).")
        s = str(v).strip()
        try:
            url = make_url(s)
        except Exception as exc:
            raise ValueError(f"DATABASE_URL is not a valid database URL: {exc}") from exc
        if not url.host:
            raise ValueError(
                "DATABASE_URL is missing a hostname after @. Check .env for a typo, stray "
                "line breaks, or a truncated copy from Supabase / your provider."
            )
        return s


settings = Settings()
