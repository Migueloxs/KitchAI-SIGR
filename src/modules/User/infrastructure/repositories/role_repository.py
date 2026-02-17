"""
Repositorio RoleRepository - Manejo de persistencia de roles.
"""
from typing import Optional, List
from src.modules.User.domain.entities.role import Role
from src.shared.infrastructure.database.turso_connection import get_turso_client
from datetime import datetime


class RoleRepository:
    """
    Repositorio para manejar la persistencia de roles en la base de datos.
    Implementa el patrón Repository para abstraer la capa de datos.
    """
    
    def __init__(self):
        """Inicializar el repositorio con la conexión a la base de datos."""
        self.client = get_turso_client()
    
    def find_by_id(self, role_id: str) -> Optional[Role]:
        """
        Buscar un rol por su ID.
        
        Args:
            role_id: ID del rol a buscar
        
        Returns:
            Entidad Role si se encuentra, None en caso contrario
        """
        try:
            result = self.client.execute(
                "SELECT id, name, description, created_at FROM roles WHERE id = ?",
                [role_id]
            )
            
            if not result.rows:
                return None
            
            row = result.rows[0]
            return self._map_to_entity(row)
        except Exception as e:
            print(f"Error al buscar rol por ID: {str(e)}")
            return None
    
    def find_by_name(self, name: str) -> Optional[Role]:
        """
        Buscar un rol por su nombre.
        
        Args:
            name: Nombre del rol (admin, employee, waiter)
        
        Returns:
            Entidad Role si se encuentra, None en caso contrario
        """
        try:
            result = self.client.execute(
                "SELECT id, name, description, created_at FROM roles WHERE LOWER(name) = LOWER(?)",
                [name]
            )
            
            if not result.rows:
                return None
            
            row = result.rows[0]
            return self._map_to_entity(row)
        except Exception as e:
            print(f"Error al buscar rol por nombre: {str(e)}")
            return None
    
    def find_all(self) -> List[Role]:
        """
        Obtener todos los roles disponibles en el sistema.
        
        Returns:
            Lista de entidades Role
        """
        try:
            result = self.client.execute(
                "SELECT id, name, description, created_at FROM roles ORDER BY name"
            )
            
            return [self._map_to_entity(row) for row in result.rows]
        except Exception as e:
            print(f"Error al obtener todos los roles: {str(e)}")
            return []
    
    def _map_to_entity(self, row) -> Role:
        """
        Mapear una fila de la base de datos a una entidad Role.
        
        Args:
            row: Fila de resultado de la consulta
        
        Returns:
            Entidad Role
        """
        return Role(
            id=row[0],
            name=row[1],
            description=row[2],
            created_at=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3]
        )
