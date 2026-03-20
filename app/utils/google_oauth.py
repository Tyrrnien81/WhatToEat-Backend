from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.config import settings


def verify_google_token(token: str) -> dict | None:
    """Verify a Google ID token and return user info (email, name, sub)."""
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return {
            "email": id_info["email"],
            "name": id_info.get("name", ""),
            "google_id": id_info["sub"],
        }
    except ValueError:
        return None
