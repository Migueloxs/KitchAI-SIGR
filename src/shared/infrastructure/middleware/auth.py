"""
Authentication middleware for FastAPI.

Provides JWT token verification and user authentication.
"""

import os
from datetime import datetime, timedelta
import jwt
from typing import Dict
from fastapi import HTTPException, status, Header
from functools import lru_cache

# Get JWT secret key from environment or use default for development
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


@lru_cache(maxsize=128)
def get_secret_key() -> str:
    """Get JWT secret key from environment."""
    return JWT_SECRET_KEY


async def verify_token(authorization: str = Header(None)) -> Dict:
    """
    Verify JWT token from Authorization header.
    
    Expected format: "Bearer <token>"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from "Bearer <token>" format
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = parts[1]
        
        # Decode JWT token
        payload = jwt.decode(
            token,
            get_secret_key(),
            algorithms=[JWT_ALGORITHM]
        )
        
        # Return user data from token payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing user ID",
            )
        
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", []),
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_token(user_id: str, email: str, roles: list = None, expires_hours: int = None) -> str:
    """
    Create a JWT token for the user.
    
    Args:
        user_id: User ID
        email: User email  
        roles: List of user roles
        expires_hours: Token expiration time in hours (None = use default)
    
    Returns:
        JWT token string
    """
    if roles is None:
        roles = []
    
    if expires_hours is None:
        expires_hours = JWT_EXPIRATION_HOURS
    
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    
    payload = {
        "sub": user_id,
        "email": email,
        "roles": roles,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(
        payload,
        get_secret_key(),
        algorithm=JWT_ALGORITHM
    )
    
    return token
