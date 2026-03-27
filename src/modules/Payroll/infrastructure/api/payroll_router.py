"""
Payroll API Router - REST endpoints for payroll management.

Provides REST endpoints for:
- CA1: Worked hours calculation (normal vs overtime)
- CA2: Absence tracking (justified/unjustified)
- CA3: Payroll report export (JSON consumable format)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime
from typing import Optional, List

from src.modules.Payroll.application.dto import (
    PayrollPeriodCreateDTO,
    WorkedHoursRequestDTO,
    AbsenceRecordsRequestDTO,
    PayrollReportRequestDTO,
    AddAbsenceDTO,
    AddDeductionDTO,
    CalculatePayrollDTO,
    ApprovePayrollDTO,
    PayPayrollDTO,
    PayrollPeriodResponseDTO,
    WorkHoursResponseDTO,
    AbsencesResponseDTO,
    PayrollCalculationResponseDTO,
    PayrollReportResponseDTO,
    ErrorResponseDTO,
)
from src.modules.Payroll.application.usecases.payroll_service import PayrollService
from src.shared.infrastructure.middleware.auth import verify_token
from src.shared.infrastructure.middleware.rbac import check_permission

# Initialize router
payroll_router = APIRouter(
    prefix="/api/payroll",
    tags=["Nómina"],  # Spanish: Payroll
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_payroll_service() -> PayrollService:
    """Get payroll service instance."""
    from src.shared.infrastructure.database.database_handler import DatabaseHandler
    from src.modules.Payroll.infrastructure.repositories.payroll_repository import (
        PayrollRepository,
    )
    from src.modules.Attendance.infrastructure.repositories.attendance_repository import (
        AttendanceRepository,
    )
    from src.modules.User.infrastructure.repositories.user_repository import (
        UserRepository,
    )
    
    db = DatabaseHandler()
    payroll_repo = PayrollRepository(db)
    attendance_repo = AttendanceRepository(db)
    user_repo = UserRepository(db)
    
    return PayrollService(payroll_repo, attendance_repo, user_repo)


# ============================================================================
# PAYROLL PERIODS MANAGEMENT
# ============================================================================

@payroll_router.post(
    "/periods",
    response_model=PayrollPeriodResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Payroll Period",
    description="Create a new payroll period (monthly, weekly, bi-weekly, etc.)",
)
async def create_payroll_period(
    dto: PayrollPeriodCreateDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Create a new payroll period.
    
    **Permissions Required:** HR_MANAGER, ADMIN
    
    Example request:
    ```json
    {
        "name": "2026-03 (March 2026)",
        "period_type": "MONTHLY",
        "start_date": "2026-03-01",
        "end_date": "2026-03-31",
        "is_active": false
    }
    ```
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN"])
    
    try:
        period = payroll_service.create_payroll_period(dto)
        return PayrollPeriodResponseDTO.from_orm(period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create payroll period")


@payroll_router.get(
    "/periods/active",
    response_model=List[PayrollPeriodResponseDTO],
    summary="Get Active Payroll Periods",
    description="Retrieve all active payroll periods",
)
async def get_active_payroll_periods(
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """Get all active payroll periods."""
    try:
        periods = payroll_service.get_active_payroll_periods()
        return [PayrollPeriodResponseDTO.from_orm(p) for p in periods]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve payroll periods")


@payroll_router.get(
    "/periods/{period_id}",
    response_model=PayrollPeriodResponseDTO,
    summary="Get Payroll Period by ID",
)
async def get_payroll_period(
    period_id: str,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """Get a specific payroll period by ID."""
    try:
        period = payroll_service.repository.get_payroll_period_by_id(period_id)
        if not period:
            raise HTTPException(
                status_code=404,
                detail=f"Payroll period not found: {period_id}",
            )
        return PayrollPeriodResponseDTO.from_orm(period)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve payroll period")


# ============================================================================
# WORKED HOURS CALCULATION (CA1)
# ============================================================================

@payroll_router.post(
    "/worked-hours",
    response_model=WorkHoursResponseDTO,
    summary="Calculate Worked Hours",
    description="Calculate worked hours (normal vs overtime) for an employee in a payroll period",
)
async def calculate_worked_hours(
    dto: WorkedHoursRequestDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Calculate worked hours for an employee (CA1 - Acceptance Criteria 1).
    
    Returns normal hours, overtime hours, and lateness tracking.
    
    **Permissions Required:** HR, SUPERVISOR, or own employee data
    
    Example request:
    ```json
    {
        "employee_id": "emp-123",
        "payroll_period_id": "period-2026-03"
    }
    ```
    
    Example response:
    ```json
    {
        "id": "wh-456",
        "employee_id": "emp-123",
        "employee_name": "Juan García",
        "email": "juan@kitchai.com",
        "payroll_period": "2026-03 (March 2026)",
        "start_date": "2026-03-01",
        "end_date": "2026-03-31",
        "normal_hours": 160.0,
        "overtime_hours": 12.5,
        "total_hours": 172.5,
        "minutes_late": 145,
        "times_late": 5,
        "days_present": 22
    }
    ```
    """
    # Check permissions - user can see own data or user must be HR/ADMIN
    if (current_user.get("employee_id") != dto.employee_id and 
        current_user.get("role") not in ["HR_MANAGER", "SUPERVISOR", "ADMIN"]):
        raise HTTPException(
            status_code=403,
            detail="Cannot access other employee's hours",
        )
    
    try:
        result = payroll_service.calculate_worked_hours(
            employee_id=dto.employee_id,
            payroll_period_id=dto.payroll_period_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate worked hours",
        )


