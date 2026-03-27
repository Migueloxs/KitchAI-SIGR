"""
Payroll application data transfer objects (DTOs).

DTOs for request validation and response serialization.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============================================================================
# REQUEST DTOs
# ============================================================================

class PayrollPeriodCreateDTO(BaseModel):
    """DTO for creating a payroll period."""
    
    name: str = Field(..., min_length=1, max_length=255)
    period_type: str = Field(..., pattern="^(WEEKLY|BIWEEKLY|MONTHLY|CUSTOM)$")
    start_date: str = Field(..., description="Date in YYYY-MM-DD format")
    end_date: str = Field(..., description="Date in YYYY-MM-DD format")
    is_active: bool = True
    
    @validator("start_date", "end_date")
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class WorkedHoursRequestDTO(BaseModel):
    """DTO for recording worked hours (CA1 - Acceptance Criteria 1)."""
    
    employee_id: str
    payroll_period_id: str
    start_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    normal_hours: Optional[float] = Field(None, ge=0)
    overtime_hours: float = Field(0, ge=0)
    daily_hours: float = Field(8.0, gt=0)
    overtime_threshold: float = Field(40.0, gt=0)
    
    @validator("start_date", "end_date")
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class AbsenceRecordsRequestDTO(BaseModel):
    """DTO for requesting absence records (CA2)."""
    
    employee_id: str
    payroll_period_id: str
    start_date: Optional[str] = Field(None, description="Optional override date in YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="Optional override date in YYYY-MM-DD")
    
    @validator("start_date", "end_date")
    def validate_date_format(cls, v):
        """Validate date format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class PayrollReportRequestDTO(BaseModel):
    """DTO for requesting payroll report for export (CA3)."""
    
    employee_id: Optional[str] = Field(None, description="If null, generate for all employees")
    payroll_period_id: str
    include_deductions: bool = True
    format_type: str = Field("JSON", pattern="^(JSON|CSV)$")


class AddAbsenceDTO(BaseModel):
    """DTO for recording an absence."""
    
    employee_id: str
    absence_date: str = Field(..., description="Date in YYYY-MM-DD format")
    absence_type: str = Field(..., pattern="^(JUSTIFIED|UNJUSTIFIED)$")
    reason: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_paid: bool = False
    payroll_period_id: Optional[str] = None
    
    @validator("absence_date")
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class AddDeductionDTO(BaseModel):
    """DTO for adding a deduction."""
    
    employee_id: str
    payroll_period_id: str
    deduction_type: str = Field(..., pattern="^(ABSENCE|DISCOUNT|OTHER)$")
    amount: float = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class CalculatePayrollDTO(BaseModel):
    """DTO for calculating payroll for an employee."""
    
    employee_id: str
    payroll_period_id: str
    hourly_rate: float = Field(..., gt=0)
    overtime_multiplier: float = Field(1.5, gt=0, le=3.0)
    include_deductions: bool = True


class ApprovePayrollDTO(BaseModel):
    """DTO for approving payroll calculation."""
    
    payroll_id: str
    # approved_by is extracted from JWT token


class PayPayrollDTO(BaseModel):
    """DTO for marking payroll as paid."""
    
    payroll_id: str
    # paid_at is set to current timestamp


# ============================================================================
# RESPONSE DTOs
# ============================================================================

class PayrollPeriodResponseDTO(BaseModel):
    """Response DTO for payroll period."""
    
    id: str
    name: str
    period_type: str
    start_date: str
    end_date: str
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class WorkHoursResponseDTO(BaseModel):
    """Response DTO for work hours (CA1 - Acceptance Criteria 1)."""
    
    id: str
    employee_id: str
    employee_name: str
    email: str
    payroll_period: str
    start_date: str
    end_date: str
    normal_hours: float
    overtime_hours: float
    total_hours: float
    minutes_late: int
    times_late: int
    days_present: int
    
    class Config:
        from_attributes = True
    
    @property
    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            f"{self.employee_name}: {self.normal_hours:.2f}h normal, "
            f"{self.overtime_hours:.2f}h overtime, {self.times_late} late arrivals"
        )


