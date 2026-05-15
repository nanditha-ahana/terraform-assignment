from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserAdminUpdateRequest,
    UserResponse,
    UserListResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),    
    current_user=Depends(get_current_user),
):
    """List all users (admin only)."""
    service = UserService(db)
    return await service.list_users(page=page, page_size=page_size, role=role, is_active=is_active)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    
):
    """Create a user record (admin only — auth service handles registration)."""
    service = UserService(db)
    return await service.create_user(data)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user=Depends(get_current_user)):
    """Get the currently authenticated user's full profile."""
    return current_user


@router.post("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update own profile fields."""
    service = UserService(db)
    return await service.update_user(current_user.id, data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a user by ID (admin only)."""
    service = UserService(db)
    return await service.get_user_by_id(user_id)


@router.post("/update-user", response_model=UserResponse)
async def admin_update_user(
    data: UserAdminUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Admin update: role, active status, verification."""
    service = UserService(db)
    user_id = data.user_id
    return await service.admin_update_user(user_id, data)


@router.post("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Hard delete a user (admin only)."""
    service = UserService(db)
    await service.delete_user(user_id)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-deactivate a user (admin only)."""
    service = UserService(db)
    return await service.deactivate_user(user_id)