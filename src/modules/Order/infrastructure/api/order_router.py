from fastapi import APIRouter, Depends, HTTPException, status
from src.modules.Order.application.usecases.order_usecases import OrderService
from src.modules.Order.application.dto.order_request import OrderRequestDTO, OrderStatusUpdateRequestDTO
from src.modules.Order.application.dto.order_response import OrderResponseDTO
from src.modules.User.infrastructure.api.auth_router import get_current_user
from typing import List

order_router = APIRouter(prefix="/api/orders", tags=["Orders"])

@order_router.post("/", response_model=OrderResponseDTO, status_code=status.HTTP_201_CREATED)
def create_order(request: OrderRequestDTO, user = Depends(get_current_user)):
    """Crear un nuevo pedido"""
    service = OrderService()
    return service.create_order(waiter_id=user["id"], request=request)

@order_router.put("/{order_id}/status", response_model=OrderResponseDTO)
def update_order_status(order_id: str, request: OrderStatusUpdateRequestDTO, user = Depends(get_current_user)):
    """
    Actualizar el estado de un pedido

    - **order_id**: ID del pedido
    - **new_status**: Nuevo estado (pending, preparing, ready, served, cancelled)
    - **cancellation_reason**: Requerido solo cuando new_status es 'cancelled'
    """
    try:
        service = OrderService()
        return service.update_order_status(order_id, request, user["id"])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@order_router.get("/{order_id}", response_model=OrderResponseDTO)
def get_order(order_id: str, user = Depends(get_current_user)):
    """Obtener detalles de un pedido específico"""
    service = OrderService()
    order = service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con ID {order_id} no encontrado"
        )
    return order

@order_router.get("/", response_model=List[OrderResponseDTO])
def get_orders(user = Depends(get_current_user)):
    """Obtener todos los pedidos del mesero actual"""
    service = OrderService()
    return service.get_orders_by_waiter(user["id"])