from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import JWTError, jwt
import bcrypt
from fastapi.responses import JSONResponse
from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: Dict[str, Any], expires_in: int | None = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Claims to encode in the token
        expires_in: Expiration time in days. If None, token never expires.
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Only add exp if expires_in is specified
    if expires_in is not None:
        expire = datetime.now(timezone.utc) + timedelta(days=expires_in)
        to_encode["exp"] = expire
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_in: int | None = None) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Claims to encode in the token
        expires_in: Expiration time in days. Defaults to settings.refresh_token_expire_days
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    to_encode["type"] = "refresh"
    
    if expires_in is None:
        expires_in = settings.refresh_token_expire_days
    
    expire = datetime.now(timezone.utc) + timedelta(days=expires_in)
    to_encode["exp"] = expire
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token claims
    
    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    return payload


def create_cookie_response(
    access_token: str,
    refresh_token: str,
    user_data: Dict[str, Any],
    secure: bool = False,
) -> JSONResponse:
    """
    Create JSONResponse with JWT tokens in HttpOnly cookies.
    
    Args:
        access_token: JWT access token
        refresh_token: JWT refresh token
        user_data: User info to include in response body
        secure: If True, use Secure flag (HTTPS only). Use True in production.
    
    Returns:
        JSONResponse with Set-Cookie headers for both tokens
    """
    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": user_data,
    }
    
    response = JSONResponse(content=response_data, status_code=200)
    
    # Set access token cookie - HttpOnly, no expiration (indefinite)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="none" if not secure else "lax",
        path="/",
    )
    
    # Set refresh token cookie - HttpOnly, expires in 30 days
    refresh_expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="none" if not secure else "lax",
        path="/",
        expires=refresh_expires,
    )
    
    return response


def create_logout_response() -> JSONResponse:
    """
    Create JSONResponse that clears authentication cookies.
    
    Returns:
        JSONResponse with expired cookies
    """
    response = JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=200
    )
    
    # Clear both cookies
    response.delete_cookie(key="access_token", path="/", secure=False)
    response.delete_cookie(key="refresh_token", path="/", secure=False)
    
    return response
