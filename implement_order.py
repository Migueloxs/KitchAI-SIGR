import os

files = {
    'src/modules/Order/domain/entities/order.py': '''
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.modules.Order.domain.entities.order_item import OrderItem

class Order(BaseModel):
    id: str
    waiter_id: str
    table_number: int
    status: str # PENDING, PREPARING, SERVED, CANCELLED
    total: float
    items: List[OrderItem] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
''',
    'src/modules/Order/domain/entities/order_item.py': '''
from pydantic import BaseModel

class OrderItem(BaseModel):
    id: str
    order_id: str
    product_id: str
    quantity: int
    price: float
    subtotal: float
    notes: str = ""
''',
    'src/modules/Order/application/dto/order_request.py': '''
from pydantic import BaseModel
from typing import List, Optional

class OrderItemRequestDTO(BaseModel):
    product_id: str
    quantity: int
    price: float
    notes: Optional[str] = ""

class OrderRequestDTO(BaseModel):
    table_number: int
    items: List[OrderItemRequestDTO]
''',
    'src/modules/Order/application/dto/order_response.py': '''
from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemResponseDTO(BaseModel):
    id: str
    product_id: str
    quantity: int
    price: float
    subtotal: float
    notes: str

class OrderResponseDTO(BaseModel):
    id: str
    waiter_id: str
    table_number: int
    status: str
    total: float
    items: List[OrderItemResponseDTO]
    created_at: datetime
    updated_at: datetime
''',
    'src/modules/Order/domain/repositories/order_repository_interface.py': '''
from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.Order.domain.entities.order import Order

class IOrderRepository(ABC):
    @abstractmethod
    def create(self, order: Order) -> Order: pass
    
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]: pass
    
    @abstractmethod
    def get_all(self, waiter_id: Optional[str] = None) -> List[Order]: pass
    
    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool: pass
''',
    'src/modules/Order/infrastructure/repositories/order_repository.py': '''
from typing import List, Optional
from src.modules.Order.domain.entities.order import Order
from src.modules.Order.domain.entities.order_item import OrderItem
from src.modules.Order.domain.repositories.order_repository_interface import IOrderRepository
from src.shared.infrastructure.database.turso_connection import get_turso_client

class OrderRepository(IOrderRepository):
    def __init__(self):
        self.client = get_turso_client()

    def create(self, order: Order) -> Order:
        self.client.execute(
            "INSERT INTO orders (id, waiter_id, table_number, status, total, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [order.id, order.waiter_id, order.table_number, order.status, order.total, order.created_at.isoformat(), order.updated_at.isoformat()]
        )
        for item in order.items:
            self.client.execute(
                "INSERT INTO order_items (id, order_id, product_id, quantity, price, subtotal, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [item.id, order.id, item.product_id, item.quantity, item.price, item.subtotal, item.notes]
            )
        return order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        # simplified
        return None

    def get_all(self, waiter_id: Optional[str] = None) -> List[Order]:
        return []

    def update_status(self, order_id: str, status: str) -> bool:
        self.client.execute("UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?", [status, order_id])
        return True
''',
    'src/modules/Order/application/usecases/order_usecases.py': '''
from src.modules.Order.infrastructure.repositories.order_repository import OrderRepository
from src.modules.Order.application.dto.order_request import OrderRequestDTO
from src.modules.Order.domain.entities.order import Order
from src.modules.Order.domain.entities.order_item import OrderItem
import uuid
from datetime import datetime

class OrderService:
    def __init__(self):
        self.repo = OrderRepository()

    def create_order(self, waiter_id: str, request: OrderRequestDTO) -> Order:
        order_id = str(uuid.uuid4())
        total = sum(i.quantity * i.price for i in request.items)
        items = [
            OrderItem(id=str(uuid.uuid4()), order_id=order_id, product_id=i.product_id, quantity=i.quantity, price=i.price, subtotal=i.quantity * i.price, notes=i.notes or "")
            for i in request.items
        ]
        order = Order(id=order_id, waiter_id=waiter_id, table_number=request.table_number, status="PENDING", total=total, items=items)
        return self.repo.create(order)

    def update_order_status(self, order_id: str, status: str):
        return self.repo.update_status(order_id, status)
''',
    'src/modules/Order/infrastructure/api/order_router.py': '''
from fastapi import APIRouter, Depends, HTTPException
from src.modules.Order.application.usecases.order_usecases import OrderService
from src.modules.Order.application.dto.order_request import OrderRequestDTO
# Assuming some get_current_user logic exists in User
# from src.modules.User.domain.services.auth_service import get_current_user

order_router = APIRouter(prefix="/orders", tags=["Orders"])

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
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip())
