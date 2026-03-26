from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.Sales.application.usecases.sales_usecases import SalesService
from src.modules.Sales.application.dto.sale_response import (
    SaleResponseDTO,
    SalesReportDTO,
)
from src.modules.User.infrastructure.api.auth_router import get_current_user

sales_router = APIRouter(prefix="/api/sales", tags=["Ventas y Reportes"])

ADMIN_ROLE_ID = "uuid-role-admin"
EMPLOYEE_ROLE_ID = "uuid-role-employee"


def _require_admin(user: dict) -> None:
    if user.get("role_id") != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a reportes de ventas",
        )


def _require_admin_or_employee(user: dict) -> None:
    if user.get("role_id") not in [ADMIN_ROLE_ID, EMPLOYEE_ROLE_ID]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere permiso de administrador o empleado",
        )


@sales_router.get("/", response_model=List[SaleResponseDTO])
def list_all_sales(user=Depends(get_current_user)):
    """Listar todas las ventas registradas"""
    _require_admin(user)
    service = SalesService()
    return service.get_all_sales()


@sales_router.get("/{sale_id}", response_model=SaleResponseDTO)
def get_sale_by_id(sale_id: str, user=Depends(get_current_user)):
    """Obtener detalles de una venta específica"""
    _require_admin(user)
    service = SalesService()
    sale = service.get_sale_by_id(sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venta con ID {sale_id} no encontrada",
        )
    return sale


@sales_router.get("/by-date-range/", response_model=List[SaleResponseDTO])
def get_sales_by_date_range(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """Obtener ventas por rango de fechas"""
    _require_admin_or_employee(user)
    service = SalesService()
    try:
        return service.get_sales_by_date_range(start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@sales_router.get("/by-waiter/{waiter_id}", response_model=List[SaleResponseDTO])
def get_sales_by_waiter(waiter_id: str, user=Depends(get_current_user)):
    """Obtener ventas de un mesero específico"""
    _require_admin(user)
    service = SalesService()
    return service.get_sales_by_waiter(waiter_id)


@sales_router.get("/report/daily/", response_model=dict)
def get_daily_report(
    date: str = Query(
        None, description="Fecha para el reporte (YYYY-MM-DD), por defecto hoy"
    ),
    user=Depends(get_current_user),
):
    """Obtener reporte diario de ventas"""
    _require_admin_or_employee(user)
    service = SalesService()
    return service.get_daily_report(date)


@sales_router.get("/report/period/", response_model=SalesReportDTO)
def get_period_report(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """Obtener reporte de ventas por período"""
    _require_admin_or_employee(user)
    service = SalesService()
    try:
        return service.get_period_report(start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
