from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from pydantic import ValidationError

from kepin.core.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_join_code() -> str:
    return secrets.token_hex(8)


def create_token(user_id: str, purpose: str = "access", expires_minutes: int | None = None) -> str:
    settings = get_settings()
    ttl = expires_minutes if expires_minutes is not None else settings.jwt_expire_minutes
    payload = {
        "sub": user_id,
        "purpose": purpose,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ttl),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except (JWTError, ValidationError):
        return None
