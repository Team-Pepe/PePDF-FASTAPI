from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.module.auth.schemas import LoginRequest, TokenResponse, RefreshTokenRequest
from app.module.auth.services import authenticate_user, create_tokens, verify_refresh_token
from app.core.security import create_cookie_response, create_logout_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    User login endpoint.
    Returns tokens in HttpOnly cookies.
    
    Args:
        credentials: LoginRequest with email and password
        db: Database session
    
    Returns:
        Response with Set-Cookie headers for access and refresh tokens
    
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
    
    # Get tokens
    token_response = await create_tokens(user)
    
    # Return response with cookies
    return create_cookie_response(
        access_token=token_response.access_token,
        refresh_token=token_response.refresh_token,
        user_data={
            "id": token_response.user.id,
            "email": token_response.user.email,
            "username": token_response.user.username,
        },
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Refresh access token using refresh token.
    Returns new tokens in HttpOnly cookies.
    
    Args:
        request: RefreshTokenRequest with refresh_token
        db: Database session
    
    Returns:
        Response with Set-Cookie headers for new tokens
    
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
    
    # Get new tokens
    token_response = await create_tokens(user)
    
    # Return response with cookies
    return create_cookie_response(
        access_token=token_response.access_token,
        refresh_token=token_response.refresh_token,
        user_data={
            "id": token_response.user.id,
            "email": token_response.user.email,
            "username": token_response.user.username,
        },
    )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current user from dependencies
    
    Returns:
        User information
    """
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    User logout endpoint.
    Clears authentication cookies.
    
    Returns:
        Response with cleared cookies
    """
    return create_logout_response()
