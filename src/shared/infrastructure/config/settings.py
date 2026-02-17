"""
Configuración de la aplicación usando variables de entorno.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
# Buscar el archivo .env en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# Cargar explícitamente el archivo .env con override=True
load_dotenv(ENV_FILE, override=True)


class Settings:
    """Configuración de la aplicación."""
    
    # Database
    TURSO_DATABASE_URL: str = os.getenv("TURSO_DATABASE_URL", "")
    TURSO_AUTH_TOKEN: str = os.getenv("TURSO_AUTH_TOKEN", "")
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # JWT (JSON Web Tokens) - Configuración para autenticación
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    
    def __init__(self):
        """Validar que las variables necesarias estén configuradas."""
        if not self.TURSO_DATABASE_URL:
            raise ValueError(
                f"TURSO_DATABASE_URL no está configurada en el archivo .env\n"
                f"Buscando en: {ENV_FILE}\n"
                f"Archivo existe: {ENV_FILE.exists()}"
            )
        if not self.TURSO_AUTH_TOKEN:
            raise ValueError("TURSO_AUTH_TOKEN no está configurado en el archivo .env")
        
        # Validar configuración JWT en producción
        if self.is_production and not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY no está configurado en el archivo .env")
        
        # En desarrollo, generar una clave temporal si no existe
        if self.is_development and not self.JWT_SECRET_KEY:
            import secrets
            self.JWT_SECRET_KEY = secrets.token_urlsafe(32)
            print("⚠️  JWT_SECRET_KEY no configurado. Usando clave temporal para desarrollo.")
    
    @property
    def is_production(self) -> bool:
        """Verificar si el entorno es producción."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Verificar si el entorno es desarrollo."""
        return self.ENVIRONMENT == "development"


# Instancia global de configuración
settings = Settings()
