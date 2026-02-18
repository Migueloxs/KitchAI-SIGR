"""
Repositorios de infraestructura para el módulo User.
Los repositorios manejan la persistencia de datos en la base de datos.
"""
from .user_repository import UserRepository
from .role_repository import RoleRepository
from .login_attempt_repository import LoginAttemptRepository
from .permission_repository import PermissionRepository

__all__ = ["UserRepository", "RoleRepository", "LoginAttemptRepository", "PermissionRepository"]
