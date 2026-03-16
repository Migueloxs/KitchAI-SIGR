from typing import List, Optional
from src.modules.Order.domain.repositories.order_repository_interface import IOrderRepository
from src.modules.Order.domain.entities.order import Order, OrderStatus
from src.modules.Order.domain.entities.order_item import OrderItem
from src.shared.infrastructure.database.turso_connection import get_turso_client
from datetime import datetime

class OrderRepository(IOrderRepository):
    def __init__(self):
        self.db = get_turso_client()

    def create(self, order: Order) -> Order:
        # Insertar pedido
        self.db.execute("""
            INSERT INTO orders (
                id, order_number, customer_name, customer_phone, table_number,
                status, total_amount, tax_amount, discount_amount, final_amount,
                payment_status, payment_method, special_instructions, waiter_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            order.id, order.order_number, order.customer_name, order.customer_phone,
            order.table_number, order.status.value, order.total_amount, order.tax_amount,
            order.discount_amount, order.final_amount, order.payment_status,
            order.payment_method, order.special_instructions, order.waiter_id,
            order.created_at.isoformat(), order.updated_at.isoformat()
        ])

        # Insertar items del pedido
        for item in order.items:
            self.db.execute("""
                INSERT INTO order_items (
                    id, order_id, menu_item_id, menu_item_name, quantity,
                    unit_price, subtotal, special_notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                item.id, order.id, item.menu_item_id, item.menu_item_name,
                item.quantity, item.unit_price, item.subtotal,
                item.special_notes, item.created_at.isoformat()
            ])

        return order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        # Obtener pedido
        order_result = self.db.execute("""
            SELECT id, order_number, customer_name, customer_phone, table_number,
                   status, total_amount, tax_amount, discount_amount, final_amount,
                   payment_status, payment_method, special_instructions, waiter_id,
                   cancelled_by, cancelled_at, cancellation_reason,
                   created_at, updated_at, preparation_started_at, ready_at,
                   completed_at, preparation_time, total_time
            FROM orders WHERE id = ?
        """, [order_id]).fetchone()

        if not order_result:
            return None

        # Obtener items del pedido
        items_result = self.db.execute("""
            SELECT id, menu_item_id, menu_item_name, quantity, unit_price,
                   subtotal, special_notes, created_at
            FROM order_items WHERE order_id = ? ORDER BY created_at
        """, [order_id]).fetchall()

        # Convertir items
        items = []
        for item_row in items_result:
            items.append(OrderItem(
                id=item_row[0],
                order_id=order_id,
                menu_item_id=item_row[1],
                menu_item_name=item_row[2],
                quantity=item_row[3],
                unit_price=item_row[4],
                subtotal=item_row[5],
                special_notes=item_row[6],
                created_at=datetime.fromisoformat(item_row[7])
            ))

        # Convertir timestamps
        def parse_datetime(value):
            return datetime.fromisoformat(value) if value else None

        return Order(
            id=order_result[0],
            order_number=order_result[1],
            customer_name=order_result[2],
            customer_phone=order_result[3],
            table_number=order_result[4],
            status=OrderStatus(order_result[5]),
            total_amount=order_result[6],
            tax_amount=order_result[7],
            discount_amount=order_result[8],
            final_amount=order_result[9],
            payment_status=order_result[10],
            payment_method=order_result[11],
            special_instructions=order_result[12],
            waiter_id=order_result[13],
            cancelled_by=order_result[14],
            cancelled_at=parse_datetime(order_result[15]),
            cancellation_reason=order_result[16],
            created_at=parse_datetime(order_result[17]),
            updated_at=parse_datetime(order_result[18]),
            preparation_started_at=parse_datetime(order_result[19]),
            ready_at=parse_datetime(order_result[20]),
            completed_at=parse_datetime(order_result[21]),
            preparation_time=order_result[22],
            total_time=order_result[23],
            items=items
        )

    def get_all(self, waiter_id: Optional[str] = None) -> List[Order]:
        query = """
            SELECT id, order_number, customer_name, customer_phone, table_number,
                   status, total_amount, tax_amount, discount_amount, final_amount,
                   payment_status, payment_method, special_instructions, waiter_id,
                   cancelled_by, cancelled_at, cancellation_reason,
                   created_at, updated_at, preparation_started_at, ready_at,
                   completed_at, preparation_time, total_time
            FROM orders
        """
        params = []

        if waiter_id:
            query += " WHERE waiter_id = ?"
            params.append(waiter_id)

        query += " ORDER BY created_at DESC"

        results = self.db.execute(query, params).fetchall()
        orders = []

        for row in results:
            # Obtener items para cada pedido
            items_result = self.db.execute("""
                SELECT id, menu_item_id, menu_item_name, quantity, unit_price,
                       subtotal, special_notes, created_at
                FROM order_items WHERE order_id = ? ORDER BY created_at
            """, [row[0]]).fetchall()

            items = []
            for item_row in items_result:
                items.append(OrderItem(
                    id=item_row[0],
                    order_id=row[0],
                    menu_item_id=item_row[1],
                    menu_item_name=item_row[2],
                    quantity=item_row[3],
                    unit_price=item_row[4],
                    subtotal=item_row[5],
                    special_notes=item_row[6],
                    created_at=datetime.fromisoformat(item_row[7])
                ))

            def parse_datetime(value):
                return datetime.fromisoformat(value) if value else None

            orders.append(Order(
                id=row[0],
                order_number=row[1],
                customer_name=row[2],
                customer_phone=row[3],
                table_number=row[4],
                status=OrderStatus(row[5]),
                total_amount=row[6],
                tax_amount=row[7],
                discount_amount=row[8],
                final_amount=row[9],
                payment_status=row[10],
                payment_method=row[11],
                special_instructions=row[12],
                waiter_id=row[13],
                cancelled_by=row[14],
                cancelled_at=parse_datetime(row[15]),
                cancellation_reason=row[16],
                created_at=parse_datetime(row[17]),
                updated_at=parse_datetime(row[18]),
                preparation_started_at=parse_datetime(row[19]),
                ready_at=parse_datetime(row[20]),
                completed_at=parse_datetime(row[21]),
                preparation_time=row[22],
                total_time=row[23],
                items=items
            ))

        return orders

    def update_status(self, order_id: str, status: str) -> bool:
        """Método legacy para compatibilidad"""
        self.db.execute(
            "UPDATE orders SET status = ?, updated_at = ? WHERE id = ?",
            [status, datetime.now().isoformat(), order_id]
        )
        return True

    def update_status_with_details(self, order: Order) -> Order:
        """Actualiza el estado del pedido con todos los campos adicionales"""
        self.db.execute("""
            UPDATE orders SET
                status = ?, updated_at = ?, preparation_started_at = ?,
                ready_at = ?, completed_at = ?, preparation_time = ?,
                total_time = ?, cancelled_by = ?, cancelled_at = ?,
                cancellation_reason = ?, payment_status = ?
            WHERE id = ?
        """, [
            order.status.value,
            order.updated_at.isoformat() if order.updated_at else None,
            order.preparation_started_at.isoformat() if order.preparation_started_at else None,
            order.ready_at.isoformat() if order.ready_at else None,
            order.completed_at.isoformat() if order.completed_at else None,
            order.preparation_time,
            order.total_time,
            order.cancelled_by,
            order.cancelled_at.isoformat() if order.cancelled_at else None,
            order.cancellation_reason,
            order.payment_status,
            order.id
        ])
        return order
