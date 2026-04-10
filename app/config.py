from pydantic_settings import BaseSettings


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


settings = Settings()
