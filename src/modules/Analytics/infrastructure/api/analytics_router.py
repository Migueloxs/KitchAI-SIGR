"""Analytics API Router - Endpoints for analysis and metrics."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from src.modules.Analytics.application.usecases import AnalyticsService
from src.modules.Analytics.application.dto import (
    SalesDataResponseDTO,
    ComparativeAnalyticsResponseDTO,
    AnalyticsSummaryDTO,
)
from src.modules.User.infrastructure.api.auth_router import get_current_user


analytics_router = APIRouter(prefix="/api/analytics", tags=["Análisis y Métricas"])

ADMIN_ROLE_ID = "uuid-role-admin"
EMPLOYEE_ROLE_ID = "uuid-role-employee"


def _require_admin_or_employee(user: dict) -> None:
    """Require user to have admin or employee role."""
    if user.get("role_id") not in [ADMIN_ROLE_ID, EMPLOYEE_ROLE_ID]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere permiso de administrador o empleado para acceder a análisis",
        )


@analytics_router.get("/sales-data", response_model=SalesDataResponseDTO)
def get_sales_analytics(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    service_type: Optional[str] = Query(None, description="Tipo de servicio: dine-in, delivery, takeaway o all"),
    employee_id: Optional[str] = Query(None, description="ID del empleado (opcional)"),
    category_name: Optional[str] = Query(None, description="Nombre de categoría (opcional)"),
    user=Depends(get_current_user),
):
    """
    CA1: Get aggregated sales data by product, hour and category.
    
    Returns sales metrics structured in JSON format with:
    - Sales breakdown by product
    - Sales breakdown by hour (hourly trends)
    - Sales breakdown by category
    - Sales breakdown by service type
    - Metadata with totals, percentages and key metrics
    
    ### CA2: Supported Filters:
    - `start_date` and `end_date`: Filter by date range (required)
    - `service_type`: Filter by service type (dine-in, delivery, takeaway)
    - `employee_id`: Filter by specific employee
    - `category_name`: Filter by product category
    
    ### CA3: Response includes:
    - **Metadata**: Total revenue, cost, profit, tax, discounts
    - **Percentages**: Profit margin, percentage by service type
    - **Comparatives**: Data structured for period comparison
    """
    _require_admin_or_employee(user)
    
    service = AnalyticsService()
    
    try:
        return service.get_sales_analytics(
            start_date=start_date,
            end_date=end_date,
            service_type=service_type,
            employee_id=employee_id,
            category_name=category_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos de análisis: {str(e)}",
        )


@analytics_router.get("/comparative", response_model=ComparativeAnalyticsResponseDTO)
def get_comparative_analytics(
    start_date: str = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha fin (YYYY-MM-DD)"),
    period_type: str = Query("day", description="Tipo de período: day, week, month, quarter, year"),
    service_type: Optional[str] = Query(None, description="Tipo de servicio (opcional)"),
    user=Depends(get_current_user),
):
    """
    CA3: Get comparative analytics with previous period.
    
    Returns comprehensive analysis including:
    - **Current period sales data** (same as CA1 endpoint)
    - **Comparison with previous period**: Revenue, cost, profit and transaction changes in percentages
    - **Top performing products**: Best sellers by revenue
    - **Top employee**: Employee with highest sales
    - **Peak hours analysis**: Hours with highest revenue
    
    ### Period Types Supported:
    - `day`: Compare with previous day
    - `week`: Compare with previous week
    - `month`: Compare with previous month
    - `quarter`: Compare with previous quarter
    - `year`: Compare with previous year
    
    This endpoint addresses CA3 requirements by providing:
    - Metadatos with totals and percentages
    - Comparativas with previous periods
    - Insights for actionable business decisions
    """
    _require_admin_or_employee(user)
    
    service = AnalyticsService()
    
    try:
        return service.get_comparative_analytics(
            start_date=start_date,
            end_date=end_date,
            period_type=period_type,
            service_type=service_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener análisis comparativo: {str(e)}",
        )


@analytics_router.get("/dashboard", response_model=AnalyticsSummaryDTO)
def get_dashboard_summary(
    date: Optional[str] = Query(None, description="Fecha a analizar (YYYY-MM-DD, default: hoy)"),
    user=Depends(get_current_user),
):
    """
    Get dashboard summary for a specific date.
    
    Returns quick metrics for dashboards:
    - Total revenue, profit, transactions
    - Average ticket
    - Peak hour and revenue
    - Revenue breakdown by service type
    
    If no date is provided, returns data for today.
    """
    _require_admin_or_employee(user)
    
    service = AnalyticsService()
    
    try:
        return service.get_dashboard_summary(date=date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen del dashboard: {str(e)}",
        )
