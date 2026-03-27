"""
Role-Based Access Control (RBAC) middleware for FastAPI.

Provides permission checking based on user roles.
"""

from typing import List, Dict
from fastapi import HTTPException, status


def check_permission(current_user: Dict, required_roles: List[str]) -> bool:
    """
    Check if user has any of the required roles.
    
    Args:
        current_user: User data from JWT token (dict with 'roles' key)
        required_roles: List of required roles (user needs at least one)
    
    Raises:
        HTTPException: If user doesn't have required role
        
    Returns:
        True if user has permission
    """
    if not current_user or "roles" not in current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User information not found in token",
        )
    
    user_roles = current_user.get("roles", [])
    
    # Check if user has any of the required roles
    for role in required_roles:
        if role in user_roles:
            return True
    
    # User doesn't have required role
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"User does not have required role. Required: {', '.join(required_roles)}",
    )


def get_user_roles(current_user: Dict) -> List[str]:
    """
    Get user roles from current user data.
    
    Args:
        current_user: User data from JWT token
        
    Returns:
        List of user roles
    """
    return current_user.get("roles", [])


def has_role(current_user: Dict, role: str) -> bool:
    """
    Check if user has a specific role.
    
    Args:
        current_user: User data from JWT token
        role: Role to check for
        
    Returns:
        True if user has the role, False otherwise
    """
    user_roles = get_user_roles(current_user)
    return role in user_roles


def is_admin(current_user: Dict) -> bool:
    """
    Check if user is admin.
    
    Args:
        current_user: User data from JWT token
        
    Returns:
        True if user is admin, False otherwise
    """
    return has_role(current_user, "ADMIN")


def is_hr_manager(current_user: Dict) -> bool:
    """
    Check if user is HR manager.
    
    Args:
        current_user: User data from JWT token
        
    Returns:
        True if user is HR manager, False otherwise
    """
    return has_role(current_user, "HR_MANAGER")
