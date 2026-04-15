import time
import uuid

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

bearer_optional = HTTPBearer(auto_error=False)

_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0
_JWKS_TTL_SECONDS = 3600  # re-fetch signing keys every hour

# Shown when no Supabase access token is present (mobile often misconfigures fetch headers).
UNAUTH_DETAIL = (
    "Not authenticated. Send Authorization: Bearer <access_token> using the Supabase session "
    "access_token, or set header X-Supabase-Access-Token to the same value."
)


def _access_token_from_request(
    credentials: HTTPAuthorizationCredentials | None,
    x_supabase_access_token: str | None,
) -> str | None:
    if credentials is not None and credentials.credentials:
        t = credentials.credentials.strip()
        if t:
            return t
    if x_supabase_access_token:
        t = x_supabase_access_token.strip()
        if t:
            return t
    return None


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
    issuer = settings.supabase_issuer
    if not issuer:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_ISSUER or SUPABASE_URL must be configured",
        )

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
            issuer=issuer,
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


async def _payload_from_access_token(token: str) -> dict:
    try:
        jwks = await _get_jwks()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch signing keys",
        )
    return _decode_supabase_token(token, jwks)


async def _payload_from_credentials(credentials: HTTPAuthorizationCredentials) -> dict:
    return await _payload_from_access_token(credentials.credentials)


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
    x_supabase_access_token: str | None = Header(None, alias="X-Supabase-Access-Token"),
) -> dict:
    token = _access_token_from_request(credentials, x_supabase_access_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTH_DETAIL,
        )
    return await _payload_from_access_token(token)


async def get_current_user_id(
    payload: dict = Depends(get_current_user_payload),
) -> uuid.UUID:
    return _sub_uuid_from_payload(payload)


async def get_raw_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
    x_supabase_access_token: str | None = Header(None, alias="X-Supabase-Access-Token"),
) -> str:
    token = _access_token_from_request(credentials, x_supabase_access_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTH_DETAIL,
        )
    return token


async def get_user_id_jwt_or_dev_query(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
    x_supabase_access_token: str | None = Header(None, alias="X-Supabase-Access-Token"),
) -> uuid.UUID:
    """JWT (preferred) or, when ALLOW_QUERY_USER_ID is True, ?user_id= for local tests only."""
    token = _access_token_from_request(credentials, x_supabase_access_token)
    if token:
        payload = await _payload_from_access_token(token)
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
        detail=UNAUTH_DETAIL,
    )


async def get_optional_user_id_jwt_or_dev_query(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_optional),
    x_supabase_access_token: str | None = Header(None, alias="X-Supabase-Access-Token"),
) -> uuid.UUID | None:
    """Optional identity for public feeds (e.g. likedByMe) via JWT or dev query."""
    token = _access_token_from_request(credentials, x_supabase_access_token)
    if token:
        payload = await _payload_from_access_token(token)
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
