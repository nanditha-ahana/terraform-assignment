from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: str = "user"
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class UserCreateRequest(UserBase):
    """Used internally or by admin to create users."""
    pass




class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class UserAdminUpdateRequest(UserUpdateRequest):
    user_id: int
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UserResponse]

    model_config = {"from_attributes": True}