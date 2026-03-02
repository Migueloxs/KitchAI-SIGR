"""
Entidades del dominio User.
Aquí se definen las entidades principales del módulo de usuarios.
"""
from .user import User
from .role import Role
from .permission import Permission

__all__ = ["User", "Role", "Permission"]
