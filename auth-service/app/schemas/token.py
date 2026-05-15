from typing import Optional

from pydantic import BaseModel


class UserLoginRequest(BaseModel):
    username: str  # can be email or username
    password: str
 
 
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
 
 
class RefreshTokenRequest(BaseModel):
    refresh_token: str
 
 
class TokenVerifyRequest(BaseModel):
    token: str
 
 
class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
 