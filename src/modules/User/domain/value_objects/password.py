"""
Value Object Password - Representa una contraseña válida.
Encapsula las reglas de validación de contraseñas seguras.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Password:
    """
    Value Object que representa una contraseña válida.
    Valida que la contraseña cumpla con los requisitos de seguridad.
    
    Attributes:
        value: El valor de la contraseña en texto plano
    
    Raises:
        ValueError: Si la contraseña no cumple con los requisitos de seguridad
    """
    value: str
    
    def __post_init__(self):
        """Validar la fortaleza de la contraseña al crear la instancia."""
        if not self.value:
            raise ValueError("La contraseña no puede estar vacía")
        
        # Longitud mínima de 8 caracteres
        if len(self.value) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        # Longitud máxima de 128 caracteres
        if len(self.value) > 128:
            raise ValueError("La contraseña no puede tener más de 128 caracteres")
        
        # Debe contener al menos una letra minúscula
        if not re.search(r'[a-z]', self.value):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        
        # Debe contener al menos una letra mayúscula
        if not re.search(r'[A-Z]', self.value):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        
        # Debe contener al menos un número
        if not re.search(r'\d', self.value):
            raise ValueError("La contraseña debe contener al menos un número")
        
        # Debe contener al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', self.value):
            raise ValueError("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>)")
    
    def __str__(self) -> str:
        """Representación en string (oculta la contraseña por seguridad)."""
        return "********"
    
    def __repr__(self) -> str:
        """Representación para debugging (oculta la contraseña)."""
        return "Password(********)"
