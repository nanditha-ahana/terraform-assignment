from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    username: str  # can be email or username
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}