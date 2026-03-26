"""
Attendance API Router - REST endpoints for attendance management
Implements CA1, CA2, CA3 requirements
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime, date
from typing import List, Optional

from src.modules.Attendance.application.usecases.attendance_service import AttendanceService
from src.modules.Attendance.application.dto import (
    CheckInRequestDTO,
    CheckOutRequestDTO,
    AttendanceRecordResponseDTO,
    AttendanceAlertResponseDTO,
    AcknowledgeAlertRequestDTO,
    AttendanceSummaryDTO,
    AttendanceReportDTO,
    AttendanceReportListDTO,
    TodayAttendanceSummaryListDTO,
    AttendanceStatisticsDTO,
)
from src.modules.User.infrastructure.api.auth_router import get_current_user

attendance_router = APIRouter(prefix="/api/attendance", tags=["Asistencia"])

ADMIN_ROLE_ID = "uuid-role-admin"
SUPERVISOR_ROLE_ID = "uuid-role-supervisor"
EMPLOYEE_ROLE_ID = "uuid-role-employee"


def _require_admin_or_supervisor(user: dict) -> None:
    """Require admin or supervisor role"""
    if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere ser Administrador o Supervisor para acceder a esta función",
        )


def _require_admin(user: dict) -> None:
    """Require admin role"""
    if user.get("role_id") != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere ser Administrador",
        )


def _require_employee_or_higher(user: dict) -> None:
    """Require employee role or higher"""
    allowed_roles = [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID, EMPLOYEE_ROLE_ID]
    if user.get("role_id") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere ser un empleado para acceder a esta función",
        )


# ==================== CA1: CHECK-IN / CHECK-OUT ====================


@attendance_router.post(
    "/check-in",
    response_model=AttendanceRecordResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def check_in(
    request: CheckInRequestDTO,
    user=Depends(get_current_user),
):
    """
    CA1: Employee checks in
    Registers the employee's arrival time for the day
    """
    # Verify employee can only check in for themselves
    if request.employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede registrar entrada para otro empleado",
            )
    
    service = AttendanceService()
    
    try:
        return service.check_in(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registrando entrada: {str(e)}",
        )


@attendance_router.post(
    "/check-out",
    response_model=AttendanceRecordResponseDTO,
)
def check_out(
    request: CheckOutRequestDTO,
    user=Depends(get_current_user),
):
    """
    CA1: Employee checks out
    Registers the employee's departure time for the day
    """
    # Verify employee can only check out for themselves
    if request.employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede registrar salida para otro empleado",
            )
    
    service = AttendanceService()
    
    try:
        return service.check_out(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registrando salida: {str(e)}",
        )


@attendance_router.get(
    "/today",
    response_model=Optional[AttendanceRecordResponseDTO],
)
def get_today_attendance(
    employee_id: str = Query(..., description="ID del empleado"),
    user=Depends(get_current_user),
):
    """
    Get today's attendance record for an employee
    Employee can only view their own record unless admin/supervisor
    """
    # Verify access
    if employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede ver el registro de otro empleado",
            )
    
    service = AttendanceService()
    
    try:
        return service.get_today_attendance(employee_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@attendance_router.get(
    "/history",
    response_model=List[AttendanceRecordResponseDTO],
)
def get_attendance_history(
    employee_id: str = Query(..., description="ID del empleado"),
    start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
):
    """
    Get attendance history for an employee
    """
    # Verify access
    if employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede ver el historial de otro empleado",
            )
    
    service = AttendanceService()
    
    try:
        records, total = service.get_attendance_history(
            employee_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== CA2: ALERT MANAGEMENT ====================


@attendance_router.post(
    "/alerts/check-missing-checkins",
    response_model=List[AttendanceAlertResponseDTO],
)
def generate_alerts(user=Depends(get_current_user)):
    """
    CA2: Generate automatic alerts for missing check-ins
    This endpoint should be called periodically (e.g., via cron job or scheduler)
    """
    _require_admin_or_supervisor(user)
    
    service = AttendanceService()
    
    try:
        return service.generate_no_checkin_alerts()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando alertas: {str(e)}",
        )


@attendance_router.get(
    "/alerts/pending",
    response_model=List[AttendanceAlertResponseDTO],
)
def get_pending_alerts(
    employee_id: Optional[str] = Query(None, description="ID del empleado (opcional)"),
    user=Depends(get_current_user),
):
    """
    CA2: Get pending (unacknowledged) alerts
    """
    # Regular employees can only see their own alerts
    if employee_id and employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede ver alertas de otro empleado",
            )
    
    # If not admin/supervisor and no employee_id provided, use current user
    if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
        employee_id = user.get("id")
    
    service = AttendanceService()
    
    try:
        return service.get_pending_alerts(employee_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@attendance_router.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=AttendanceAlertResponseDTO,
)
def acknowledge_alert(
    alert_id: str,
    request: AcknowledgeAlertRequestDTO,
    user=Depends(get_current_user),
):
    """
    Acknowledge an alert (typically by supervisor/admin)
    """
    _require_admin_or_supervisor(user)
    
    service = AttendanceService()
    
    try:
        return service.acknowledge_alert(request, user.get("id"))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@attendance_router.get(
    "/alerts",
    response_model=List[AttendanceAlertResponseDTO],
)
def get_alerts(
    employee_id: str = Query(..., description="ID del empleado"),
    start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
):
    """
    Get alerts for an employee
    """
    # Verify access
    if employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede ver alertas de otro empleado",
            )
    
    service = AttendanceService()
    
    try:
        alerts, total = service.get_alerts_for_employee(
            employee_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== CA3: REPORTS AND STATISTICS ====================


@attendance_router.get(
    "/reports/today",
    response_model=TodayAttendanceSummaryListDTO,
)
def get_today_summary(user=Depends(get_current_user)):
    """
    CA3: Get today's attendance summary for all employees
    """
    _require_admin_or_supervisor(user)
    
    service = AttendanceService()
    
    try:
        summaries = service.get_today_attendance_summary()
        
        checked_in = sum(1 for s in summaries if s.status == "CHECKED_IN")
        absent = sum(1 for s in summaries if s.status == "ABSENT")
        pending_alerts = sum(s.pending_alerts for s in summaries)
        
        return TodayAttendanceSummaryListDTO(
            data=summaries,
            total=len(summaries),
            with_pending_alerts=sum(1 for s in summaries if s.pending_alerts > 0),
            checked_in_count=checked_in,
            absent_count=absent,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@attendance_router.get(
    "/reports/attendance",
    response_model=AttendanceReportListDTO,
)
def get_attendance_report(
    employee_id: Optional[str] = Query(None, description="ID del empleado (opcional)"),
    start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
):
    """
    CA3: Get detailed attendance report
    """
    # Regular employees can only see their own report
    if employee_id and employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede ver el reporte de otro empleado",
            )
    
    # If not admin/supervisor and no employee_id provided, use current user
    if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
        employee_id = user.get("id")
    
    service = AttendanceService()
    
    try:
        reports, total = service.get_attendance_report(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        
        import math
        total_pages = math.ceil(total / limit)
        page = (offset // limit) + 1
        
        return AttendanceReportListDTO(
            data=reports,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@attendance_router.get(
    "/statistics",
    response_model=AttendanceStatisticsDTO,
)
def get_statistics(
    employee_id: Optional[str] = Query(None, description="ID del empleado"),
    days: int = Query(30, ge=1, le=365, description="Número de días a considerar"),
    user=Depends(get_current_user),
):
    """
    CA3: Get attendance statistics for an employee
    """
    # If employee_id not provided, get current user's stats
    if not employee_id:
        employee_id = user.get("id")
    
    # Regular employees can only see their own stats
    if employee_id != user.get("id"):
        if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede ver estadísticas de otro empleado",
            )
    
    service = AttendanceService()
    
    try:
        return service.get_employee_statistics(employee_id, days=days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
