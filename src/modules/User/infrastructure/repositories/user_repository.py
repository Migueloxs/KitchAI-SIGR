"""
Repositorio UserRepository - Manejo de persistencia de usuarios.
"""
from typing import Optional
from datetime import datetime
from src.modules.User.domain.entities.user import User
from src.shared.infrastructure.database.turso_connection import get_turso_client


class UserRepository:
    """
    Repositorio para manejar la persistencia de usuarios en la base de datos.
    Implementa operaciones CRUD y consultas específicas del dominio.
    """
    
    def __init__(self):
        """Inicializar el repositorio con la conexión a la base de datos."""
        self.client = get_turso_client()
    
    def save(self, user: User) -> User:
        """
        Guardar un nuevo usuario en la base de datos.
        
        Args:
            user: Entidad User a guardar
        
        Returns:
            Entidad User guardada
        
        Raises:
            Exception: Si hay un error al guardar
        """
        try:
            self.client.execute(
                """
                INSERT INTO users (
                    id, name, email, phone, password_hash, role_id,
                    failed_login_attempts, locked_until, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    user.id,
                    user.name,
                    user.email,
                    user.phone,
                    user.password_hash,
                    user.role_id,
                    user.failed_login_attempts,
                    user.locked_until.isoformat() if user.locked_until else None,
                    user.created_at.isoformat(),
                    user.updated_at.isoformat()
                ]
            )
            return user
        except Exception as e:
            print(f"Error al guardar usuario: {str(e)}")
            raise
    
    def update(self, user: User) -> User:
        """
        Actualizar un usuario existente en la base de datos.
        
        Args:
            user: Entidad User con los datos actualizados
        
        Returns:
            Entidad User actualizada
        
        Raises:
            Exception: Si hay un error al actualizar
        """
        try:
            self.client.execute(
                """
                UPDATE users SET
                    name = ?,
                    phone = ?,
                    password_hash = ?,
                    role_id = ?,
                    failed_login_attempts = ?,
                    locked_until = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                [
                    user.name,
                    user.phone,
                    user.password_hash,
                    user.role_id,
                    user.failed_login_attempts,
                    user.locked_until.isoformat() if user.locked_until else None,
                    user.updated_at.isoformat(),
                    user.id
                ]
            )
            return user
        except Exception as e:
            print(f"Error al actualizar usuario: {str(e)}")
            raise
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Buscar un usuario por su ID.
        
        Args:
            user_id: ID del usuario a buscar
        
        Returns:
            Entidad User si se encuentra, None en caso contrario
        """
        try:
            result = self.client.execute(
                """
                SELECT id, name, email, phone, password_hash, role_id,
                       failed_login_attempts, locked_until, created_at, updated_at
                FROM users
                WHERE id = ?
                """,
                [user_id]
            )
            
            if not result.rows:
                return None
            
            return self._map_to_entity(result.rows[0])
        except Exception as e:
            print(f"Error al buscar usuario por ID: {str(e)}")
            return None
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Buscar un usuario por su email.
        
        Args:
            email: Email del usuario a buscar
        
        Returns:
            Entidad User si se encuentra, None en caso contrario
        """
        try:
            result = self.client.execute(
                """
                SELECT id, name, email, phone, password_hash, role_id,
                       failed_login_attempts, locked_until, created_at, updated_at
                FROM users
                WHERE LOWER(email) = LOWER(?)
                """,
                [email]
            )
            
            if not result.rows:
                return None
            
            return self._map_to_entity(result.rows[0])
        except Exception as e:
            print(f"Error al buscar usuario por email: {str(e)}")
            return None
    
    def email_exists(self, email: str) -> bool:
        """
        Verificar si un email ya está registrado.
        
        Args:
            email: Email a verificar
        
        Returns:
            True si el email existe, False en caso contrario
        """
        try:
            result = self.client.execute(
                "SELECT COUNT(*) FROM users WHERE LOWER(email) = LOWER(?)",
                [email]
            )
            count = result.rows[0][0]
            return count > 0
        except Exception as e:
            print(f"Error al verificar existencia de email: {str(e)}")
            return False
    
    def _map_to_entity(self, row) -> User:
        """
        Mapear una fila de la base de datos a una entidad User.
        
        Args:
            row: Fila de resultado de la consulta
        
        Returns:
            Entidad User
        """
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            phone=row[3],
            password_hash=row[4],
            role_id=row[5],
            failed_login_attempts=row[6] or 0,
            locked_until=datetime.fromisoformat(row[7]) if row[7] else None,
            created_at=datetime.fromisoformat(row[8]) if isinstance(row[8], str) else row[8],
            updated_at=datetime.fromisoformat(row[9]) if isinstance(row[9], str) else row[9]
        )
