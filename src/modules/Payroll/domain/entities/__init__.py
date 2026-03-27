"""
Payroll domain entities module.

This module defines the core entities for the Payroll Management System:
- WorkHours: Represents worked hours (normal and overtime) for an employee in a payroll period
- PayrollAbsence: Represents absences (justified or unjustified) for payroll deduction
- PayrollDeduction: Represents adjustments/deductions for a payroll period
- PayrollCalculation: Represents the final calculated payroll for an employee
- PayrollPeriod: Represents a payroll period (weekly, monthly, bi-weekly, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class PeriodType(str, Enum):
    """Payroll period types."""
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"


class AbsenceType(str, Enum):
    """Types of absences."""
    JUSTIFIED = "JUSTIFIED"  # Vacation, medical leave, business travel, etc.
    UNJUSTIFIED = "UNJUSTIFIED"  # No-show, unauthorized absence


class DeductionType(str, Enum):
    """Types of deductions."""
    ABSENCE = "ABSENCE"  # Deduction for unjustified absence
    DISCOUNT = "DISCOUNT"  # Disciplinary discount
    OTHER = "OTHER"  # Other deductions


class PayrollStatus(str, Enum):
    """Payroll calculation statuses."""
    DRAFT = "DRAFT"  # Initial calculation, not final
    CALCULATED = "CALCULATED"  # Calculation complete and verified
    APPROVED = "APPROVED"  # Approved by manager/HR
    PAID = "PAID"  # Payment processed


@dataclass
class PayrollPeriod:
    """
    Represents a payroll period (e.g., March 2026, Week 13 2026).
    
    This entity defines the time frame for payroll calculations.
    """
    
    id: str
    name: str  # e.g., "2026-03 (March 2026)" or "W13 2026"
    period_type: PeriodType
    start_date: str  # YYYY-MM-DD format
    end_date: str  # YYYY-MM-DD format
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate period dates."""
        if self.start_date >= self.end_date:
            raise ValueError(
                f"Invalid period: start_date ({self.start_date}) must be before "
                f"end_date ({self.end_date})"
            )


@dataclass
class WorkHours:
    """
    Represents worked hours for an employee in a specific payroll period.
    
    Attributes:
        id: Unique identifier
        employee_id: Reference to employee (user)
        payroll_period_id: Reference to payroll period
        normal_hours: Hours within standard shift (e.g., 40 for typical week)
        overtime_hours: Hours beyond standard shift
        total_hours: normal_hours + overtime_hours
        minutes_late: Total minutes late during period
        times_late: Number of times late
        notes: Additional notes
        calculated_at: When calculation was performed
    """
    
    id: str
    employee_id: str
    payroll_period_id: str
    normal_hours: float
    overtime_hours: float = 0.0
    total_hours: float = 0.0
    minutes_late: int = 0
    times_late: int = 0
    notes: Optional[str] = None
    calculated_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate and recalculate total hours."""
        if self.normal_hours < 0:
            raise ValueError("normal_hours cannot be negative")
        if self.overtime_hours < 0:
            raise ValueError("overtime_hours cannot be negative")
        
        # Recalculate total
        self.total_hours = self.normal_hours + self.overtime_hours
        
        if self.times_late > 0 and self.minutes_late == 0:
            raise ValueError(
                "If times_late > 0, minutes_late must be > 0"
            )


@dataclass
class PayrollAbsence:
    """
    Represents an absence for an employee.
    
    Attributes:
        id: Unique identifier
        employee_id: Reference to employee
        absence_date: Date of absence (YYYY-MM-DD)
        absence_type: JUSTIFIED or UNJUSTIFIED
        reason: Human-readable reason
        description: Additional details
        is_paid: Whether paid or deducted
        payroll_period_id: Reference to payroll period
        created_by: Manager/HR who recorded this
    """
    
    id: str
    employee_id: str
    absence_date: str  # YYYY-MM-DD
    absence_type: AbsenceType
    reason: str
    description: Optional[str] = None
    is_paid: bool = False
    payroll_period_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate absence data."""
        try:
            # Validate date format
            datetime.fromisoformat(self.absence_date)
        except ValueError:
            raise ValueError(
                f"Invalid absence_date format: {self.absence_date}. "
                "Expected YYYY-MM-DD"
            )


@dataclass
class PayrollDeduction:
    """
    Represents a deduction or adjustment for a payroll period.
    
    Attributes:
        id: Unique identifier
        employee_id: Reference to employee
        payroll_period_id: Reference to payroll period
        deduction_type: Type of deduction (ABSENCE, DISCOUNT, OTHER)
        amount: Deduction amount (positive number)
        reason: Human-readable reason
        description: Additional details
        created_by: Manager who created this deduction
    """
    
    id: str
    employee_id: str
    payroll_period_id: str
    deduction_type: DeductionType
    amount: float
    reason: str
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate deduction data."""
        if self.amount <= 0:
            raise ValueError("amount must be positive")


@dataclass
class PayrollCalculation:
    """
    Represents the complete calculated payroll for an employee.
    
    This is the final payroll record containing all calculations and approvals.
    
    Attributes:
        id: Unique identifier
        employee_id: Reference to employee
        payroll_period_id: Reference to payroll period
        normal_hours: Total normal hours worked
        overtime_hours: Total overtime hours worked
        hourly_rate: Base hourly rate at calculation time
        overtime_multiplier: Multiplier for overtime (e.g., 1.5x)
        base_salary: normal_hours * hourly_rate
        overtime_salary: overtime_hours * hourly_rate * overtime_multiplier
        gross_salary: base_salary + overtime_salary
        total_deductions: Sum of all deductions
        net_salary: gross_salary - total_deductions
        status: Current status (DRAFT, CALCULATED, APPROVED, PAID)
        calculated_at: When calculation was performed
        approved_by: Manager who approved
        approved_at: When approved
        paid_at: When payment was processed
    """
    
    id: str
    employee_id: str
    payroll_period_id: str
    normal_hours: float
    overtime_hours: float
    hourly_rate: float
    overtime_multiplier: float  # typically 1.5
    base_salary: float
    overtime_salary: float
    gross_salary: float
    total_deductions: float = 0.0
    net_salary: float = 0.0
    status: PayrollStatus = PayrollStatus.DRAFT
    calculated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    paid_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate and recalculate payroll totals."""
        # Validate rates
        if self.hourly_rate <= 0:
            raise ValueError("hourly_rate must be positive")
        if self.overtime_multiplier <= 0:
            raise ValueError("overtime_multiplier must be positive")
        
        # Recalculate salaries
        self.base_salary = self.normal_hours * self.hourly_rate
        self.overtime_salary = (
            self.overtime_hours * self.hourly_rate * self.overtime_multiplier
        )
        self.gross_salary = self.base_salary + self.overtime_salary
        self.net_salary = self.gross_salary - self.total_deductions
        
        # Validate calculated values
        if self.net_salary < 0:
            raise ValueError(
                f"net_salary cannot be negative: {self.net_salary}"
            )
    
    def set_approved(self, approved_by: str, approved_at: Optional[str] = None):
        """Mark payroll as approved."""
        self.status = PayrollStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = approved_at or datetime.utcnow().isoformat()
    
    def set_paid(self, paid_at: Optional[str] = None):
        """Mark payroll as paid."""
        if self.status != PayrollStatus.APPROVED:
            raise ValueError("Cannot mark as paid until approved")
        
        self.status = PayrollStatus.PAID
        self.paid_at = paid_at or datetime.utcnow().isoformat()
