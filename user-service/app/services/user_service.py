from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest, UserAdminUpdateRequest, UserListResponse


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> UserListResponse:
        query = select(User)
        count_query = select(func.count()).select_from(User)

        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(User.id)
        result = await self.db.execute(query)
        users = result.scalars().all()

        return UserListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[UserResponse.model_validate(user) for user in users]
        )

    async def create_user(self, data: UserCreateRequest) -> User:
        # Check uniqueness
        existing_email = await self.get_user_by_email(data.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        existing_username = await self.get_user_by_username(data.username)
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")

        user = User(**data.model_dump())
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user(
        self,
        user_id: int,
        data: UserUpdateRequest
    ) -> User:
        user = await self.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id {user_id}"
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)

        return user
    
    
    async def admin_update_user(self, user_id: int, data: UserAdminUpdateRequest) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found with id {user_id}")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found with id {user_id}")
        await self.db.delete(user)
        await self.db.flush()

    async def deactivate_user(self, user_id: int) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        setattr(user, "is_active", False)
        await self.db.flush()
        await self.db.refresh(user)
        return user