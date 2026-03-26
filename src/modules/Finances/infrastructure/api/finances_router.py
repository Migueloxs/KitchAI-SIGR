"""API Router - Finances Module"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.Finances.application.usecases.finances_usecases import FinancesService
from src.modules.Finances.application.dto.finance_response import (
    ExpenseResponseDTO,
    DailyFinancialDTO,
    PeriodFinancialDTO,
    FinancialReportDTO,
    CreateExpenseRequestDTO,
)
from src.modules.User.infrastructure.api.auth_router import get_current_user

finances_router = APIRouter(prefix="/api/finances", tags=["Finanzas"])

ADMIN_ROLE_ID = "uuid-role-admin"
EMPLOYEE_ROLE_ID = "uuid-role-employee"


def _require_admin(user: dict) -> None:
    if user.get("role_id") != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a reportes financieros",
        )


def _require_admin_or_employee(user: dict) -> None:
    if user.get("role_id") not in [ADMIN_ROLE_ID, EMPLOYEE_ROLE_ID]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere permiso de administrador o empleado",
        )


# ==================== EXPENSE MANAGEMENT ====================


@finances_router.post("/expenses/", response_model=ExpenseResponseDTO)
def create_expense(
    request: CreateExpenseRequestDTO,
    user=Depends(get_current_user),
):
    """Crear un nuevo gasto (admin solo)"""
    _require_admin(user)
    service = FinancesService()
    return service.create_expense(request, user.get("id"))


@finances_router.get("/expenses/", response_model=list[ExpenseResponseDTO])
def list_all_expenses(user=Depends(get_current_user)):
    """Listar todos los gastos (admin solo)"""
    _require_admin(user)
    service = FinancesService()
    return service.get_all_expenses()


@finances_router.get("/expenses/{expense_id}", response_model=ExpenseResponseDTO)
def get_expense(expense_id: str, user=Depends(get_current_user)):
    """Obtener gasto específico (admin solo)"""
    _require_admin(user)
    service = FinancesService()
    expense = service.get_expense(expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gasto con ID {expense_id} no encontrado",
        )
    return expense


# ==================== CA1: INCOME CALCULATIONS ====================


@finances_router.get("/income/daily/")
def get_daily_income(
    date: str = Query(..., description="Fecha (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """CA1: Obtener ingresos totales del día (suma de todas las ventas)"""
    _require_admin_or_employee(user)
    service = FinancesService()
    income = service.get_total_income_by_date(date)
    return {"date": date, "total_income": income}


@finances_router.get("/income/period/")
def get_period_income(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """CA1: Obtener ingresos totales del período (suma de todas las ventas)"""
    _require_admin_or_employee(user)
    service = FinancesService()
    income = service.get_total_income_by_period(start_date, end_date)
    return {
        "period_start": start_date,
        "period_end": end_date,
        "total_income": income,
    }


# ==================== CA2: PROFIT CALCULATIONS ====================


@finances_router.get("/profit/daily/")
def get_daily_profit(
    date: str = Query(..., description="Fecha (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """CA2: Obtener ganancia neta del día (ingresos - gastos)"""
    _require_admin_or_employee(user)
    service = FinancesService()
    profit_data = service.get_net_profit_by_date(date)
    return {
        "date": date,
        "total_income": profit_data["income"],
        "total_expenses": profit_data["expenses"],
        "net_profit": profit_data["net_profit"],
    }


@finances_router.get("/profit/period/")
def get_period_profit(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """CA2: Obtener ganancia neta del período (ingresos - gastos)"""
    _require_admin_or_employee(user)
    service = FinancesService()
    profit_data = service.get_net_profit_by_period(start_date, end_date)
    return {
        "period_start": start_date,
        "period_end": end_date,
        "total_income": profit_data["income"],
        "total_expenses": profit_data["expenses"],
        "net_profit": profit_data["net_profit"],
        "profit_margin_percent": profit_data["profit_margin"],
    }


# ==================== CA3: REAL-TIME REPORTS ====================


@finances_router.get("/report/daily/", response_model=DailyFinancialDTO)
def get_daily_report(
    date: str = Query(None, description="Fecha (YYYY-MM-DD), por defecto hoy"),
    user=Depends(get_current_user),
):
    """CA3: Obtener reporte financiero diario en tiempo real"""
    _require_admin_or_employee(user)
    service = FinancesService()
    
    if not date:
        from datetime import datetime
        date = datetime.now().date().isoformat()
    
    return service.get_daily_financial_summary(date)


@finances_router.get("/report/period/", response_model=PeriodFinancialDTO)
def get_period_report(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """CA3: Obtener reporte financiero del período en tiempo real"""
    _require_admin_or_employee(user)
    service = FinancesService()
    
    try:
        return service.get_period_financial_summary(start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al generar reporte: {str(e)}",
        )


@finances_router.get("/report/comprehensive/", response_model=FinancialReportDTO)
def get_comprehensive_report(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    user=Depends(get_current_user),
):
    """CA3: Obtener reporte financiero completo con desglose detallado"""
    _require_admin(user)
    service = FinancesService()
    
    try:
        return service.get_comprehensive_financial_report(start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al generar reporte: {str(e)}",
        )
