from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.dependencies import get_db
from app.services.user_service import UserService
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


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
