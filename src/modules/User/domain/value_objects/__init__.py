"""
Value Objects del dominio User.
Los value objects son objetos inmutables que representan conceptos del dominio.
"""
from .email import Email
from .password import Password

__all__ = ["Email", "Password"]
