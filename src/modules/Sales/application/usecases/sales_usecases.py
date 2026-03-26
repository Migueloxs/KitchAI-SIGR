from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from src.modules.Sales.domain.entities.sale import Sale, SaleItem
from src.modules.Sales.infrastructure.repositories.sales_repository import SalesRepository
from src.modules.Sales.application.dto.sale_response import (
    SaleResponseDTO,
    SalesReportDTO,
    SalesByWaiterDTO,
    SalesByDateDTO,
)
from src.modules.Order.domain.entities.order import Order


class SalesService:
    def __init__(self):
        self.repo = SalesRepository()

    def register_sale_from_order(self, order: Order) -> SaleResponseDTO:
        """Registrar una venta basada en una orden completada"""
        if self.repo.exists_for_order(order.id):
            raise ValueError(f"Ya existe una venta registrada para la orden {order.id}")

        if order.status.value not in ["served", "delivered"]:
            raise ValueError(
                f"La orden debe estar en estado 'served' o 'delivered' para registrar una venta"
            )

        sale = Sale(
            id=str(uuid.uuid4()),
            order_id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            waiter_id=order.waiter_id,
            payment_method=order.payment_method,
            total_amount=order.total_amount,
            tax_amount=order.tax_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            items_count=len(order.items),
            sale_date=datetime.now().date().isoformat(),
            registered_at=datetime.now(),
            items=[
                SaleItem(
                    id=str(uuid.uuid4()),
                    sale_id=None,
                    menu_item_id=item.menu_item_id,
                    menu_item_name=item.menu_item_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                )
                for item in order.items
            ],
        )

        saved_sale = self.repo.create(sale)
        return self._to_response_dto(saved_sale)

    def get_sale_by_id(self, sale_id: str) -> Optional[SaleResponseDTO]:
        sale = self.repo.get_by_id(sale_id)
        return self._to_response_dto(sale) if sale else None

    def get_all_sales(self) -> List[SaleResponseDTO]:
        sales = self.repo.get_all()
        return [self._to_response_dto(sale) for sale in sales]

    def get_sales_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[SaleResponseDTO]:
        sales = self.repo.get_by_date_range(start_date, end_date)
        return [self._to_response_dto(sale) for sale in sales]

    def get_sales_by_waiter(self, waiter_id: str) -> List[SaleResponseDTO]:
        sales = self.repo.get_by_waiter(waiter_id)
        return [self._to_response_dto(sale) for sale in sales]

    def get_daily_report(self, date: str = None) -> dict:
        if not date:
            date = datetime.now().date().isoformat()

        return self.repo.get_summary_by_date(date)

    def get_period_report(self, start_date: str, end_date: str) -> SalesReportDTO:
        sales = self.repo.get_by_date_range(start_date, end_date)

        total_revenue = sum(sale.final_amount for sale in sales)
        total_tax = sum(sale.tax_amount for sale in sales)
        total_discount = sum(sale.discount_amount for sale in sales)

        by_waiter = self.repo.get_summary_by_waiter(start_date, end_date)
        by_payment_method = self.repo.get_summary_by_payment_method(start_date, end_date)

        by_waiter_dict = {item["waiter_id"]: item for item in by_waiter}
        by_payment_method_dict = {
            item["payment_method"]: item for item in by_payment_method
        }

        return SalesReportDTO(
            total_sales=len(sales),
            total_revenue=total_revenue,
            total_tax=total_tax,
            total_discount=total_discount,
            period_from=start_date,
            period_to=end_date,
            by_waiter=by_waiter_dict,
            by_payment_method=by_payment_method_dict,
        )

    def _to_response_dto(self, sale: Sale) -> SaleResponseDTO:
        return SaleResponseDTO(
            id=sale.id,
            order_id=sale.order_id,
            order_number=sale.order_number,
            customer_name=sale.customer_name,
            waiter_id=sale.waiter_id,
            payment_method=sale.payment_method,
            total_amount=sale.total_amount,
            tax_amount=sale.tax_amount,
            discount_amount=sale.discount_amount,
            final_amount=sale.final_amount,
            items_count=sale.items_count,
            sale_date=sale.sale_date,
            registered_at=sale.registered_at,
            items=[
                {
                    "id": item.id,
                    "menu_item_id": item.menu_item_id,
                    "menu_item_name": item.menu_item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                }
                for item in sale.items
            ],
        )
