"""
Value Object Email - Representa un correo electrónico válido.
Encapsula la validación de formato de email.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Value Object que representa un email válido.
    Es inmutable (frozen=True) siguiendo el patrón de Value Objects.
    
    Attributes:
        value: El valor del email
    
    Raises:
        ValueError: Si el email no tiene un formato válido
    """
    value: str
    
    def __post_init__(self):
        """Validar el formato del email al crear la instancia."""
        if not self.value:
            raise ValueError("El email no puede estar vacío")
        
        # Expresión regular para validar el formato básico de un email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, self.value):
            raise ValueError(f"El email '{self.value}' no tiene un formato válido")
        
        # Validar longitud máxima
        if len(self.value) > 255:
            raise ValueError("El email no puede tener más de 255 caracteres")
    
    def get_domain(self) -> str:
        """
        Obtener el dominio del email.
        
        Returns:
            El dominio del email (ej: 'gmail.com' para 'usuario@gmail.com')
        """
        return self.value.split('@')[1]
    
    def __str__(self) -> str:
        """Representación en string del email."""
        return self.value
