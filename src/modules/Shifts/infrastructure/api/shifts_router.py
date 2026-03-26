"""
Shifts API Router - REST endpoints for shifts management
Implements CA1, CA2, CA3 requirements
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import date
from typing import List, Optional

from src.modules.Shifts.application.usecases.shifts_service import ShiftsService
from src.modules.Shifts.application.dto import (
    CreateShiftRequestDTO,
    UpdateShiftRequestDTO,
    AssignShiftRequestDTO,
    UpdateShiftAssignmentRequestDTO,
    BulkAssignShiftRequestDTO,
    ShiftResponseDTO,
    ShiftAssignmentResponseDTO,
    WeeklyCalendarDTO,
    ShiftConflictDTO,
    BulkAssignmentResponseDTO,
)
from src.modules.User.infrastructure.api.auth_router import get_current_user

shifts_router = APIRouter(prefix="/api/shifts", tags=["Turnos"])

ADMIN_ROLE_ID = "uuid-role-admin"
SUPERVISOR_ROLE_ID = "uuid-role-supervisor"
EMPLOYEE_ROLE_ID = "uuid-role-employee"


def _require_admin_or_supervisor(user: dict) -> None:
    """Require admin or supervisor role"""
    if user.get("role_id") not in [ADMIN_ROLE_ID, SUPERVISOR_ROLE_ID]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere ser Administrador o Supervisor para gestionar turnos",
        )


def _require_admin(user: dict) -> None:
    """Require admin role"""
    if user.get("role_id") != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere ser Administrador",
        )


# ==================== SHIFT MANAGEMENT (CA1) ====================


@shifts_router.post("/shifts/", response_model=ShiftResponseDTO, status_code=status.HTTP_201_CREATED)
def create_shift(
    request: CreateShiftRequestDTO,
    user=Depends(get_current_user),
):
    """
    CA1: Create a new shift pattern
    Define weekly shifts (entry/exit times) for the restaurant
    """
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        return service.create_shift(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando turno: {str(e)}",
        )


@shifts_router.get("/shifts/", response_model=List[ShiftResponseDTO])
def get_all_shifts(
    active_only: bool = Query(True, description="Solo turnos activos"),
    user=Depends(get_current_user),
):
    """Get all shifts"""
    service = ShiftsService()
    
    try:
        return service.get_all_shifts(active_only=active_only)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@shifts_router.get("/shifts/{shift_id}", response_model=ShiftResponseDTO)
def get_shift(
    shift_id: str,
    user=Depends(get_current_user),
):
    """Get a specific shift"""
    service = ShiftsService()
    
    try:
        return service.get_shift(shift_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@shifts_router.get("/shifts/day/{day_of_week}", response_model=List[ShiftResponseDTO])
def get_shifts_by_day(
    day_of_week: int,
    user=Depends(get_current_user),
):
    """Get shifts for a specific day of the week"""
    service = ShiftsService()
    
    try:
        return service.get_shifts_by_day(day_of_week)
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


@shifts_router.put("/shifts/{shift_id}", response_model=ShiftResponseDTO)
def update_shift(
    shift_id: str,
    request: UpdateShiftRequestDTO,
    user=Depends(get_current_user),
):
    """Update a shift"""
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        return service.update_shift(shift_id, request)
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


@shifts_router.delete("/shifts/{shift_id}")
def delete_shift(
    shift_id: str,
    user=Depends(get_current_user),
):
    """Delete (deactivate) a shift"""
    _require_admin(user)
    service = ShiftsService()
    
    try:
        success = service.delete_shift(shift_id)
        return {"success": success, "message": "Turno eliminado correctamente"}
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


# ==================== SHIFT ASSIGNMENTS (CA1, CA2) ====================


@shifts_router.post("/assignments/", response_model=ShiftAssignmentResponseDTO, status_code=status.HTTP_201_CREATED)
def assign_shift(
    request: AssignShiftRequestDTO,
    user=Depends(get_current_user),
):
    """
    CA1: Assign a shift to an employee
    CA2: Validates no overlapping shifts on the same day
    """
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        return service.assign_shift(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error asignando turno: {str(e)}",
        )


@shifts_router.post("/assignments/bulk/", response_model=BulkAssignmentResponseDTO, status_code=status.HTTP_201_CREATED)
def bulk_assign_shift(
    request: BulkAssignShiftRequestDTO,
    user=Depends(get_current_user),
):
    """
    CA1: Assign a shift to multiple employees
    CA2: Validates each employee individually
    """
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        return service.bulk_assign_shift(request)
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


@shifts_router.get("/assignments/employee/{employee_id}", response_model=List[ShiftAssignmentResponseDTO])
def get_employee_assignments(
    employee_id: str,
    user=Depends(get_current_user),
):
    """Get all shift assignments for an employee"""
    service = ShiftsService()
    
    try:
        return service.get_employee_assignments(employee_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@shifts_router.put("/assignments/{assignment_id}", response_model=ShiftAssignmentResponseDTO)
def update_assignment(
    assignment_id: str,
    request: UpdateShiftAssignmentRequestDTO,
    user=Depends(get_current_user),
):
    """Update a shift assignment (extend or end)"""
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        return service.update_assignment(assignment_id, request)
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


@shifts_router.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: str,
    user=Depends(get_current_user),
):
    """Delete a shift assignment"""
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        success = service.delete_assignment(assignment_id)
        return {"success": success, "message": "Asignación de turno eliminada"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==================== CALENDAR VIEW (CA3) ====================


@shifts_router.get("/calendar/employee/{employee_id}", response_model=WeeklyCalendarDTO)
def get_employee_calendar(
    employee_id: str,
    week_start: Optional[str] = Query(None, description="Formato YYYY-MM-DD"),
    user=Depends(get_current_user),
):
    """
    CA3: Get employee's calendar view
    Shows all assigned shifts in calendar format
    Accessible by employees and supervisors
    """
    service = ShiftsService()
    
    try:
        week_start_date = None
        if week_start:
            from datetime import datetime as dt
            week_start_date = dt.fromisoformat(week_start).date()
        
        return service.get_employee_calendar(employee_id, week_start_date)
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


@shifts_router.get("/calendar/team/")
def get_team_calendar(
    employee_ids: str = Query(..., description="IDs separados por comas"),
    week_start: Optional[str] = Query(None, description="Formato YYYY-MM-DD"),
    user=Depends(get_current_user),
):
    """
    CA3: Get team calendar view
    Shows schedules for multiple employees
    """
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        emp_ids = [e.strip() for e in employee_ids.split(",")]
        
        week_start_date = None
        if week_start:
            from datetime import datetime as dt
            week_start_date = dt.fromisoformat(week_start).date()
        
        return service.get_team_calendar(emp_ids, week_start_date)
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


# ==================== CONFLICT DETECTION (CA2) ====================


@shifts_router.get("/conflicts/check/")
def check_conflicts(
    employee_id: str = Query(...),
    target_date: str = Query(..., description="Formato YYYY-MM-DD"),
    user=Depends(get_current_user),
):
    """
    CA2: Check for overlapping shifts
    Validates that an employee doesn't have conflicting shifts
    """
    _require_admin_or_supervisor(user)
    service = ShiftsService()
    
    try:
        from datetime import datetime as dt
        target = dt.fromisoformat(target_date).date()
        
        conflict_dto = service.check_conflicts_for_employee(employee_id, target)
        if conflict_dto:
            return conflict_dto
        
        return {"message": "Sin conflictos de turnos"}
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
