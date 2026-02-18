"""
DTO UserResponse - Respuesta con información del usuario (sin contraseña).
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """
    DTO para la respuesta con información del usuario.
    NUNCA incluye la contraseña por seguridad.
    
    Attributes:
        id: Identificador único del usuario
        name: Nombre completo
        email: Correo electrónico
        phone: Número de teléfono
        role_id: ID del rol asignado
        created_at: Fecha de creación de la cuenta
    """
    id: str = Field(
        ...,
        description="Identificador único del usuario (UUID)"
    )
    
    name: str = Field(
        ...,
        description="Nombre completo del usuario"
    )
    
    email: EmailStr = Field(
        ...,
        description="Correo electrónico del usuario"
    )
    
    phone: Optional[str] = Field(
        None,
        description="Número de teléfono del usuario"
    )
    
    role_id: str = Field(
        ...,
        description="ID del rol asignado al usuario"
    )
    
    created_at: datetime = Field(
        ...,
        description="Fecha y hora de creación de la cuenta"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Juan Pérez",
                    "email": "juan.perez@example.com",
                    "phone": "+18295551234",
                    "role_id": "uuid-role-waiter",
                    "created_at": "2026-02-17T10:30:00"
                }
            ]
        }
    }