class AbsenceRecordDTO(BaseModel):
    """Response DTO for absence record."""
    
    id: str
    employee_id: str
    absence_date: str
    absence_type: str  # JUSTIFIED or UNJUSTIFIED
    reason: str
    description: Optional[str]
    is_paid: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AbsencesResponseDTO(BaseModel):
    """Response DTO for absences summary (CA2 - Acceptance Criteria 2)."""
    
    employee_id: str
    employee_name: str
    email: str
    payroll_period: str
    start_date: str
    end_date: str
    justified_absences: int
    unjustified_absences: int
    total_absences: int
    paid_absences: int
    absence_records: List[AbsenceRecordDTO] = []
    
    class Config:
        from_attributes = True
    
    @property
    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            f"{self.employee_name}: {self.justified_absences} justified, "
            f"{self.unjustified_absences} unjustified, {self.paid_absences} paid"
        )


class DeductionResponseDTO(BaseModel):
    """Response DTO for deduction."""
    
    id: str
    employee_id: str
    deduction_type: str
    amount: float
    reason: str
    description: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class PayrollCalculationResponseDTO(BaseModel):
    """Response DTO for payroll calculation."""
    
    id: str
    employee_id: str
    employee_name: str
    payroll_period_id: str
    payroll_period: str
    normal_hours: float
    overtime_hours: float
    hourly_rate: float
    overtime_multiplier: float
    base_salary: float
    overtime_salary: float
    gross_salary: float
    total_deductions: float
    net_salary: float
    status: str
    calculated_at: str
    approved_by: Optional[str]
    approved_at: Optional[str]
    paid_at: Optional[str]
    
    class Config:
        from_attributes = True
    
    @property
    def summary(self) -> str:
        """Return human-readable summary."""
        return (
            f"Gross: ${self.gross_salary:,.2f}, "
            f"Deductions: ${self.total_deductions:,.2f}, "
            f"Net: ${self.net_salary:,.2f}"
        )


class PayrollReportLineDTO(BaseModel):
    """Line item in payroll report (CA3 - Acceptance Criteria 3)."""
    
    employee_id: str
    employee_name: str
    email: str
    normal_hours: float
    overtime_hours: float
    hourly_rate: float
    overtime_multiplier: float
    base_salary: float
    overtime_salary: float
    gross_salary: float
    total_deductions: float
    net_salary: float
    status: str
    paid: bool
    
    class Config:
        from_attributes = True


class PayrollReportResponseDTO(BaseModel):
    """Response DTO for payroll report export (CA3 - JSON consumable format)."""
    
    payroll_period_id: str
    payroll_period: str
    period_start: str
    period_end: str
    generated_at: str
    company_name: str = "KitchAI SIGR"
    currency: str = "USD"
    records: List[PayrollReportLineDTO]
    summary: dict = Field(default_factory=dict)
    
    class Config:
        from_attributes = True
    
    def calculate_summary(self):
        """Calculate totals for summary section."""
        self.summary = {
            "total_employees": len(self.records),
            "total_gross_salary": sum(r.gross_salary for r in self.records),
            "total_deductions": sum(r.total_deductions for r in self.records),
            "total_net_salary": sum(r.net_salary for r in self.records),
            "total_normal_hours": sum(r.normal_hours for r in self.records),
            "total_overtime_hours": sum(r.overtime_hours for r in self.records),
            "employees_paid": sum(1 for r in self.records if r.paid),
            "employees_pending": sum(1 for r in self.records if not r.paid),
        }
        return self


class PayrollExportDTO(BaseModel):
    """DTO for exporting payroll to external systems."""
    
    export_id: str
    export_date: str
    export_format: str  # JSON, CSV, XML
    payroll_report: PayrollReportResponseDTO
    export_method: str = "API"  # API, EMAIL, SFTP, etc.
    
    class Config:
        from_attributes = True


# ============================================================================
# ERROR RESPONSE DTOs
# ============================================================================

class ErrorResponseDTO(BaseModel):
    """Standard error response."""
    
    error: str
    message: str
    code: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        from_attributes = True


class ValidationErrorDTO(BaseModel):
    """Validation error response."""
    
    error: str = "VALIDATION_ERROR"
    message: str
    details: List[dict]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        from_attributes = True
