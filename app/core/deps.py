from typing import Annotated, Dict, Any, Optional
from fastapi import Depends, HTTPException, status, Header, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from app.core.database import get_db as _get_db
from app.core.security import decode_token
from app.models import User
from sqlalchemy import select


async def get_db() -> AsyncSession:
    """Get database session"""
    async for session in _get_db():
        yield session


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[Optional[str], Cookie()] = None,
    authorization: Annotated[Optional[str], Header()] = None,
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    Tries to extract token from cookies first, then from Authorization header.
    
    Args:
        access_token: JWT from HttpOnly cookie
        authorization: Authorization header with Bearer token (fallback)
        db: Database session
    
    Returns:
        User information dictionary
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Try to get token from cookie first
    token = access_token
    
    # Fallback: try to extract from Authorization header
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
    }


async def get_optional_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[Optional[str], Header()] = None,
) -> Dict[str, Any] | None:
    """
    Get current user if authenticated, otherwise None.
    
    Args:
        authorization: Optional Authorization header with Bearer token
        db: Database session
    
    Returns:
        User information dictionary or None
    """
    if authorization is None:
        return None
    
    return await get_current_user(authorization, db)
