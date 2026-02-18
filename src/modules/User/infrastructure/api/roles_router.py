"""
Router de gestión de roles - Endpoints para administrar roles y permisos.
Define los endpoints HTTP para listar, asignar roles y ver permisos.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.modules.User.application.dto.permission_response import (
    PermissionResponse,
    RolePermissionsResponse
)
from src.modules.User.application.dto.change_role_request import ChangeRoleRequest
from src.modules.User.application.dto.user_response import UserResponse
from src.modules.User.application.usecases.update_user_role import UpdateUserRoleUseCase
from src.modules.User.infrastructure.repositories.user_repository import UserRepository
from src.modules.User.infrastructure.repositories.role_repository import RoleRepository
from src.modules.User.infrastructure.repositories.permission_repository import PermissionRepository


# Crear router para endpoints de roles
router = APIRouter(
    prefix="/api/roles",
    tags=["Roles y Permisos"],
    responses={
        401: {"description": "No autorizado"},
        404: {"description": "Recurso no encontrado"},
        400: {"description": "Solicitud inválida"}
    }
)

# Inicializar repositorios
user_repository = UserRepository()
role_repository = RoleRepository()
permission_repository = PermissionRepository()


@router.get(
    "/",
    response_model=List[dict],
    summary="Listar todos los roles disponibles",
    description="Obtiene la lista de todos los roles definidos en el sistema"
)
async def list_roles():
    """
    Obtiene todos los roles disponibles en el sistema.

    Returns:
        Lista de roles con sus detalles
    """
    try:
        roles = role_repository.find_all()
        return [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "created_at": role.created_at
            }
            for role in roles
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener roles: {str(e)}"
        )


@router.get(
    "/{role_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="Obtener permisos de un rol",
    description="Obtiene todos los permisos asociados a un rol específico"
)
async def get_role_permissions(role_id: str):
    """
    Obtiene todos los permisos asignados a un rol.

    Args:
        role_id: ID del rol

    Returns:
        Información del rol con sus permisos
    """
    try:
        role = role_repository.find_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol '{role_id}' no existe"
            )

        permissions = permission_repository.find_by_role_id(role_id)
        permission_responses = [
            PermissionResponse(
                id=perm.id,
                name=perm.name,
                description=perm.description,
                created_at=perm.created_at
            )
            for perm in permissions
        ]

        return RolePermissionsResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=permission_responses
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener permisos del rol: {str(e)}"
        )


@router.get(
    "/permissions/",
    response_model=List[PermissionResponse],
    summary="Listar todos los permisos",
    description="Obtiene la lista de todos los permisos disponibles en el sistema"
)
async def list_permissions():
    """
    Obtiene todos los permisos disponibles en el sistema.

    Returns:
        Lista de permisos
    """
    try:
        perms = permission_repository.find_all()
        return [
            PermissionResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                created_at=p.created_at
            )
            for p in perms
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener permisos: {str(e)}"
        )


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="Cambiar rol de un usuario",
    description="Asigna un nuevo rol a un usuario existente",
    responses={
        200: {
            "description": "Rol actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Juan Pérez",
                        "email": "juan.perez@example.com",
                        "phone": "+18295551234",
                        "role_id": "uuid-role-admin",
                        "created_at": "2026-02-17T10:30:00"
                    }
                }
            }
        },
        400: {"description": "Rol inválido o no existe"},
        404: {"description": "Usuario no encontrado"}
    }
)
async def update_user_role(user_id: str, request: ChangeRoleRequest):
    """
    Actualiza el rol de un usuario existente.

    Args:
        user_id: ID del usuario
        request: DTO con el nuevo rol

    Returns:
        Datos del usuario actualizado

    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si el rol no existe
        HTTPException 500: Si hay error en el servidor
    """
    try:
        use_case = UpdateUserRoleUseCase(
            user_repository=user_repository,
            role_repository=role_repository
        )

        user, error = use_case.execute(user_id, request)

        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role_id=user.role_id,
            created_at=user.created_at
        )

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail=error_msg
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al cambiar rol de usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el rol del usuario"
        )
