from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.Inventory.application.dto.inventory_request import (
    CreateInventoryItemRequestDTO,
    UpdateInventoryItemRequestDTO,
)
from src.modules.Inventory.application.dto.inventory_response import InventoryItemResponseDTO
from src.modules.Inventory.application.usecases.inventory_usecases import InventoryService
from src.modules.User.infrastructure.api.auth_router import get_current_user


inventory_router = APIRouter(prefix="/api/inventory", tags=["Inventario"])

ADMIN_ROLE_ID = "uuid-role-admin"


def _require_admin(user: dict) -> None:
    if user.get("role_id") != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden gestionar el inventario",
        )


@inventory_router.post("/", response_model=InventoryItemResponseDTO, status_code=status.HTTP_201_CREATED)
def create_inventory_item(request: CreateInventoryItemRequestDTO, user=Depends(get_current_user)):
    _require_admin(user)
    service = InventoryService()
    try:
        return service.create_item(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@inventory_router.get("/", response_model=List[InventoryItemResponseDTO])
def list_inventory_items(user=Depends(get_current_user)):
    _require_admin(user)
    service = InventoryService()
    return service.get_items()


@inventory_router.get("/{item_id}", response_model=InventoryItemResponseDTO)
def get_inventory_item(item_id: str, user=Depends(get_current_user)):
    _require_admin(user)
    service = InventoryService()
    item = service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Articulo con ID {item_id} no encontrado",
        )
    return item


@inventory_router.put("/{item_id}", response_model=InventoryItemResponseDTO)
def update_inventory_item(
    item_id: str,
    request: UpdateInventoryItemRequestDTO,
    user=Depends(get_current_user),
):
    _require_admin(user)
    service = InventoryService()
    try:
        return service.update_item(item_id, request)
    except ValueError as e:
        message = str(e)
        error_status = status.HTTP_404_NOT_FOUND if "no encontrado" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=error_status, detail=message)


@inventory_router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_inventory_item(item_id: str, user=Depends(get_current_user)):
    _require_admin(user)
    service = InventoryService()
    try:
        service.delete_item(item_id)
        return {"message": "Articulo eliminado correctamente", "item_id": item_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
