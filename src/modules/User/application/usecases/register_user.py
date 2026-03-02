"""
Caso de Uso: Registrar un nuevo usuario en el sistema.
Implementa toda la lógica de negocio para el registro de usuarios.
"""
import uuid
from datetime import datetime

from src.modules.User.domain.entities.user import User
from src.modules.User.domain.value_objects.email import Email
from src.modules.User.domain.value_objects.password import Password
from src.modules.User.domain.services.password_service import PasswordService
from src.modules.User.infrastructure.repositories.user_repository import UserRepository
from src.modules.User.infrastructure.repositories.role_repository import RoleRepository
from src.modules.User.application.dto.register_request import RegisterRequest


class RegisterUserUseCase:
    """
    Caso de uso para registrar un nuevo usuario.
    
    Flujo:
    1. Validar que el email no esté registrado
    2. Validar que el rol exista
    3. Validar la contraseña contra las reglas de seguridad
    4. Hashear la contraseña
    5. Crear la entidad User
    6. Guardar en la base de datos
    
    Attributes:
        user_repository: Repositorio de usuarios
        role_repository: Repositorio de roles
        password_service: Servicio para hashear contraseñas
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        password_service: PasswordService
    ):
        """
        Inicializar el caso de uso con sus dependencias.
        
        Args:
            user_repository: Repositorio de usuarios
            role_repository: Repositorio de roles
            password_service: Servicio de contraseñas
        """
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.password_service = password_service
    
    def execute(self, request: RegisterRequest) -> tuple[User, str | None]:
        """
        Ejecutar el caso de uso de registro.
        
        Args:
            request: DTO con los datos del usuario a registrar
        
        Returns:
            Tupla con (Usuario creado, Mensaje de error si aplica)
        
        Raises:
            ValueError: Si hay errores de validación
            Exception: Si hay errores en la base de datos
        """
        # 1. Validar que el email no esté registrado
        email = Email(request.email)
        if self.user_repository.email_exists(email.value):
            raise ValueError(f"El email {email.value} ya está registrado en el sistema")
        
        # 2. Determinar rol (si no se especificó, usamos waiter por defecto)
        requested_role = request.role if request.role is not None else 'waiter'
        role = self.role_repository.find_by_name(requested_role)
        if not role:
            raise ValueError(f"El rol '{requested_role}' no existe en el sistema")
        
        # 3. Validar la contraseña contra las reglas de seguridad
        # El value object Password ya valida las reglas
        password = Password(request.password)
        
        # 4. Hashear la contraseña
        password_hash = self.password_service.hash_password(password.value)
        
        # 5. Crear la entidad User
        user = User(
            id=str(uuid.uuid4()),
            name=request.name,
            email=email.value,
            phone=request.phone,
            password_hash=password_hash,
            role_id=role.id,
            failed_login_attempts=0,
            locked_until=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 6. Guardar en la base de datos
        try:
            saved_user = self.user_repository.save(user)
            return saved_user, None
        except Exception as e:
            print(f"❌ Error al guardar usuario: {str(e)}")
            raise Exception("Error al crear el usuario. Por favor, intente nuevamente.")
