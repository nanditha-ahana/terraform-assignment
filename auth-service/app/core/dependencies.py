from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.dependencies import get_db
from app.services.auth_service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
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
    return user_id


async def get_current_active_user(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