# ============================================================================
# ABSENCE RECORDS (CA2)
# ============================================================================

@payroll_router.post(
    "/absences",
    response_model=AbsencesResponseDTO,
    summary="Get Absence Records",
    description="Get absence records (justified/unjustified) for an employee in a period",
)
async def get_absences(
    dto: AbsenceRecordsRequestDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Get absence records for an employee (CA2 - Acceptance Criteria 2).
    
    Shows breakdown of justified vs unjustified absences.
    
    **Permissions Required:** HR, SUPERVISOR, or own employee data
    
    Example request:
    ```json
    {
        "employee_id": "emp-123",
        "payroll_period_id": "period-2026-03"
    }
    ```
    
    Example response:
    ```json
    {
        "employee_id": "emp-123",
        "employee_name": "Juan García",
        "email": "juan@kitchai.com",
        "payroll_period": "2026-03 (March 2026)",
        "start_date": "2026-03-01",
        "end_date": "2026-03-31",
        "justified_absences": 2,
        "unjustified_absences": 1,
        "total_absences": 3,
        "paid_absences": 2
    }
    ```
    """
    # Check permissions
    if (current_user.get("employee_id") != dto.employee_id and 
        current_user.get("role") not in ["HR_MANAGER", "SUPERVISOR", "ADMIN"]):
        raise HTTPException(
            status_code=403,
            detail="Cannot access other employee's absences",
        )
    
    try:
        result = payroll_service.get_absences_for_period(
            employee_id=dto.employee_id,
            payroll_period_id=dto.payroll_period_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve abseence records",
        )


@payroll_router.post(
    "/absences/record",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Record Absence",
    description="Record an absence for an employee",
)
async def record_absence(
    dto: AddAbsenceDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Record an absence for an employee.
    
    **Permissions Required:** HR_MANAGER, SUPERVISOR, ADMIN
    
    Example request:
    ```json
    {
        "employee_id": "emp-123",
        "absence_date": "2026-03-05",
        "absence_type": "JUSTIFIED",
        "reason": "Medical leave",
        "description": "Doctor appointment",
        "is_paid": true
    }
    ```
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "SUPERVISOR", "ADMIN"])
    
    try:
        absence = payroll_service.record_absence(dto)
        return {
            "id": absence.id,
            "employee_id": absence.employee_id,
            "absence_date": absence.absence_date,
            "absence_type": absence.absence_type.value,
            "reason": absence.reason,
            "created_at": absence.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to record absence",
        )


# ============================================================================
# DEDUCTIONS MANAGEMENT
# ============================================================================

@payroll_router.post(
    "/deductions",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add Deduction",
    description="Add a deduction for a payroll period",
)
async def add_deduction(
    dto: AddDeductionDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Add a deduction for a payroll period.
    
    **Permissions Required:** HR_MANAGER, ADMIN
    
    Example request:
    ```json
    {
        "employee_id": "emp-123",
        "payroll_period_id": "period-2026-03",
        "deduction_type": "DISCOUNT",
        "amount": 100.00,
        "reason": "Disciplinary action",
        "description": "Breakage of equipment"
    }
    ```
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN"])
    
    try:
        deduction = payroll_service.add_deduction(dto)
        return {
            "id": deduction.id,
            "employee_id": deduction.employee_id,
            "amount": deduction.amount,
            "reason": deduction.reason,
            "created_at": deduction.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to add deduction",
        )


# ============================================================================
# PAYROLL CALCULATION
# ============================================================================

@payroll_router.post(
    "/calculate",
    response_model=PayrollCalculationResponseDTO,
    summary="Calculate Payroll",
    description="Calculate payroll for an employee",
)
async def calculate_payroll(
    dto: CalculatePayrollDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Calculate payroll for an employee.
    
    **Permissions Required:** HR_MANAGER, ADMIN
    
    Example request:
    ```json
    {
        "employee_id": "emp-123",
        "payroll_period_id": "period-2026-03",
        "hourly_rate": 15.50,
        "overtime_multiplier": 1.5,
        "include_deductions": true
    }
    ```
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN"])
    
    try:
        result = payroll_service.calculate_payroll(dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate payroll",
        )


# ============================================================================
# PAYROLL REPORTING & EXPORT (CA3)
# ============================================================================

@payroll_router.post(
    "/report",
    response_model=PayrollReportResponseDTO,
    summary="Generate Payroll Report",
    description="Generate payroll report for export (CA3 - JSON consumable format)",
)
async def generate_payroll_report(
    dto: PayrollReportRequestDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Generate payroll report for export (CA3 - Acceptance Criteria 3).
    
    Produces JSON format consumable by external payroll systems.
    
    **Permissions Required:** HR_MANAGER, ADMIN
    
    Example request:
    ```json
    {
        "payroll_period_id": "period-2026-03",
        "include_deductions": true,
        "format_type": "JSON"
    }
    ```
    
    Example response:
    ```json
    {
        "payroll_period_id": "period-2026-03",
        "payroll_period": "2026-03 (March 2026)",
        "period_start": "2026-03-01",
        "period_end": "2026-03-31",
        "generated_at": "2026-03-31T18:30:00",
        "company_name": "KitchAI SIGR",
        "currency": "USD",
        "records": [
            {
                "employee_id": "emp-123",
                "employee_name": "Juan García",
                "email": "juan@kitchai.com",
                "normal_hours": 160.0,
                "overtime_hours": 12.5,
                "hourly_rate": 15.50,
                "overtime_multiplier": 1.5,
                "base_salary": 2480.00,
                "overtime_salary": 291.88,
                "gross_salary": 2771.88,
                "total_deductions": 150.00,
                "net_salary": 2621.88,
                "status": "APPROVED",
                "paid": false
            }
        ],
        "summary": {
            "total_employees": 1,
            "total_gross_salary": 2771.88,
            "total_deductions": 150.00,
            "total_net_salary": 2621.88,
            "total_normal_hours": 160.0,
            "total_overtime_hours": 12.5,
            "employees_paid": 0,
            "employees_pending": 1
        }
    }
    ```
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN"])
    
    try:
        result = payroll_service.generate_payroll_report(dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate payroll report",
        )


@payroll_router.post(
    "/export/json",
    response_model=dict,
    summary="Export Payroll as JSON",
    description="Export payroll data as JSON for external systems",
)
async def export_payroll_json(
    dto: PayrollReportRequestDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Export payroll data as JSON.
    
    **Permissions Required:** HR_MANAGER, ADMIN
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN"])
    
    try:
        result = payroll_service.export_payroll_to_json(dto)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to export payroll",
        )


# ============================================================================
# APPROVAL & PAYMENT WORKFLOW
# ============================================================================

@payroll_router.post(
    "/approve",
    response_model=PayrollCalculationResponseDTO,
    summary="Approve Payroll",
    description="Approve a payroll calculation",
)
async def approve_payroll(
    dto: ApprovePayrollDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Approve a payroll calculation.
    
    **Permissions Required:** HR_MANAGER, ADMIN
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN"])
    
    try:
        result = payroll_service.approve_payroll(
            payroll_id=dto.payroll_id,
            approved_by=current_user.get("id"),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to approve payroll",
        )


@payroll_router.post(
    "/pay",
    response_model=PayrollCalculationResponseDTO,
    summary="Mark Payroll as Paid",
    description="Mark a payroll as paid",
)
async def mark_payroll_paid(
    dto: PayPayrollDTO,
    current_user: dict = Depends(verify_token),
    payroll_service: PayrollService = Depends(get_payroll_service),
):
    """
    Mark payroll as paid.
    
    **Permissions Required:** HR_MANAGER, ADMIN, ACCOUNTING
    """
    # Check permissions
    check_permission(current_user, ["HR_MANAGER", "ADMIN", "ACCOUNTING"])
    
    try:
        result = payroll_service.mark_payroll_paid(dto.payroll_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to mark payroll as paid",
        )


# ============================================================================
# HEALTH CHECK & STATISTICS
# ============================================================================

@payroll_router.get(
    "/health",
    response_model=dict,
    summary="Payroll Module Health Check",
    description="Check payroll module status",
)
async def payroll_health(
    current_user: dict = Depends(verify_token),
):
    """
    Health check endpoint for payroll module.
    
    Returns:
    ```json
    {
        "status": "healthy",
        "module": "payroll",
        "version": "1.0.0",
        "timestamp": "2026-03-31T18:30:00"
    }
    ```
    """
    return {
        "status": "healthy",
        "module": "payroll",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
