from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.models.tokens import RefreshToken
from app.schemas.auth_schema import UserRegisterRequest
from app.schemas.token import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegisterRequest) -> User:
        # Check duplicate email / username
        result = await self.db.execute(
            select(User).where(
                or_(User.email == data.email, User.username == data.username)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            field = "Email" if str(existing.email) == str(data.email) else "Username"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{field} already registered",
            )

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, username_or_email: str, password: str) -> User:
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == username_or_email,
                    User.email == username_or_email,
                )
            )
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, str(user.hashed_password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is disabled",
            )
        return user

    async def create_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"username": user.username},
        )
        refresh_token_str = create_refresh_token(subject=user.id)

        # Persist refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        await self.db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse:
        # Validate the refresh token
        try:
            payload = decode_token(refresh_token_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Check DB record
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        )
        db_token = result.scalar_one_or_none()
        if not db_token or db_token.is_revoked is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked or not found",
            )

        # Revoke old token (rotation)
        setattr(db_token, "is_revoked", True)
        await self.db.flush()

        user = await self.get_user_by_id(int(payload["sub"]))
        if not user or user.is_active is False:
            raise HTTPException(status_code=400, detail="User not found or inactive")

        return await self.create_tokens(user)

    async def revoke_token(self, refresh_token_str: str) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        )
        db_token = result.scalar_one_or_none()
        if db_token:
            setattr(db_token, "is_revoked", True)
            await self.db.flush()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, str(user.hashed_password)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        setattr(user, "hashed_password", get_password_hash(new_password))
        await self.db.flush()

    def verify_token(self, token: str) -> dict:
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return {"valid": False}
            return {
                "valid": True,
                "user_id": int(payload["sub"]),
                "username": payload.get("username"),
                "role": payload.get("role"),
            }
        except ValueError:
            return {"valid": False}