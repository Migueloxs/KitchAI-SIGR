"""
DTOs (Data Transfer Objects) for Attendance API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Check-In/Check-Out DTOs ====================

class CheckInRequestDTO(BaseModel):
    """Request DTO for checking in"""
    employee_id: str = Field(..., description="ID of the employee checking in")
    check_in_time: Optional[datetime] = Field(
        None,
        description="Check-in time (defaults to current time if not provided)"
    )
    notes: Optional[str] = Field(None, description="Optional notes about the check-in")
    
    class Config:
        example = {
            "employee_id": "emp-123",
            "check_in_time": "2026-03-26T08:00:00",
            "notes": "Checked in from main entrance"
        }


class CheckOutRequestDTO(BaseModel):
    """Request DTO for checking out"""
    employee_id: str = Field(..., description="ID of the employee checking out")
    record_id: str = Field(..., description="ID of the attendance record to check out")
    check_out_time: Optional[datetime] = Field(
        None,
        description="Check-out time (defaults to current time if not provided)"
    )
    notes: Optional[str] = Field(None, description="Optional notes about the check-out")
    
    class Config:
        example = {
            "employee_id": "emp-123",
            "record_id": "att-rec-456",
            "check_out_time": "2026-03-26T16:00:00",
            "notes": "Checked out from back exit"
        }


class AttendanceRecordResponseDTO(BaseModel):
    """Response DTO for attendance record"""
    id: str
    employee_id: str
    shift_assignment_id: Optional[str]
    check_in_time: datetime
    check_out_time: Optional[datetime]
    duration_minutes: Optional[int]
    status: str
    is_late: bool
    late_by_minutes: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        example = {
            "id": "att-rec-123",
            "employee_id": "emp-123",
            "shift_assignment_id": "shift-asgn-456",
            "check_in_time": "2026-03-26T08:00:00",
            "check_out_time": "2026-03-26T16:00:00",
            "duration_minutes": 480,
            "status": "CHECKED_OUT",
            "is_late": False,
            "late_by_minutes": None,
            "notes": None,
            "created_at": "2026-03-26T08:00:00",
            "updated_at": "2026-03-26T16:00:00"
        }


# ==================== Alert DTOs ====================

class AttendanceAlertResponseDTO(BaseModel):
    """Response DTO for attendance alert"""
    id: str
    employee_id: str
    alert_type: str
    description: str
    severity: str
    shift_assignment_id: Optional[str]
    referenced_attendance_id: Optional[str]
    is_acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    auto_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        example = {
            "id": "alert-123",
            "employee_id": "emp-123",
            "alert_type": "LATE_ARRIVAL",
            "description": "Employee checked in 15 minutes late",
            "severity": "WARNING",
            "shift_assignment_id": "shift-asgn-456",
            "referenced_attendance_id": "att-rec-123",
            "is_acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "auto_resolved": False,
            "resolved_at": None,
            "created_at": "2026-03-26T08:15:00",
            "updated_at": "2026-03-26T08:15:00"
        }


class AcknowledgeAlertRequestDTO(BaseModel):
    """Request DTO to acknowledge an alert"""
    alert_id: str = Field(..., description="ID of the alert to acknowledge")
    notes: Optional[str] = Field(None, description="Optional notes about acknowledging the alert")
    
    class Config:
        example = {
            "alert_id": "alert-123",
            "notes": "Employee was stuck in traffic"
        }


# ==================== Report DTOs ====================

class AttendanceSummaryDTO(BaseModel):
    """Summary of today's attendance for an employee"""
    employee_id: str
    employee_name: str
    email: str
    check_in_time: str
    check_out_time: str
    is_late: bool
    status: str
    pending_alerts: int
    
    class Config:
        example = {
            "employee_id": "emp-123",
            "employee_name": "Juan García",
            "email": "juan@restaurant.com",
            "check_in_time": "2026-03-26T08:00:00",
            "check_out_time": "NOT CHECKED OUT",
            "is_late": False,
            "status": "CHECKED_IN",
            "pending_alerts": 0
        }


class AttendanceReportDTO(BaseModel):
    """Detailed attendance report for a date range"""
    employee_id: str
    employee_name: str
    attendance_date: datetime
    shift_name: str
    scheduled_check_in: str
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    attendance_status: str
    late_by_minutes: Optional[int]
    alert_count: int
    
    class Config:
        example = {
            "employee_id": "emp-123",
            "employee_name": "Juan García",
            "attendance_date": "2026-03-26",
            "shift_name": "Mañana",
            "scheduled_check_in": "08:00",
            "check_in_time": "2026-03-26T08:00:00",
            "check_out_time": "2026-03-26T16:00:00",
            "attendance_status": "PRESENT",
            "late_by_minutes": None,
            "alert_count": 0
        }


class AttendanceReportListDTO(BaseModel):
    """Paginated list of attendance reports"""
    data: List[AttendanceReportDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


class TodayAttendanceSummaryListDTO(BaseModel):
    """List of today's attendance for all employees"""
    data: List[AttendanceSummaryDTO]
    total: int
    with_pending_alerts: int
    checked_in_count: int
    absent_count: int


# ==================== Statistics DTOs ====================

class AttendanceStatisticsDTO(BaseModel):
    """Attendance statistics for an employee"""
    employee_id: str
    employee_name: str
    total_working_days: int
    present_days: int
    absent_days: int
    late_arrivals: int
    no_checkout_count: int
    average_check_in_delay_minutes: Optional[float]
    average_work_duration_minutes: Optional[float]
    
    class Config:
        example = {
            "employee_id": "emp-123",
            "employee_name": "Juan García",
            "total_working_days": 20,
            "present_days": 19,
            "absent_days": 1,
            "late_arrivals": 2,
            "no_checkout_count": 0,
            "average_check_in_delay_minutes": 5.5,
            "average_work_duration_minutes": 480.0
        }
