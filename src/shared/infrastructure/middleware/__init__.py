"""
Middleware package for shared infrastructure.

Provides authentication, authorization, and other middleware functionality.
"""

from .auth import verify_token, create_token
from .rbac import check_permission, get_user_roles, has_role, is_admin, is_hr_manager

__all__ = [
    "verify_token",
    "create_token",
    "check_permission",
    "get_user_roles",
    "has_role",
    "is_admin",
    "is_hr_manager",
]
