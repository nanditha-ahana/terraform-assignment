from jose import JWTError, jwt
from app.core.config import settings


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")