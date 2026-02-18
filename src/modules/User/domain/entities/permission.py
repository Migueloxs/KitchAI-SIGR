"""
Entidad Permission - Representa un permiso en el sistema.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Permission:
    """Entidad que representa un permiso del sistema.

    Un permiso define una acción que puede realizar un rol.
    Ejemplo: manage_users, manage_inventory, view_reports, etc.

    Attributes:
        id: Identificador único (UUID)
        name: Nombre del permiso (único)
        description: Descripción del permiso
        created_at: Fecha de creación
    """
    id: str
    name: str
    description: str = None  # type: ignore
    created_at: datetime = None  # type: ignore
