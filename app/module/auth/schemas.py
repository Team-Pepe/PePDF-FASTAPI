from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserInfo(BaseModel):
    """User information returned in responses"""

    id: str
    username: str
    email: str


class LoginRequest(BaseModel):
    """Login request body"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response with user info"""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: UserInfo


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str


class TokenData(BaseModel):
    """Token claims data"""

    sub: str  # email
    type: str = "access"
