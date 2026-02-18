"""
DTO ChangeRoleRequest - Cuerpo para modificar el rol de un usuario.
"""
from pydantic import BaseModel, Field


class ChangeRoleRequest(BaseModel):
    """Solicitud para actualizar el rol de un usuario existente.

    Attributes:
        role: Nombre del nuevo rol (admin, employee, waiter)
    """
    role: str = Field(
        ...,
        description="Nuevo rol del usuario (admin, employee o waiter)"
    )

    @classmethod
    def validate_role(cls, v: str) -> str:  # type: ignore
        valid_roles = ['admin', 'employee', 'waiter']
        v_lower = v.lower()
        if v_lower not in valid_roles:
            raise ValueError(f"El rol debe ser uno de: {', '.join(valid_roles)}")
        return v_lower
