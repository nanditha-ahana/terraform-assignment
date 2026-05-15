from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.AUTH_SERVICE_URL}/api/v1/auth/login")


def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub") or ""
        token_type: str = payload.get("type") or ""
        if user_id is None or token_type != "access":
            raise credentials_exception
    except ValueError:
        raise credentials_exception
    return payload


def get_current_user_id(payload: dict = Depends(get_current_user_payload)) -> int:
    return int(payload["sub"])


def require_admin(payload: dict = Depends(get_current_user_payload)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return payload


def require_manager_or_admin(payload: dict = Depends(get_current_user_payload)):
    if payload.get("role") not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or admin access required")
    return payload