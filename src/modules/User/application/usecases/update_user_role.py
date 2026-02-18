"""
Caso de Uso: Cambiar el rol de un usuario.
Implementa la lógica de negocio para actualizar el rol de un usuario existente.
"""
from src.modules.User.domain.entities.user import User
from src.modules.User.infrastructure.repositories.user_repository import UserRepository
from src.modules.User.infrastructure.repositories.role_repository import RoleRepository
from src.modules.User.application.dto.change_role_request import ChangeRoleRequest


class UpdateUserRoleUseCase:
    """
    Caso de uso para actualizar el rol de un usuario existente.

    Flujo:
    1. Buscar el usuario por ID
    2. Validar que exista el nuevo rol
    3. Actualizar el rol del usuario
    4. Guardar en la base de datos

    Attributes:
        user_repository: Repositorio de usuarios
        role_repository: Repositorio de roles
    """

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository
    ):
        """Inicializar el caso de uso."""
        self.user_repository = user_repository
        self.role_repository = role_repository

    def execute(self, user_id: str, request: ChangeRoleRequest) -> tuple[User, str | None]:
        """
        Ejecutar la actualización del rol del usuario.

        Args:
            user_id: ID del usuario a actualizar
            request: DTO con el nuevo rol

        Returns:
            Tupla con (Usuario actualizado, Mensaje de error si aplica)

        Raises:
            ValueError: Si hay errores de validación
        """
        # 1. Buscar el usuario
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"El usuario '{user_id}' no existe en el sistema")

        # 2. Validar que el nuevo rol exista
        new_role = self.role_repository.find_by_name(request.role)
        if not new_role:
            raise ValueError(f"El rol '{request.role}' no existe en el sistema")

        # 3. Actualizar el rol del usuario
        user.role_id = new_role.id

        # 4. Guardar en la base de datos
        try:
            updated_user = self.user_repository.update(user)
            return updated_user, None
        except Exception as e:
            print(f"❌ Error al actualizar rol del usuario: {str(e)}")
            raise Exception("Error al actualizar el rol del usuario.")
