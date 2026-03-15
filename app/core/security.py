from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(plain: str) -> str:
    """Hash a plain text password using bcrypt."""
    # bcrypt has a 72-byte limit
    password_bytes = plain.encode('utf-8')[:72]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain text password against a hashed password."""
    # bcrypt has a 72-byte limit
    password_bytes = plain.encode('utf-8')[:72]
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": expire,
        "type": "access",
    })
    
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
    })
    
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        raise


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """Verify a token and check its type."""
    payload = decode_token(token)
    
    if payload.get("type") != token_type:
        raise ValueError(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
    
    return payload
