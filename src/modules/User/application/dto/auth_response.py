"""
DTO AuthResponse - Respuesta exitosa de autenticación con token JWT.
"""
from pydantic import BaseModel, Field
from .user_response import UserResponse


class AuthResponse(BaseModel):
    """
    DTO para la respuesta de autenticación exitosa.
    Incluye el token JWT y la información del usuario.
    
    Attributes:
        access_token: Token JWT para autenticación en futuras peticiones
        token_type: Tipo de token (siempre "bearer")
        user: Información del usuario autenticado
    """
    access_token: str = Field(
        ...,
        description="Token JWT para autenticación"
    )
    
    token_type: str = Field(
        default="bearer",
        description="Tipo de token (Bearer)"
    )
    
    user: UserResponse = Field(
        ...,
        description="Información del usuario autenticado"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Juan Pérez",
                        "email": "juan.perez@example.com",
                        "phone": "+18295551234",
                        "role_id": "uuid-role-waiter",
                        "created_at": "2026-02-17T10:30:00"
                    }
                }
            ]
        }
    }
