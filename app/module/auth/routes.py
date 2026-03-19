from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.module.auth.schemas import LoginRequest, TokenResponse, RefreshTokenRequest
from app.module.auth.services import authenticate_user, create_tokens, verify_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    User login endpoint.
    
    Args:
        credentials: LoginRequest with email and password
        db: Database session
    
    Returns:
        TokenResponse with access_token, refresh_token, and user info
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = await authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await create_tokens(user)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        request: RefreshTokenRequest with refresh_token
        db: Database session
    
    Returns:
        TokenResponse with new access_token, refresh_token, and user info
    
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    user = await verify_refresh_token(db, request.refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await create_tokens(user)
