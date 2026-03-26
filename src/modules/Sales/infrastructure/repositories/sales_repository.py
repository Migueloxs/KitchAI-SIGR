from datetime import datetime
from typing import List, Optional
import uuid

from src.modules.Sales.domain.entities.sale import Sale, SaleItem
from src.modules.Sales.domain.repositories.sales_repository_interface import SalesRepositoryInterface
from src.shared.infrastructure.database.turso_connection import get_turso_client


class SalesRepository(SalesRepositoryInterface):
    def __init__(self):
        self.client = get_turso_client()

    def create(self, sale: Sale) -> Sale:
        sale_id = sale.id or str(uuid.uuid4())
        
        # Insertar venta
        self.client.execute(
            """
            INSERT INTO sales (
                id, order_id, order_number, customer_name, waiter_id,
                payment_method, total_amount, tax_amount, discount_amount, final_amount,
                items_count, sale_date, registered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                sale_id,
                sale.order_id,
                sale.order_number,
                sale.customer_name,
                sale.waiter_id,
                sale.payment_method,
                sale.total_amount,
                sale.tax_amount,
                sale.discount_amount,
                sale.final_amount,
                sale.items_count,
                sale.sale_date,
                sale.registered_at.isoformat(),
            ],
        )

        # Insertar items de la venta
        for item in sale.items:
            self.client.execute(
                """
                INSERT INTO sale_items (
                    id, sale_id, menu_item_id, menu_item_name, quantity, unit_price, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    item.id,
                    sale_id,
                    item.menu_item_id,
                    item.menu_item_name,
                    item.quantity,
                    item.unit_price,
                    item.subtotal,
                ],
            )

        return sale.model_copy(update={"id": sale_id})

    def get_by_id(self, sale_id: str) -> Optional[Sale]:
        result = self.client.execute(
            """
            SELECT id, order_id, order_number, customer_name, waiter_id,
                   payment_method, total_amount, tax_amount, discount_amount, final_amount,
                   items_count, sale_date, registered_at
            FROM sales
            WHERE id = ?
            """,
            [sale_id],
        )

        if not result.rows:
            return None

        return self._map_to_entity(result.rows[0])

    def get_by_order_id(self, order_id: str) -> Optional[Sale]:
        result = self.client.execute(
            """
            SELECT id, order_id, order_number, customer_name, waiter_id,
                   payment_method, total_amount, tax_amount, discount_amount, final_amount,
                   items_count, sale_date, registered_at
            FROM sales
            WHERE order_id = ?
            """,
            [order_id],
        )

        if not result.rows:
            return None

        return self._map_to_entity(result.rows[0])

    def get_all(self) -> List[Sale]:
        result = self.client.execute(
            """
            SELECT id, order_id, order_number, customer_name, waiter_id,
                   payment_method, total_amount, tax_amount, discount_amount, final_amount,
                   items_count, sale_date, registered_at
            FROM sales
            ORDER BY registered_at DESC
            """
        )

        return [self._map_to_entity(row) for row in result.rows]

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Sale]:
        result = self.client.execute(
            """
            SELECT id, order_id, order_number, customer_name, waiter_id,
                   payment_method, total_amount, tax_amount, discount_amount, final_amount,
                   items_count, sale_date, registered_at
            FROM sales
            WHERE sale_date >= ? AND sale_date <= ?
            ORDER BY registered_at DESC
            """,
            [start_date, end_date],
        )

        return [self._map_to_entity(row) for row in result.rows]

    def get_by_waiter(self, waiter_id: str) -> List[Sale]:
        result = self.client.execute(
            """
            SELECT id, order_id, order_number, customer_name, waiter_id,
                   payment_method, total_amount, tax_amount, discount_amount, final_amount,
                   items_count, sale_date, registered_at
            FROM sales
            WHERE waiter_id = ?
            ORDER BY registered_at DESC
            """,
            [waiter_id],
        )

        return [self._map_to_entity(row) for row in result.rows]

    def get_summary_by_date(self, date: str) -> dict:
        result = self.client.execute(
            """
            SELECT 
                COUNT(*) as total_sales,
                SUM(final_amount) as total_revenue,
                SUM(tax_amount) as total_tax,
                SUM(discount_amount) as total_discount
            FROM sales
            WHERE sale_date = ?
            """,
            [date],
        )

        if not result.rows:
            return {
                "date": date,
                "total_sales": 0,
                "total_revenue": 0.0,
                "total_tax": 0.0,
                "total_discount": 0.0,
            }

        row = result.rows[0]
        return {
            "date": date,
            "total_sales": row[0] or 0,
            "total_revenue": float(row[1] or 0.0),
            "total_tax": float(row[2] or 0.0),
            "total_discount": float(row[3] or 0.0),
        }

    def get_summary_by_waiter(self, start_date: str, end_date: str) -> List[dict]:
        result = self.client.execute(
            """
            SELECT 
                waiter_id,
                COUNT(*) as sales_count,
                SUM(final_amount) as total_revenue
            FROM sales
            WHERE sale_date >= ? AND sale_date <= ?
            GROUP BY waiter_id
            ORDER BY total_revenue DESC
            """,
            [start_date, end_date],
        )

        return [
            {
                "waiter_id": row[0],
                "sales_count": row[1],
                "total_revenue": float(row[2] or 0.0),
            }
            for row in result.rows
        ]

    def get_summary_by_payment_method(self, start_date: str, end_date: str) -> List[dict]:
        result = self.client.execute(
            """
            SELECT 
                payment_method,
                COUNT(*) as sales_count,
                SUM(final_amount) as total_revenue
            FROM sales
            WHERE sale_date >= ? AND sale_date <= ?
            GROUP BY payment_method
            ORDER BY total_revenue DESC
            """,
            [start_date, end_date],
        )

        return [
            {
                "payment_method": row[0],
                "sales_count": row[1],
                "total_revenue": float(row[2] or 0.0),
            }
            for row in result.rows
        ]

    def exists_for_order(self, order_id: str) -> bool:
        result = self.client.execute(
            "SELECT COUNT(*) FROM sales WHERE order_id = ?", [order_id]
        )
        return result.rows[0][0] > 0

    def _map_to_entity(self, row) -> Sale:
        sale_id = row[0]

        # Obtener items de la venta
        items_result = self.client.execute(
            """
            SELECT id, sale_id, menu_item_id, menu_item_name, quantity, unit_price, subtotal
            FROM sale_items
            WHERE sale_id = ?
            """,
            [sale_id],
        )

        items = [
            SaleItem(
                id=item_row[0],
                sale_id=item_row[1],
                menu_item_id=item_row[2],
                menu_item_name=item_row[3],
                quantity=item_row[4],
                unit_price=item_row[5],
                subtotal=item_row[6],
            )
            for item_row in items_result.rows
        ]

        return Sale(
            id=row[0],
            order_id=row[1],
            order_number=row[2],
            customer_name=row[3],
            waiter_id=row[4],
            payment_method=row[5],
            total_amount=row[6],
            tax_amount=row[7],
            discount_amount=row[8],
            final_amount=row[9],
            items_count=row[10],
            sale_date=row[11],
            registered_at=datetime.fromisoformat(row[12])
            if isinstance(row[12], str)
            else row[12],
            items=items,
        )
