"""
Casos de uso (Use Cases) del módulo de autenticación.
Los casos de uso implementan la lógica de negocio de la aplicación.
"""
from .register_user import RegisterUserUseCase
from .login_user import LoginUserUseCase
from .update_user_role import UpdateUserRoleUseCase

__all__ = ["RegisterUserUseCase", "LoginUserUseCase", "UpdateUserRoleUseCase"]
