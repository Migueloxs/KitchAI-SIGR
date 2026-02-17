"""
Entidad User - Representa un usuario del sistema.
Esta es la entidad principal del dominio de usuarios, 
encapsula toda la lógica de negocio relacionada con un usuario.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class User:
    """
    Entidad que representa un usuario en el sistema.
    
    Attributes:
        id: Identificador único del usuario (UUID)
        name: Nombre completo del usuario
        email: Correo electrónico (único en el sistema)
        phone: Número de teléfono (opcional)
        password_hash: Contraseña hasheada (nunca en texto plano)
        role_id: ID del rol asignado al usuario
        failed_login_attempts: Contador de intentos fallidos de login
        locked_until: Fecha hasta la cual la cuenta está bloqueada (si aplica)
        created_at: Fecha de creación de la cuenta
        updated_at: Fecha de última actualización
    """
    id: str
    name: str
    email: str
    password_hash: str
    role_id: str
    phone: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.id:
            raise ValueError("El ID del usuario es obligatorio")
        if not self.name:
            raise ValueError("El nombre es obligatorio")
        if not self.email:
            raise ValueError("El email es obligatorio")
        if not self.password_hash:
            raise ValueError("El hash de contraseña es obligatorio")
        if not self.role_id:
            raise ValueError("El rol es obligatorio")
    
    def is_locked(self) -> bool:
        """
        Verificar si la cuenta está bloqueada.
        
        Returns:
            True si la cuenta está bloqueada, False en caso contrario
        """
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until
    
    def lock_account(self, duration_minutes: int = 15) -> None:
        """
        Bloquear la cuenta del usuario por un período determinado.
        Se bloquea cuando se superan los intentos de login permitidos.
        
        Args:
            duration_minutes: Duración del bloqueo en minutos (por defecto 15)
        """
        self.locked_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.updated_at = datetime.now()
    
    def unlock_account(self) -> None:
        """
        Desbloquear la cuenta del usuario manualmente.
        También resetea el contador de intentos fallidos.
        """
        self.locked_until = None
        self.failed_login_attempts = 0
        self.updated_at = datetime.now()
    
    def increment_failed_attempts(self, max_attempts: int = 5) -> None:
        """
        Incrementar el contador de intentos fallidos de login.
        Si se alcanza el máximo, la cuenta se bloquea automáticamente.
        
        Args:
            max_attempts: Número máximo de intentos permitidos antes del bloqueo
        """
        self.failed_login_attempts += 1
        self.updated_at = datetime.now()
        
        # Bloquear la cuenta si se alcanza el máximo de intentos
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
    
    def reset_failed_attempts(self) -> None:
        """
        Resetear el contador de intentos fallidos.
        Se llama tras un login exitoso.
        """
        self.failed_login_attempts = 0
        self.updated_at = datetime.now()
    
    def update_profile(self, name: Optional[str] = None, 
                       phone: Optional[str] = None) -> None:
        """
        Actualizar información del perfil del usuario.
        
        Args:
            name: Nuevo nombre (opcional)
            phone: Nuevo teléfono (opcional)
        """
        if name:
            self.name = name
        if phone:
            self.phone = phone
        self.updated_at = datetime.now()
