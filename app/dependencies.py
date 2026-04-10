import time
import uuid

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

security = HTTPBearer()
bearer_optional = HTTPBearer(auto_error=False)

_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0
_JWKS_TTL_SECONDS = 3600  # re-fetch signing keys every hour


async def _get_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at

    now = time.monotonic()
    if _jwks_cache is not None and (now - _jwks_fetched_at) < _JWKS_TTL_SECONDS:
        return _jwks_cache

    if not settings.SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL is not configured")

    jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url, timeout=10)
        response.raise_for_status()

    _jwks_cache = response.json()
    _jwks_fetched_at = now
    return _jwks_cache


def _decode_supabase_token(token: str, jwks: dict) -> dict:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )

    kid = header.get("kid")
    alg = header.get("alg")
    if not kid or not alg:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )

    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signing key not found",
        )

    try:
        return jwt.decode(
            token,
            key,
            algorithms=[alg],
            issuer=settings.SUPABASE_ISSUER,
            options={"verify_aud": False},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def _sub_uuid_from_payload(payload: dict) -> uuid.UUID:
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        return uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )


async def _payload_from_credentials(credentials: HTTPAuthorizationCredentials) -> dict:
    try:
        jwks = await _get_jwks()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch signing keys",
        )
    return _decode_supabase_token(credentials.credentials, jwks)


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    return await _payload_from_credentials(credentials)


async def get_current_user_id(
    payload: dict = Depends(get_current_user_payload),
) -> uuid.UUID:
    return _sub_uuid_from_payload(payload)


async def get_user_id_jwt_or_dev_query(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
) -> uuid.UUID:
    """JWT (preferred) or, when ALLOW_QUERY_USER_ID is True, ?user_id= for local tests only."""
    if credentials is not None:
        payload = await _payload_from_credentials(credentials)
        return _sub_uuid_from_payload(payload)

    if settings.ALLOW_QUERY_USER_ID:
        raw = request.query_params.get("user_id")
        if raw:
            try:
                return uuid.UUID(raw)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_id",
                )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def get_optional_user_id_jwt_or_dev_query(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
) -> uuid.UUID | None:
    """Optional identity for public feeds (e.g. likedByMe) via JWT or dev query."""
    if credentials is not None:
        payload = await _payload_from_credentials(credentials)
        return _sub_uuid_from_payload(payload)

    if settings.ALLOW_QUERY_USER_ID:
        raw = request.query_params.get("user_id")
        if raw:
            try:
                return uuid.UUID(raw)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_id",
                )

    return None
