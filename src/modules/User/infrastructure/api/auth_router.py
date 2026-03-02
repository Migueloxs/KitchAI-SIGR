"""
Router de autenticación - Endpoints para registro y login.
Define los endpoints HTTP para el módulo de autenticación.
"""
from fastapi import APIRouter, HTTPException, Request, status
from typing import Optional

from src.modules.User.application.dto.register_request import RegisterRequest
from src.modules.User.application.dto.login_request import LoginRequest
from src.modules.User.application.dto.user_response import UserResponse
from src.modules.User.application.dto.auth_response import AuthResponse
from src.modules.User.application.usecases.register_user import RegisterUserUseCase
from src.modules.User.application.usecases.login_user import LoginUserUseCase
from src.modules.User.infrastructure.repositories.user_repository import UserRepository
from src.modules.User.infrastructure.repositories.role_repository import RoleRepository
from src.modules.User.infrastructure.repositories.login_attempt_repository import LoginAttemptRepository
from src.modules.User.infrastructure.repositories.permission_repository import PermissionRepository
from src.modules.User.domain.services.password_service import PasswordService
from src.modules.User.domain.services.auth_service import AuthService
from src.shared.infrastructure.config.settings import settings


# Crear el router con prefijo /api/auth
router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"],
    responses={
        401: {"description": "No autorizado"},
        429: {"description": "Demasiados intentos - Cuenta bloqueada"}
    }
)

# Inicializar servicios y repositorios
password_service = PasswordService()
auth_service = AuthService(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)
user_repository = UserRepository()
role_repository = RoleRepository()
login_attempt_repository = LoginAttemptRepository()


def get_client_ip(request: Request) -> Optional[str]:
    """
    Obtener la dirección IP del cliente.
    
    Args:
        request: Objeto Request de FastAPI
    
    Returns:
        Dirección IP del cliente
    """
    # Intentar obtener IP de headers (si hay proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    
    # Obtener IP directa
    return request.client.host if request.client else None


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="""
    Crea un nuevo usuario en el sistema con las credenciales proporcionadas.
    Si no se incluye el campo `role`, se asignará el rol **waiter** por defecto.
    
    **Criterios de Aceptación:**
    - CA1: Acepta: Nombre, email, teléfono, contraseña, rol (opcional)
    - CA2: La contraseña se almacena con hash seguro (bcrypt)
    - Retorna código 201 con los datos del usuario (sin contraseña)
    
    **Validaciones:**
    - El email debe ser único en el sistema
    - La contraseña debe cumplir requisitos de seguridad:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un carácter especial (!@#$%^&*(),.?":{}|<>)
    - El rol, si se provee, debe ser: admin, employee o waiter
    """,
    responses={
        201: {
            "description": "Usuario creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Juan Pérez",
                        "email": "juan.perez@example.com",
                        "phone": "+18295551234",
                        "role_id": "uuid-role-waiter",
                        "created_at": "2026-02-17T10:30:00"
                    }
                }
            }
        },
        400: {"description": "Datos inválidos o email ya registrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def register(request_data: RegisterRequest):
    """
    Endpoint POST /api/auth/register
    Registra un nuevo usuario en el sistema.
    
    Args:
        request_data: Datos del usuario a registrar
    
    Returns:
        Usuario creado (sin contraseña)
    
    Raises:
        HTTPException 400: Si hay errores de validación
        HTTPException 500: Si hay errores en el servidor
    """
    try:
        # Crear instancia del caso de uso
        register_use_case = RegisterUserUseCase(
            user_repository=user_repository,
            role_repository=role_repository,
            password_service=password_service
        )
        
        # Ejecutar el caso de uso
        user, error = register_use_case.execute(request_data)
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Mapear a DTO de respuesta
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role_id=user.role_id,
            created_at=user.created_at
        )
        
    except ValueError as e:
        # Errores de validación de negocio
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        # Errores inesperados
        print(f"❌ Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el registro. Por favor, intente nuevamente."
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="""
    Autentica un usuario con sus credenciales y retorna un token JWT.
    
    **Criterios de Aceptación:**
    - CA3: Si falla 5 veces consecutivas, la cuenta se bloquea por 15 minutos
    - CA3: Retorna error 429 (Too Many Requests) cuando está bloqueada
    - CA2: Verifica la contraseña contra el hash almacenado (nunca en texto plano)
    
    **Seguridad:**
    - Registra todos los intentos de login (exitosos y fallidos)
    - Bloqueo automático tras 5 intentos fallidos consecutivos
    - Contador de intentos se resetea tras login exitoso
    """,
    responses={
        200: {
            "description": "Login exitoso - Retorna token JWT",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "name": "Juan Pérez",
                            "email": "juan.perez@example.com",
                            "phone": "+18295551234",
                            "role_id": "uuid-role-waiter",
                            "created_at": "2026-02-17T10:30:00"
                        }
                    }
                }
            }
        },
        401: {"description": "Credenciales inválidas"},
        429: {"description": "Cuenta bloqueada - Demasiados intentos fallidos"},
        500: {"description": "Error interno del servidor"}
    }
)
async def login(request_data: LoginRequest, request: Request):
    """
    Endpoint POST /api/auth/login
    Autentica un usuario y retorna un token JWT.
    
    Args:
        request_data: Credenciales del usuario
        request: Objeto Request para obtener IP
    
    Returns:
        Token JWT y datos del usuario
    
    Raises:
        HTTPException 401: Si las credenciales son inválidas
        HTTPException 429: Si la cuenta está bloqueada
        HTTPException 500: Si hay errores en el servidor
    """
    try:
        # Obtener IP del cliente para auditoría
        client_ip = get_client_ip(request)
        
        # Crear instancia del caso de uso
        login_use_case = LoginUserUseCase(
            user_repository=user_repository,
            login_attempt_repository=login_attempt_repository,
            password_service=password_service
        )
        
        # Ejecutar el caso de uso
        user, error, status_code = login_use_case.execute(
            request=request_data,
            ip_address=client_ip
        )
        
        # Verificar errores
        if error:
            raise HTTPException(
                status_code=status_code,
                detail=error
            )
        
        # Generar token JWT
        access_token = auth_service.generate_token(
            user_id=user.id,
            email=user.email,
            role_id=user.role_id,
            expires_in_minutes=settings.JWT_EXPIRATION_MINUTES
        )
        
        # Mapear a DTO de respuesta
        user_response = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role_id=user.role_id,
            created_at=user.created_at
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        # Errores inesperados
        print(f"❌ Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el login. Por favor, intente nuevamente."
        )
