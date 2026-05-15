from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.dependencies import get_db
from app.schemas.auth_schema import (
    UserRegisterRequest,
    UserResponse
)
from app.schemas.token import (
    RefreshTokenRequest,
    TokenResponse,
    TokenVerifyRequest,
    TokenVerifyResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    user = await service.register(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 compatible login — returns access + refresh tokens."""
    service = AuthService(db)
    user = await service.authenticate(form_data.username, form_data.password)
    return await service.create_tokens(user)



@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Revoke the provided refresh token."""
    service = AuthService(db)
    await service.revoke_token(data.refresh_token)


@router.post("/verify-token", response_model=TokenVerifyResponse)
async def verify_token(data: TokenVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify an access token (used by other services)."""
    service = AuthService(db)
    result = service.verify_token(data.token)
    return TokenVerifyResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_active_user)):
    """Return the currently authenticated user's profile."""
    return current_user
