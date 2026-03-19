from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.config import settings
from app.models import User
from app.module.auth.repositories import get_user_by_email
from app.module.auth.schemas import TokenResponse, UserInfo
from jose import JWTError


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Authenticate user with email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
    
    Returns:
        User object if credentials are valid, None otherwise
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def create_tokens(user: User) -> TokenResponse:
    """
    Create access and refresh tokens for user.
    
    Args:
        user: User object
    
    Returns:
        TokenResponse with tokens and user info
    """
    # Create access token with indefinite expiration
    access_token = create_access_token(
        data={"sub": user.email},
        expires_in=settings.access_token_expire_days,
    )
    
    # Create refresh token with default expiration
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_in=settings.refresh_token_expire_days,
    )
    
    user_info = UserInfo(
        id=str(user.id),
        username=user.username,
        email=user.email,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        user=user_info,
    )


async def verify_refresh_token(db: AsyncSession, refresh_token: str) -> User | None:
    """
    Verify refresh token and return associated user.
    
    Args:
        db: Database session
        refresh_token: JWT refresh token
    
    Returns:
        User object if refresh token is valid, None otherwise
    """
    try:
        payload = decode_token(refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            return None
        
        email: str = payload.get("sub")
        if email is None:
            return None
        
        user = await get_user_by_email(db, email)
        return user if user and user.is_active else None
    except JWTError:
        return None
