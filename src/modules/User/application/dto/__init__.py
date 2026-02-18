"""
DTOs (Data Transfer Objects) para el módulo de autenticación.
Los DTOs definen la estructura de los datos que se transfieren 
entre las capas de la aplicación y la API.
"""
from .register_request import RegisterRequest
from .login_request import LoginRequest
from .user_response import UserResponse
from .auth_response import AuthResponse
from .change_role_request import ChangeRoleRequest
from .permission_response import PermissionResponse, RolePermissionsResponse

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "AuthResponse",
    "ChangeRoleRequest",
    "PermissionResponse",
    "RolePermissionsResponse"
]
