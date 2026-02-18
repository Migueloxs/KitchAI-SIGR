"""
Conexión a Turso DB (LibSQL) - Capa de Infraestructura.
Este módulo maneja la conexión a la base de datos Turso usando el patrón Singleton.
"""
from typing import Optional
from libsql_client import create_client_sync

from src.shared.infrastructure.config.settings import settings


class TursoConnection:
    """
    Clase Singleton para manejar la conexión a Turso DB.
    Asegura que solo exista una instancia de la conexión en toda la aplicación.
    """
    
    _instance: Optional["TursoConnection"] = None
    _client = None
    
    def __new__(cls):
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(TursoConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar la conexión (solo se ejecuta una vez)."""
        if self._client is None:
            self._connect()
    
    def _connect(self) -> None:
        """Establecer la conexión con Turso DB."""
        try:
            self._client = create_client_sync(
                url=settings.TURSO_DATABASE_URL,
                auth_token=settings.TURSO_AUTH_TOKEN
            )
            print(f"✅ Conexión exitosa a Turso DB ({settings.ENVIRONMENT})")
        except Exception as e:
            print(f"❌ Error al conectar con Turso DB: {str(e)}")
            raise
    
    @property
    def client(self):
        """
        Obtener el cliente de conexión a Turso DB.
        
        Returns:
            Client: Cliente de libsql para ejecutar consultas.
        
        Raises:
            RuntimeError: Si no se ha establecido la conexión.
        """
        if self._client is None:
            raise RuntimeError("No hay conexión activa con Turso DB")
        return self._client
    
    def execute(self, query: str, params: Optional[list] = None):
        """
        Ejecutar una consulta SQL.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta (opcional).
        
        Returns:
            Resultado de la consulta.
        """
        try:
            if params:
                result = self.client.execute(query, params)
            else:
                result = self.client.execute(query)
            return result
        except Exception as e:
            print(f"❌ Error al ejecutar consulta: {str(e)}")
            raise
    
    def close(self) -> None:
        """Cerrar la conexión con Turso DB."""
        if self._client is not None:
            self._client.close()
            self._client = None
            print("🔌 Conexión cerrada con Turso DB")


# Instancia global de la conexión
turso_db = TursoConnection()


# Función helper para obtener el cliente
def get_turso_client():
    """
    Obtener el cliente de Turso DB para usar en repositorios.
    
    Returns:
        Client: Cliente de libsql.
    
    Example:
        >>> client = get_turso_client()
        >>> result = client.execute("SELECT * FROM users")
    """
    return turso_db.client
