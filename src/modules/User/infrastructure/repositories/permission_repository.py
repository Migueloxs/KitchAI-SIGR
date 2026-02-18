"""
Repositorio PermissionRepository - Manejo de persistencia de permisos.
"""
from typing import Optional, List
from src.modules.User.domain.entities.permission import Permission
from src.shared.infrastructure.database.turso_connection import get_turso_client
from datetime import datetime


class PermissionRepository:
    """Repositorio para manejar la persistencia de permisos en la base de datos."""

    def __init__(self):
        """Inicializar el repositorio con conexión a la BD."""
        self.client = get_turso_client()

    def find_by_id(self, permission_id: str) -> Optional[Permission]:
        """Buscar un permiso por su ID."""
        try:
            result = self.client.execute(
                "SELECT id, name, description, created_at FROM permissions WHERE id = ?",
                [permission_id]
            )
            if not result.rows:
                return None
            row = result.rows[0]
            return self._map_to_entity(row)
        except Exception as e:
            print(f"Error al buscar permiso por ID: {str(e)}")
            return None

    def find_by_name(self, name: str) -> Optional[Permission]:
        """Buscar un permiso por su nombre."""
        try:
            result = self.client.execute(
                "SELECT id, name, description, created_at FROM permissions WHERE LOWER(name) = LOWER(?)",
                [name]
            )
            if not result.rows:
                return None
            row = result.rows[0]
            return self._map_to_entity(row)
        except Exception as e:
            print(f"Error al buscar permiso por nombre: {str(e)}")
            return None

    def find_all(self) -> List[Permission]:
        """Obtener todos los permisos disponibles."""
        try:
            result = self.client.execute(
                "SELECT id, name, description, created_at FROM permissions ORDER BY name"
            )
            return [self._map_to_entity(row) for row in result.rows]
        except Exception as e:
            print(f"Error al obtener todos los permisos: {str(e)}")
            return []

    def find_by_role_id(self, role_id: str) -> List[Permission]:
        """Obtener todos los permisos asociados a un rol."""
        try:
            result = self.client.execute(
                """
                SELECT DISTINCT p.id, p.name, p.description, p.created_at
                FROM permissions p
                INNER JOIN role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                ORDER BY p.name
                """,
                [role_id]
            )
            return [self._map_to_entity(row) for row in result.rows]
        except Exception as e:
            print(f"Error al obtener permisos del rol: {str(e)}")
            return []

    def _map_to_entity(self, row) -> Permission:
        """Mapear una fila a una entidad Permission."""
        return Permission(
            id=row[0],
            name=row[1],
            description=row[2],
            created_at=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3]
        )
