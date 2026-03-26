"""Financial Reports Repository - Detailed queries for reporting"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta

from src.shared.infrastructure.database.turso_connection import get_turso_client
from src.modules.User.infrastructure.repositories.user_repository import UserRepository


class FinancialReportsRepository:
    """Repository for advanced financial reporting queries"""

    def __init__(self):
        self.client = get_turso_client()
        self.user_repo = UserRepository()

    # ==================== CA1: Sales Data by Date ====================

    def get_sales_by_date_range_detailed(
        self, start_date: str, end_date: str
    ) -> List[Dict]:
        """Get detailed sales data filtered by date range"""
        result = self.client.execute(
            """
            SELECT
                s.id, s.order_number, s.customer_name, s.waiter_id,
                s.payment_method, s.total_amount, s.tax_amount,
                s.discount_amount, s.final_amount, s.items_count,
                s.sale_date, s.registered_at
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ?
            ORDER BY s.sale_date DESC, s.registered_at DESC
            """,
            [start_date, end_date],
        )

        sales = []
        for row in result.rows:
            sales.append({
                "id": row[0],
                "order_number": row[1],
                "customer_name": row[2],
                "waiter_id": row[3],
                "payment_method": row[4],
                "total_amount": float(row[5]),
                "tax_amount": float(row[6]),
                "discount_amount": float(row[7]),
                "final_amount": float(row[8]),
                "items_count": row[9],
                "sale_date": row[10],
                "registered_at": row[11],
            })

        return sales

    # ==================== CA2: Filtered Sales Queries ====================

    def get_sales_by_payment_method(
        self, start_date: str, end_date: str, payment_method: str
    ) -> List[Dict]:
        """Get sales filtered by payment method"""
        result = self.client.execute(
            """
            SELECT
                s.id, s.order_number, s.customer_name, s.waiter_id,
                s.payment_method, s.total_amount, s.tax_amount,
                s.discount_amount, s.final_amount, s.items_count,
                s.sale_date, s.registered_at
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ? AND s.payment_method = ?
            ORDER BY s.sale_date DESC
            """,
            [start_date, end_date, payment_method],
        )

        return [self._map_sale_row(row) for row in result.rows]

    def get_sales_by_waiter(
        self, start_date: str, end_date: str, waiter_id: str
    ) -> List[Dict]:
        """Get sales filtered by employee (waiter)"""
        result = self.client.execute(
            """
            SELECT
                s.id, s.order_number, s.customer_name, s.waiter_id,
                s.payment_method, s.total_amount, s.tax_amount,
                s.discount_amount, s.final_amount, s.items_count,
                s.sale_date, s.registered_at
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ? AND s.waiter_id = ?
            ORDER BY s.sale_date DESC
            """,
            [start_date, end_date, waiter_id],
        )

        return [self._map_sale_row(row) for row in result.rows]

    def get_sales_by_product_category(
        self, start_date: str, end_date: str, category: str
    ) -> List[Dict]:
        """Get sales filtered by product category"""
        result = self.client.execute(
            """
            SELECT
                s.id, s.order_number, s.customer_name, s.waiter_id,
                s.payment_method, s.total_amount, s.tax_amount,
                s.discount_amount, s.final_amount, s.items_count,
                s.sale_date, s.registered_at
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            WHERE s.sale_date BETWEEN ? AND ? AND si.menu_item_name LIKE ?
            ORDER BY s.sale_date DESC
            """,
            [start_date, end_date, f"%{category}%"],
        )

        return [self._map_sale_row(row) for row in result.rows]

    # ==================== CA3: Aggregated Metrics ====================

    def get_payment_method_summary(
        self, start_date: str, end_date: str
    ) -> Dict[str, Dict]:
        """Get summary grouped by payment method"""
        result = self.client.execute(
            """
            SELECT
                s.payment_method,
                COUNT(s.id) as count,
                SUM(s.final_amount) as total_amount,
                AVG(s.final_amount) as avg_amount
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY s.payment_method
            ORDER BY total_amount DESC
            """,
            [start_date, end_date],
        )

        summary = {}
        for row in result.rows:
            method = row[0] or "Sin método"
            summary[method] = {
                "method": method,
                "count": row[1],
                "total_amount": float(row[2]) if row[2] else 0.0,
                "average_amount": float(row[3]) if row[3] else 0.0,
            }

        return summary

    def get_waiter_performance_summary(
        self, start_date: str, end_date: str
    ) -> Dict[str, Dict]:
        """Get performance summary by waiter"""
        result = self.client.execute(
            """
            SELECT
                s.waiter_id,
                COUNT(s.id) as count,
                SUM(s.final_amount) as total_amount,
                AVG(s.final_amount) as avg_amount
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY s.waiter_id
            ORDER BY total_amount DESC
            """,
            [start_date, end_date],
        )

        summary = {}
        for row in result.rows:
            waiter_id = row[0]
            waiter_name = self._get_waiter_name(waiter_id)
            summary[waiter_id] = {
                "waiter_id": waiter_id,
                "waiter_name": waiter_name,
                "sales_count": row[1],
                "total_sales": float(row[2]) if row[2] else 0.0,
                "average_sale": float(row[3]) if row[3] else 0.0,
            }

        return summary

    def get_product_category_summary(
        self, start_date: str, end_date: str
    ) -> Dict[str, Dict]:
        """Get summary grouped by product category"""
        result = self.client.execute(
            """
            SELECT
                si.menu_item_name,
                COUNT(si.id) as quantity,
                SUM(si.subtotal) as total_amount
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY si.menu_item_name
            ORDER BY total_amount DESC
            """,
            [start_date, end_date],
        )

        summary = {}
        for row in result.rows:
            item_name = row[0]
            summary[item_name] = {
                "menu_item_name": item_name,
                "quantity": row[1],
                "total_amount": float(row[2]) if row[2] else 0.0,
            }

        return summary

    def get_sales_with_items(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sales with all items details"""
        sales_result = self.client.execute(
            """
            SELECT
                s.id, s.order_number, s.customer_name, s.waiter_id,
                s.payment_method, s.total_amount, s.tax_amount,
                s.discount_amount, s.final_amount, s.items_count,
                s.sale_date, s.registered_at
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ?
            ORDER BY s.sale_date DESC, s.registered_at DESC
            """,
            [start_date, end_date],
        )

        sales = []
        for sale_row in sales_result.rows:
            sale_id = sale_row[0]
            
            # Get items for this sale
            items_result = self.client.execute(
                """
                SELECT menu_item_name, quantity, unit_price, subtotal
                FROM sale_items
                WHERE sale_id = ?
                """,
                [sale_id],
            )

            items = []
            for item_row in items_result.rows:
                items.append({
                    "menu_item_name": item_row[0],
                    "quantity": item_row[1],
                    "unit_price": float(item_row[2]),
                    "subtotal": float(item_row[3]),
                })

            waiter_name = self._get_waiter_name(sale_row[3])

            sales.append({
                "id": sale_id,
                "order_number": sale_row[1],
                "customer_name": sale_row[2],
                "waiter_id": sale_row[3],
                "waiter_name": waiter_name,
                "payment_method": sale_row[4],
                "total_amount": float(sale_row[5]),
                "tax_amount": float(sale_row[6]),
                "discount_amount": float(sale_row[7]),
                "final_amount": float(sale_row[8]),
                "items_count": sale_row[9],
                "sale_date": sale_row[10],
                "registered_at": sale_row[11],
                "items": items,
            })

        return sales

    def get_financial_metrics(self, start_date: str, end_date: str) -> Dict:
        """Get aggregated financial metrics for period"""
        result = self.client.execute(
            """
            SELECT
                COUNT(s.id) as total_sales,
                SUM(s.total_amount) as total_revenue,
                SUM(s.tax_amount) as total_tax,
                SUM(s.discount_amount) as total_discount,
                AVG(s.final_amount) as average_ticket,
                AVG((s.discount_amount / s.total_amount) * 100) as avg_discount_percent
            FROM sales s
            WHERE s.sale_date BETWEEN ? AND ?
            """,
            [start_date, end_date],
        )

        row = result.rows[0] if result.rows else None
        if not row:
            return {
                "total_sales": 0,
                "total_revenue": 0.0,
                "total_tax": 0.0,
                "total_discount": 0.0,
                "average_ticket": 0.0,
                "average_discount_percent": 0.0,
            }

        return {
            "total_sales": row[0] or 0,
            "total_revenue": float(row[1]) if row[1] else 0.0,
            "total_tax": float(row[2]) if row[2] else 0.0,
            "total_discount": float(row[3]) if row[3] else 0.0,
            "average_ticket": float(row[4]) if row[4] else 0.0,
            "average_discount_percent": float(row[5]) if row[5] else 0.0,
        }

    def _map_sale_row(self, row: tuple) -> Dict:
        """Map database row to sale dictionary"""
        return {
            "id": row[0],
            "order_number": row[1],
            "customer_name": row[2],
            "waiter_id": row[3],
            "payment_method": row[4],
            "total_amount": float(row[5]),
            "tax_amount": float(row[6]),
            "discount_amount": float(row[7]),
            "final_amount": float(row[8]),
            "items_count": row[9],
            "sale_date": row[10],
            "registered_at": row[11],
        }

    def _get_waiter_name(self, waiter_id: str) -> str:
        """Get waiter name by ID"""
        try:
            user = self.user_repo.get_by_id(waiter_id)
            return user.full_name if user else "Desconocido"
        except:
            return "Desconocido"
