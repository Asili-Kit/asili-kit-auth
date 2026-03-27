from datetime import UTC, datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = settings.JWT_ALGORITHM


def _create_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode.update({"iat": now, "exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    lifetime = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data=data, token_type="access", expires_delta=lifetime)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    lifetime = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(data=data, token_type="refresh", expires_delta=lifetime)


def _decode_token(token: str, expected_type: Optional[str] = None) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        raise JWTError("Invalid token type")
    return payload


def decode_access_token(token: str) -> dict:
    return _decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, expected_type="refresh")