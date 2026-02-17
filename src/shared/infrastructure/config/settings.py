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
