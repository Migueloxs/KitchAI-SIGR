"""
DTO RegisterRequest - Datos requeridos para el registro de un nuevo usuario.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    """
    DTO para la solicitud de registro de un nuevo usuario.
    Valida que todos los campos cumplan con los requisitos.
    
    Attributes:
        name: Nombre completo del usuario
        email: Correo electrónico (debe ser único)
        phone: Número de teléfono (opcional)
        password: Contraseña en texto plano (será hasheada)
        role: Rol del usuario (admin, employee, waiter)
    """
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Nombre completo del usuario"
    )
    
    email: EmailStr = Field(
        ...,
        description="Correo electrónico válido y único"
    )
    
    phone: Optional[str] = Field(
        None,
        min_length=8,
        max_length=20,
        description="Número de teléfono (opcional)"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña segura (mínimo 8 caracteres, debe incluir mayúsculas, minúsculas, números y caracteres especiales)"
    )
    
    role: str = Field(
        ...,
        description="Rol del usuario en el sistema"
    )
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validar que el rol sea uno de los permitidos."""
        valid_roles = ['admin', 'employee', 'waiter']
        v_lower = v.lower()
        if v_lower not in valid_roles:
            raise ValueError(f"El rol debe ser uno de: {', '.join(valid_roles)}")
        return v_lower
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validar y normalizar el nombre."""
        # Eliminar espacios extra
        v = ' '.join(v.split())
        
        if not v.replace(' ', '').isalpha():
            raise ValueError("El nombre solo puede contener letras y espacios")
        
        return v.title()  # Primera letra en mayúscula
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validar el formato del teléfono si se proporciona."""
        if v is None:
            return None
        
        # Eliminar espacios y guiones
        v = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Validar que solo contenga números y el símbolo +
        if not all(c.isdigit() or c == '+' for c in v):
            raise ValueError("El teléfono solo puede contener números y el símbolo +")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Juan Pérez",
                    "email": "juan.perez@example.com",
                    "phone": "+1829555-1234",
                    "password": "SecurePass123!",
                    "role": "waiter"
                }
            ]
        }
    }
