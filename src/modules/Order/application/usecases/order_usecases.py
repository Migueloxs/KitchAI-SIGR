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
        order_number = f"ORD-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        
        items = []
        total_amount = 0.0
        
        for i in request.items:
            subtotal = i.quantity * i.unit_price
            total_amount += subtotal
            
            items.append(
                OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    menu_item_id=i.menu_item_id,
                    menu_item_name=i.menu_item_name,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                    subtotal=subtotal,
                    special_notes=i.special_notes,
                    created_at=datetime.now()
                )
            )
            
        tax_amount = total_amount * 0.18 # Example tax rate
        final_amount = total_amount + tax_amount
        
        order = Order(
            id=order_id,
            order_number=order_number,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            table_number=request.table_number,
            status="pending",
            total_amount=total_amount,
            tax_amount=tax_amount,
            final_amount=final_amount,
            special_instructions=request.special_instructions,
            waiter_id=waiter_id,
            items=items,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return self.repo.create(order)

    def update_order_status(self, order_id: str, status: str):
        return self.repo.update_status(order_id, status)