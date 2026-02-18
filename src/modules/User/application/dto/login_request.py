"""
DTO LoginRequest - Datos requeridos para el inicio de sesión.
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    DTO para la solicitud de inicio de sesión.
    
    Attributes:
        email: Correo electrónico del usuario
        password: Contraseña en texto plano
    """
    email: EmailStr = Field(
        ...,
        description="Correo electrónico del usuario"
    )
    
    password: str = Field(
        ...,
        min_length=1,
        description="Contraseña del usuario"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "juan.perez@example.com",
                    "password": "SecurePass123!"
                }
            ]
        }
    }
