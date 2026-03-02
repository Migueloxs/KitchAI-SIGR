from fastapi import APIRouter, Depends, HTTPException
from src.modules.Order.application.usecases.order_usecases import OrderService
from src.modules.Order.application.dto.order_request import OrderRequestDTO
# Assuming some get_current_user logic exists in User
# from src.modules.User.domain.services.auth_service import get_current_user

order_router = APIRouter(prefix="/api/orders", tags=["Orders"])

# Mocked user dep for brevity
def get_current_user():
    return {"id": "test_waiter_id"}

@order_router.post("/")
def create_order(request: OrderRequestDTO, user = Depends(get_current_user)):
    service = OrderService()
    return service.create_order(waiter_id=user["id"], request=request)
    
@order_router.patch("/{order_id}/status")
def update_status(order_id: str, status: str, user = Depends(get_current_user)):
    service = OrderService()
    return {"success": service.update_order_status(order_id, status)}