"""
DTO PermissionResponse - Información sobre permisos.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PermissionResponse(BaseModel):
    """Respuesta con la información de un permiso.

    Attributes:
        id: ID único del permiso
        name: Nombre del permiso
        description: Descripción de lo que permite
        created_at: Fecha de creación
    """
    id: str = Field(
        ...,
        description="Identificador único del permiso"
    )

    name: str = Field(
        ...,
        description="Nombre del permiso"
    )

    description: Optional[str] = Field(
        None,
        description="Descripción o explicación del permiso"
    )

    created_at: datetime = Field(
        ...,
        description="Fecha de creación del permiso"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "perm-1",
                    "name": "manage_users",
                    "description": "Gestionar usuarios",
                    "created_at": "2026-02-17T10:30:00"
                }
            ]
        }
    }


class RolePermissionsResponse(BaseModel):
    """Respuesta con detalles de un rol y sus permisos asociados.

    Attributes:
        id: ID del rol
        name: Nombre del rol
        description: Descripción del rol
        permissions: Lista de permisos asociados
    """
    id: str = Field(..., description="ID del rol")
    name: str = Field(..., description="Nombre del rol")
    description: Optional[str] = Field(None, description="Descripción del rol")
    permissions: list[PermissionResponse] = Field(
        default_factory=list,
        description="Permisos asociados a este rol"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "uuid-role-admin",
                    "name": "admin",
                    "description": "Administrador con acceso total",
                    "permissions": [
                        {
                            "id": "perm-1",
                            "name": "manage_users",
                            "description": "Gestionar usuarios",
                            "created_at": "2026-02-17T10:30:00"
                        },
                        {
                            "id": "perm-2",
                            "name": "manage_inventory",
                            "description": "Gestionar inventario",
                            "created_at": "2026-02-17T10:30:00"
                        }
                    ]
                }
            ]
        }
    }
