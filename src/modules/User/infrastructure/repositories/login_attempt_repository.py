"""
Repositorio LoginAttemptRepository - Registro de intentos de login.
"""
from datetime import datetime
from typing import List
from src.shared.infrastructure.database.turso_connection import get_turso_client
import uuid


class LoginAttemptRepository:
    """
    Repositorio para registrar los intentos de login (exitosos y fallidos).
    Útil para auditoría y análisis de seguridad.
    """
    
    def __init__(self):
        """Inicializar el repositorio con la conexión a la base de datos."""
        self.client = get_turso_client()
    
    def save_attempt(self, email: str, success: bool, ip_address: str = None) -> None:
        """
        Registrar un intento de login.
        
        Args:
            email: Email del usuario que intentó hacer login
            success: True si fue exitoso, False si falló
            ip_address: Dirección IP desde donde se hizo el intento (opcional)
        """
        try:
            attempt_id = str(uuid.uuid4())
            self.client.execute(
                """
                INSERT INTO login_attempts (id, email, success, ip_address, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    attempt_id,
                    email,
                    1 if success else 0,
                    ip_address,
                    datetime.now().isoformat()
                ]
            )
        except Exception as e:
            print(f"Error al guardar intento de login: {str(e)}")
            # No lanzamos excepción para no interrumpir el flujo de autenticación
    
    def get_recent_failed_attempts(self, email: str, minutes: int = 15) -> int:
        """
        Obtener el número de intentos fallidos recientes para un email.
        
        Args:
            email: Email del usuario
            minutes: Ventana de tiempo en minutos (por defecto 15)
        
        Returns:
            Número de intentos fallidos en el período especificado
        """
        try:
            # Calcular el timestamp de hace X minutos
            time_threshold = datetime.now().timestamp() - (minutes * 60)
            
            result = self.client.execute(
                """
                SELECT COUNT(*) 
                FROM login_attempts 
                WHERE LOWER(email) = LOWER(?) 
                  AND success = 0 
                  AND created_at >= datetime(?, 'unixepoch')
                """,
                [email, time_threshold]
            )
            
            return result.rows[0][0]
        except Exception as e:
            print(f"Error al obtener intentos fallidos recientes: {str(e)}")
            return 0
    
    def get_attempts_by_email(self, email: str, limit: int = 10) -> List[dict]:
        """
        Obtener el historial de intentos de login para un email.
        Útil para auditoría y análisis de seguridad.
        
        Args:
            email: Email del usuario
            limit: Número máximo de registros a retornar
        
        Returns:
            Lista de intentos de login
        """
        try:
            result = self.client.execute(
                """
                SELECT id, email, success, ip_address, created_at
                FROM login_attempts
                WHERE LOWER(email) = LOWER(?)
                ORDER BY created_at DESC
                LIMIT ?
                """,
                [email, limit]
            )
            
            attempts = []
            for row in result.rows:
                attempts.append({
                    "id": row[0],
                    "email": row[1],
                    "success": bool(row[2]),
                    "ip_address": row[3],
                    "created_at": row[4]
                })
            
            return attempts
        except Exception as e:
            print(f"Error al obtener historial de intentos: {str(e)}")
            return []
