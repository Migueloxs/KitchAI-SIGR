"""
Caso de Uso: Autenticar un usuario (Login).
Implementa toda la lógica de negocio para el inicio de sesión.
"""
from typing import Optional, Tuple
from datetime import datetime

from src.modules.User.domain.entities.user import User
from src.modules.User.domain.services.password_service import PasswordService
from src.modules.User.infrastructure.repositories.user_repository import UserRepository
from src.modules.User.infrastructure.repositories.login_attempt_repository import LoginAttemptRepository
from src.modules.User.application.dto.login_request import LoginRequest


class LoginUserUseCase:
    """
    Caso de uso para autenticar un usuario.
    
    Flujo:
    1. Buscar usuario por email
    2. Verificar si la cuenta está bloqueada
    3. Verificar la contraseña
    4. Actualizar intentos de login
    5. Registrar el intento en el historial
    
    Implementa el requisito CA3:
    - Si el login falla 5 veces consecutivas, la cuenta se bloquea por 15 minutos
    - Retorna error 429 (Too Many Requests) cuando está bloqueada
    
    Attributes:
        user_repository: Repositorio de usuarios
        login_attempt_repository: Repositorio de intentos de login
        password_service: Servicio para verificar contraseñas
    """
    
    MAX_FAILED_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 15
    
    def __init__(
        self,
        user_repository: UserRepository,
        login_attempt_repository: LoginAttemptRepository,
        password_service: PasswordService
    ):
        """
        Inicializar el caso de uso con sus dependencias.
        
        Args:
            user_repository: Repositorio de usuarios
            login_attempt_repository: Repositorio de intentos de login
            password_service: Servicio de contraseñas
        """
        self.user_repository = user_repository
        self.login_attempt_repository = login_attempt_repository
        self.password_service = password_service
    
    def execute(self, request: LoginRequest, ip_address: Optional[str] = None) -> Tuple[Optional[User], str, int]:
        """
        Ejecutar el caso de uso de login.
        
        Args:
            request: DTO con las credenciales del usuario
            ip_address: Dirección IP del cliente (para auditoría)
        
        Returns:
            Tupla con (Usuario si login exitoso, Mensaje de error, Código HTTP)
            - (User, None, 200) si el login es exitoso
            - (None, "mensaje", 401) si las credenciales son inválidas
            - (None, "mensaje", 429) si la cuenta está bloqueada
        """
        # 1. Buscar usuario por email
        user = self.user_repository.find_by_email(request.email)
        
        if not user:
            # Registrar intento fallido (usuario no existe)
            self.login_attempt_repository.save_attempt(
                email=request.email,
                success=False,
                ip_address=ip_address
            )
            return None, "Credenciales inválidas", 401
        
        # 2. Verificar si la cuenta está bloqueada
        if user.is_locked():
            # Calcular tiempo restante de bloqueo
            remaining_time = (user.locked_until - datetime.now()).total_seconds()
            minutes_remaining = int(remaining_time // 60)
            
            # Registrar intento mientras está bloqueado
            self.login_attempt_repository.save_attempt(
                email=request.email,
                success=False,
                ip_address=ip_address
            )
            
            return (
                None,
                f"Cuenta bloqueada. Intenta nuevamente en {minutes_remaining} minutos.",
                429  # Too Many Requests
            )
        
        # 3. Verificar la contraseña
        password_is_valid = self.password_service.verify_password(
            plain_password=request.password,
            hashed_password=user.password_hash
        )
        
        if not password_is_valid:
            # Contraseña incorrecta
            # Incrementar contador de intentos fallidos
            user.increment_failed_attempts(max_attempts=self.MAX_FAILED_ATTEMPTS)
            
            # Actualizar en base de datos
            self.user_repository.update(user)
            
            # Registrar intento fallido
            self.login_attempt_repository.save_attempt(
                email=request.email,
                success=False,
                ip_address=ip_address
            )
            
            # Verificar si la cuenta se bloqueó
            if user.is_locked():
                return (
                    None,
                    f"Credenciales inválidas. Has superado el límite de {self.MAX_FAILED_ATTEMPTS} intentos. "
                    f"Tu cuenta ha sido bloqueada por {self.LOCK_DURATION_MINUTES} minutos.",
                    429  # Too Many Requests
                )
            
            # Calcular intentos restantes
            attempts_remaining = self.MAX_FAILED_ATTEMPTS - user.failed_login_attempts
            return (
                None,
                f"Credenciales inválidas. Te quedan {attempts_remaining} intentos antes de que tu cuenta sea bloqueada.",
                401
            )
        
        # 4. Login exitoso
        # Resetear intentos fallidos
        user.reset_failed_attempts()
        self.user_repository.update(user)
        
        # 5. Registrar intento exitoso
        self.login_attempt_repository.save_attempt(
            email=request.email,
            success=True,
            ip_address=ip_address
        )
        
        return user, None, 200
