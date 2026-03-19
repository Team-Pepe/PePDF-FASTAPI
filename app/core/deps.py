from typing import Annotated, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from app.core.database import get_db as _get_db
from app.core.security import decode_token
from app.models import User
from sqlalchemy import select

security = HTTPBearer()


async def get_db() -> AsyncSession:
    """Get database session"""
    async for session in _get_db():
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials (JWT token)
        db: Database session
    
    Returns:
        User information dictionary
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
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
    credentials: Annotated[HTTPAuthCredentials | None, Depends(security)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> Dict[str, Any] | None:
    """
    Get current user if authenticated, otherwise None.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
    
    Returns:
        User information dictionary or None
    """
    if credentials is None:
        return None
    
    return await get_current_user(credentials, db)
