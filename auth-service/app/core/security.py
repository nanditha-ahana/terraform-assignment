from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Modern password hashing
password_hash = PasswordHash.recommended()


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def get_password_hash(password: str) -> str:

    # Optional safety validation
    if len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Password must be less than 72 bytes"
        )

    return password_hash.hash(password)


def create_access_token(
    subject: str | Any,
    extra_claims: dict | None = None,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(
    subject: str | Any,
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_token(token: str) -> dict:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload

    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token"
        ) from exc