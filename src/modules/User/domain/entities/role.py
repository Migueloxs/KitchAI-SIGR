"""
Entidad Role - Representa un rol del sistema (admin, employee, waiter).
Define los roles que pueden tener los usuarios en el sistema de restaurante.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Role:
    """
    Entidad que representa un rol en el sistema.
    
    Attributes:
        id: Identificador único del rol (UUID)
        name: Nombre del rol (admin, employee, waiter)
        description: Descripción del rol
        created_at: Fecha de creación del rol
    """
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.id:
            raise ValueError("El ID del rol es obligatorio")
        if not self.name:
            raise ValueError("El nombre del rol es obligatorio")
        
        # Normalizar el nombre del rol a minúsculas
        self.name = self.name.lower()
        
        # Validar que el rol sea uno de los permitidos
        valid_roles = ["admin", "employee", "waiter"]
        if self.name not in valid_roles:
            raise ValueError(f"El rol debe ser uno de: {', '.join(valid_roles)}")
    
    def is_admin(self) -> bool:
        """Verificar si el rol es administrador."""
        return self.name == "admin"
    
    def is_employee(self) -> bool:
        """Verificar si el rol es empleado."""
        return self.name == "employee"
    
    def is_waiter(self) -> bool:
        """Verificar si el rol es mesero."""
        return self.name == "waiter"
