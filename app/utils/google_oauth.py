from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from app.config import settings


def verify_google_token(token: str):
    try:
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        if info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Invalid issuer")

        return {
            "email": info.get("email"),
            "name": info.get("name"),
            "sub": info.get("sub"),
            "email_verified": info.get("email_verified", False),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")