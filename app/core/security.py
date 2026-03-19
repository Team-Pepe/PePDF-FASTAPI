from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import JWTError, jwt
import bcrypt
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
