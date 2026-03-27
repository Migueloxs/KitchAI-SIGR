"""
Payroll service layer - Business logic for payroll calculations.

This service handles all payroll operations including:
- Calculating worked hours (normal vs overtime)
- Tracking justified/unjustified absences
- Computing payroll calculations
- Generating payroll reports for export
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from src.modules.Payroll.domain.entities import (
    PayrollPeriod,
    WorkHours,
    PayrollAbsence,
    PayrollDeduction,
    PayrollCalculation,
    PeriodType,
    AbsenceType,
    DeductionType,
    PayrollStatus,
)
from src.modules.Payroll.application.dto import (
    PayrollPeriodCreateDTO,
    WorkedHoursRequestDTO,
    AbsenceRecordsRequestDTO,
    PayrollReportRequestDTO,
    AddAbsenceDTO,
    AddDeductionDTO,
    CalculatePayrollDTO,
    WorkHoursResponseDTO,
    AbsencesResponseDTO,
    PayrollCalculationResponseDTO,
    PayrollReportResponseDTO,
    PayrollReportLineDTO,
)


class PayrollService:
    """
    Service layer for payroll management.
    
    Coordinates between domain entities, repositories, and external services.
    """
    
    def __init__(self, payroll_repository, attendance_repository, user_repository):
        """
        Initialize payroll service with dependencies.
        
        Args:
            payroll_repository: Repository for payroll data access
            attendance_repository: Repository for attendance data
            user_repository: Repository for user/employee data
        """
        self.repository = payroll_repository
        self.attendance_repo = attendance_repository
        self.user_repo = user_repository
    
    # ========================================================================
    # PAYROLL PERIOD MANAGEMENT
    # ========================================================================
    
    def create_payroll_period(
        self,
        dto: PayrollPeriodCreateDTO
    ) -> PayrollPeriod:
        """
        Create a new payroll period.
        
        Args:
            dto: PayrollPeriodCreateDTO with period details
            
        Returns:
            Created PayrollPeriod entity
        """
        period = PayrollPeriod(
            id=str(uuid.uuid4()),
            name=dto.name,
            period_type=PeriodType(dto.period_type),
            start_date=dto.start_date,
            end_date=dto.end_date,
            is_active=dto.is_active,
        )
        
        saved = self.repository.save_payroll_period(period)
        return saved
    
    def get_active_payroll_periods(self) -> List[PayrollPeriod]:
        """Get all active payroll periods."""
        return self.repository.get_active_payroll_periods()
    
    def get_payroll_period_for_date(self, date_str: str) -> Optional[PayrollPeriod]:
        """
        Get payroll period that contains the given date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            PayrollPeriod or None if no matching period
        """
        return self.repository.get_payroll_period_for_date(date_str)
    
    # ========================================================================
    # WORKED HOURS CALCULATION (CA1)
    # ========================================================================
    
    def calculate_worked_hours(
        self,
        employee_id: str,
        payroll_period_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> WorkHoursResponseDTO:
        """
        Calculate worked hours for an employee in a payroll period.
        
        This is Acceptance Criteria 1 (CA1): Return worked hours by employee
        in date range, differentiating normal vs overtime.
        
        Args:
            employee_id: Employee ID
            payroll_period_id: Payroll period ID
            start_date: Optional override start date
            end_date: Optional override end date
            
        Returns:
            WorkHoursResponseDTO with normal/overtime hours breakdown
        """
        # Get payroll period
        period = self.repository.get_payroll_period_by_id(payroll_period_id)
        if not period:
            raise ValueError(f"Payroll period not found: {payroll_period_id}")
        
        # Use override dates or period dates
        date_start = start_date or period.start_date
        date_end = end_date or period.end_date
        
        # Get attendance records for this employee and date range
        attendance_records = self.attendance_repo.get_attendance_for_period(
            employee_id=employee_id,
            start_date=date_start,
            end_date=date_end,
        )
        
        # Calculate hours from attendance records
        normal_hours, overtime_hours, minutes_late, times_late = (
            self._calculate_hours_from_attendance(
                employee_id=employee_id,
                attendance_records=attendance_records,
                start_date=date_start,
                end_date=date_end,
            )
        )
        
        # Create or update work_hours record
        work_hours = self.repository.get_or_create_work_hours(
            employee_id=employee_id,
            payroll_period_id=payroll_period_id,
        )
        
        work_hours.normal_hours = normal_hours
        work_hours.overtime_hours = overtime_hours
        work_hours.total_hours = normal_hours + overtime_hours
        work_hours.minutes_late = minutes_late
        work_hours.times_late = times_late
        work_hours.calculated_at = datetime.utcnow().isoformat()
        
        saved = self.repository.save_work_hours(work_hours)
        
        # Get employee info
        employee = self.user_repo.get_user_by_id(employee_id)
        
        # Get attendance summary (days present)
        days_present = len(
            [r for r in attendance_records if r.get("status") == "CHECKED_OUT"]
        )
        
        # Build response
        return WorkHoursResponseDTO(
            id=saved.id,
            employee_id=saved.employee_id,
            employee_name=employee.get("name", "Unknown"),
            email=employee.get("email", ""),
            payroll_period=period.name,
            start_date=period.start_date,
            end_date=period.end_date,
            normal_hours=saved.normal_hours,
            overtime_hours=saved.overtime_hours,
            total_hours=saved.total_hours,
            minutes_late=saved.minutes_late,
            times_late=saved.times_late,
            days_present=days_present,
        )
    
    def _calculate_hours_from_attendance(
        self,
        employee_id: str,
        attendance_records: List[Dict[str, Any]],
        start_date: str,
        end_date: str,
    ) -> Tuple[float, float, int, int]:
        """
        Calculate normal and overtime hours from attendance records.
        
        Args:
            employee_id: Employee ID
            attendance_records: List of attendance record dicts
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Tuple of (normal_hours, overtime_hours, total_minutes_late, times_late)
        """
        total_normal_hours = 0.0
        total_overtime_hours = 0.0
        total_minutes_late = 0
        times_late = 0
        
        # Get employee's shift assignments for the period
        shift_assignments = self.attendance_repo.get_shift_assignments_for_period(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        # Create lookup map: date -> shift info
        shift_map = {}
        for assignment in shift_assignments:
            date = assignment.get("date", assignment.get("shift_date", ""))
            shift_map[date] = assignment
        
        # Process each attendance record
        for record in attendance_records:
            check_in = record.get("check_in_time")
            check_out = record.get("check_out_time")
            
            if not check_in or not check_out:
                continue  # Incomplete record
            
            # Calculate hours worked
            hours_worked = record.get("duration_minutes", 0) / 60.0
            
            # Get expected shift for this day
            check_in_date = check_in.split("T")[0]  # Extract YYYY-MM-DD
            shift_info = shift_map.get(check_in_date)
            
            if shift_info:
                # Extract shift duration
                shift_start = shift_info.get("shift_start_time", "")
                shift_end = shift_info.get("shift_end_time", "")
                
                if shift_start and shift_end:
                    # Parse shift times and calculate expected hours
                    expected_hours = self._calculate_shift_duration(
                        shift_start, shift_end
                    )
                else:
                    # Default 8-hour shift if not specified
                    expected_hours = 8.0
            else:
                # Default 8-hour shift if no assignment
                expected_hours = 8.0
            
            # Categorize hours
            if hours_worked <= expected_hours:
                total_normal_hours += hours_worked
            else:
                total_normal_hours += expected_hours
                total_overtime_hours += (hours_worked - expected_hours)
            
            # Track lateness
            if record.get("is_late"):
                times_late += 1
                late_minutes = record.get("late_minutes", 0)
                total_minutes_late += late_minutes
        
        return total_normal_hours, total_overtime_hours, total_minutes_late, times_late
    
    def _calculate_shift_duration(self, shift_start: str, shift_end: str) -> float:
        """
        Calculate duration of a shift in hours.
        
        Args:
            shift_start: Shift start time (HH:MM format)
            shift_end: Shift end time (HH:MM format)
            
        Returns:
            Duration in hours as float
        """
        try:
            start = datetime.strptime(shift_start, "%H:%M")
            end = datetime.strptime(shift_end, "%H:%M")
            
            # Handle overnight shifts
            if end <= start:
                end = end + timedelta(days=1)
            
            duration = (end - start).total_seconds() / 3600.0
            return max(duration, 0)
        except (ValueError, AttributeError):
            return 8.0  # Default to 8-hour shift on error
    
    # ========================================================================
    # ABSENCE MANAGEMENT (CA2)
    # ========================================================================
    
    def get_absences_for_period(
        self,
        employee_id: str,
        payroll_period_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> AbsencesResponseDTO:
        """
        Get absence records for an employee in a payroll period.
        
        This is Acceptance Criteria 2 (CA2): Include justified/unjustified
        absence records.
        
        Args:
            employee_id: Employee ID
            payroll_period_id: Payroll period ID
            start_date: Optional override start date
            end_date: Optional override end date
            
        Returns:
            AbsencesResponseDTO with justified/unjustified breakdown
        """
        # Get payroll period
        period = self.repository.get_payroll_period_by_id(payroll_period_id)
        if not period:
            raise ValueError(f"Payroll period not found: {payroll_period_id}")
        
        # Use override dates or period dates
        date_start = start_date or period.start_date
        date_end = end_date or period.end_date
        
        # Get absence records
        absence_records = self.repository.get_absences_for_period(
            employee_id=employee_id,
            start_date=date_start,
            end_date=date_end,
        )
        
        # Get employee info
        employee = self.user_repo.get_user_by_id(employee_id)
        
        # Count justified and unjustified
        justified = []
        unjustified = []
        paid_count = 0
        
        for record in absence_records:
            is_justified = record.get("absence_type") == "JUSTIFIED"
            
            if is_justified:
                justified.append(record)
            else:
                unjustified.append(record)
            
            if record.get("is_paid"):
                paid_count += 1
        
        # Build response
        return AbsencesResponseDTO(
            employee_id=employee_id,
            employee_name=employee.get("name", "Unknown"),
            email=employee.get("email", ""),
            payroll_period=period.name,
            start_date=period.start_date,
            end_date=period.end_date,
            justified_absences=len(justified),
            unjustified_absences=len(unjustified),
            total_absences=len(absence_records),
            paid_absences=paid_count,
            absence_records=[],  # Could populate with details if needed
        )
    
    def record_absence(self, dto: AddAbsenceDTO) -> PayrollAbsence:
        """
        Record an absence for an employee.
        
        Args:
            dto: AddAbsenceDTO with absence details
            
        Returns:
            Created PayrollAbsence entity
        """
        absence = PayrollAbsence(
            id=str(uuid.uuid4()),
            employee_id=dto.employee_id,
            absence_date=dto.absence_date,
            absence_type=AbsenceType(dto.absence_type),
            reason=dto.reason,
            description=dto.description,
            is_paid=dto.is_paid,
            payroll_period_id=dto.payroll_period_id,
        )
        
        saved = self.repository.save_absence(absence)
        return saved
    
    # ========================================================================
    # DEDUCTIONS MANAGEMENT
    # ========================================================================
    
    def add_deduction(self, dto: AddDeductionDTO) -> PayrollDeduction:
        """
        Add a deduction for a payroll period.
        
        Args:
            dto: AddDeductionDTO with deduction details
            
        Returns:
            Created PayrollDeduction entity
        """
        deduction = PayrollDeduction(
            id=str(uuid.uuid4()),
            employee_id=dto.employee_id,
            payroll_period_id=dto.payroll_period_id,
            deduction_type=DeductionType(dto.deduction_type),
            amount=dto.amount,
            reason=dto.reason,
            description=dto.description,
        )
        
        saved = self.repository.save_deduction(deduction)
        return saved
    
    def get_total_deductions(
        self,
        employee_id: str,
        payroll_period_id: str,
    ) -> float:
        """
        Calculate total deductions for an employee in a payroll period.
        
        Args:
            employee_id: Employee ID
            payroll_period_id: Payroll period ID
            
        Returns:
            Total deduction amount
        """
        deductions = self.repository.get_deductions(
            employee_id=employee_id,
            payroll_period_id=payroll_period_id,
        )
        
        return sum(d.get("amount", 0) for d in deductions)
    
    # ========================================================================
    # PAYROLL CALCULATION
    # ========================================================================
    
    def calculate_payroll(self, dto: CalculatePayrollDTO) -> PayrollCalculationResponseDTO:
        """
        Calculate payroll for an employee.
        
        Args:
            dto: CalculatePayrollDTO with calculation parameters
            
        Returns:
            PayrollCalculationResponseDTO with complete payroll calculation
        """
        # Get work hours
        work_hours = self.repository.get_work_hours(
            employee_id=dto.employee_id,
            payroll_period_id=dto.payroll_period_id,
        )
        
        if not work_hours:
            raise ValueError(
                f"No work hours found for employee {dto.employee_id} "
                f"in period {dto.payroll_period_id}"
            )
        
        # Calculate salaries
        base_salary = work_hours.normal_hours * dto.hourly_rate
        overtime_salary = (
            work_hours.overtime_hours * dto.hourly_rate * dto.overtime_multiplier
        )
        gross_salary = base_salary + overtime_salary
        
        # Get total deductions
        total_deductions = 0.0
        if dto.include_deductions:
            total_deductions = self.get_total_deductions(
                employee_id=dto.employee_id,
                payroll_period_id=dto.payroll_period_id,
            )
        
        # Calculate net salary
        net_salary = gross_salary - total_deductions
        
        # Create or update calculation
        payroll = PayrollCalculation(
            id=str(uuid.uuid4()),
            employee_id=dto.employee_id,
            payroll_period_id=dto.payroll_period_id,
            normal_hours=work_hours.normal_hours,
            overtime_hours=work_hours.overtime_hours,
            hourly_rate=dto.hourly_rate,
            overtime_multiplier=dto.overtime_multiplier,
            base_salary=base_salary,
            overtime_salary=overtime_salary,
            gross_salary=gross_salary,
            total_deductions=total_deductions,
            net_salary=net_salary,
            status=PayrollStatus.CALCULATED,
        )
        
        saved = self.repository.save_payroll_calculation(payroll)
        
        # Get employee and period info
        employee = self.user_repo.get_user_by_id(dto.employee_id)
        period = self.repository.get_payroll_period_by_id(dto.payroll_period_id)
        
        # Build response
        return PayrollCalculationResponseDTO(
            id=saved.id,
            employee_id=saved.employee_id,
            employee_name=employee.get("name", "Unknown"),
            payroll_period_id=saved.payroll_period_id,
            payroll_period=period.name if period else "",
            normal_hours=saved.normal_hours,
            overtime_hours=saved.overtime_hours,
            hourly_rate=saved.hourly_rate,
            overtime_multiplier=saved.overtime_multiplier,
            base_salary=saved.base_salary,
            overtime_salary=saved.overtime_salary,
            gross_salary=saved.gross_salary,
            total_deductions=saved.total_deductions,
            net_salary=saved.net_salary,
            status=saved.status.value,
            calculated_at=saved.calculated_at,
            approved_by=saved.approved_by,
            approved_at=saved.approved_at,
            paid_at=saved.paid_at,
        )
    
    # ========================================================================
    # PAYROLL REPORTING & EXPORT (CA3)
    # ========================================================================
    
    def generate_payroll_report(
        self,
        dto: PayrollReportRequestDTO,
    ) -> PayrollReportResponseDTO:
        """
        Generate payroll report for export to external systems.
        
        This is Acceptance Criteria 3 (CA3): JSON format consumable
        by external payroll systems.
        
        Args:
            dto: PayrollReportRequestDTO with report parameters
            
        Returns:
            PayrollReportResponseDTO with exportable payroll data
        """
        # Get payroll period
        period = self.repository.get_payroll_period_by_id(dto.payroll_period_id)
        if not period:
            raise ValueError(f"Payroll period not found: {dto.payroll_period_id}")
        
        # Get payroll calculations
        if dto.employee_id:
            # Single employee
            records = [
                self.repository.get_payroll_calculation(
                    employee_id=dto.employee_id,
                    payroll_period_id=dto.payroll_period_id,
                )
            ]
        else:
            # All employees for period
            records = self.repository.get_payroll_calculations_for_period(
                payroll_period_id=dto.payroll_period_id,
            )
        
        # Filter out None values
        records = [r for r in records if r is not None]
        
        # Build report lines
        report_lines = []
        for calc in records:
            employee = self.user_repo.get_user_by_id(calc.employee_id)
            
            line = PayrollReportLineDTO(
                employee_id=calc.employee_id,
                employee_name=employee.get("name", "Unknown"),
                email=employee.get("email", ""),
                normal_hours=calc.normal_hours,
                overtime_hours=calc.overtime_hours,
                hourly_rate=calc.hourly_rate,
                overtime_multiplier=calc.overtime_multiplier,
                base_salary=calc.base_salary,
                overtime_salary=calc.overtime_salary,
                gross_salary=calc.gross_salary,
                total_deductions=calc.total_deductions,
                net_salary=calc.net_salary,
                status=calc.status.value,
                paid=calc.status == PayrollStatus.PAID,
            )
            report_lines.append(line)
        
        # Build report response
        report = PayrollReportResponseDTO(
            payroll_period_id=period.id,
            payroll_period=period.name,
            period_start=period.start_date,
            period_end=period.end_date,
            generated_at=datetime.utcnow().isoformat(),
            company_name="KitchAI SIGR",
            currency="USD",
            records=report_lines,
        )
        
        # Calculate summary
        report.calculate_summary()
        
        return report
    
    def export_payroll_to_json(
        self,
        dto: PayrollReportRequestDTO,
    ) -> Dict[str, Any]:
        """
        Export payroll data as JSON for external systems.
        
        Args:
            dto: PayrollReportRequestDTO with export parameters
            
        Returns:
            Dictionary with JSON-serializable payroll data
        """
        report = self.generate_payroll_report(dto)
        
        return {
            "export_id": str(uuid.uuid4()),
            "export_date": datetime.utcnow().isoformat(),
            "export_format": "JSON",
            "payroll_report": report.dict(),
            "export_method": "API",
        }
    
    # ========================================================================
    # APPROVAL & PAYMENT WORKFLOW
    # ========================================================================
    
    def approve_payroll(
        self,
        payroll_id: str,
        approved_by: str,
    ) -> PayrollCalculationResponseDTO:
        """
        Approve a payroll calculation.
        
        Args:
            payroll_id: ID of payroll to approve
            approved_by: User ID of approver
            
        Returns:
            Updated PayrollCalculationResponseDTO
        """
        payroll = self.repository.get_payroll_calculation_by_id(payroll_id)
        if not payroll:
            raise ValueError(f"Payroll not found: {payroll_id}")
        
        payroll.set_approved(approved_by)
        saved = self.repository.save_payroll_calculation(payroll)
        
        # Build response
        employee = self.user_repo.get_user_by_id(saved.employee_id)
        period = self.repository.get_payroll_period_by_id(saved.payroll_period_id)
        
        return PayrollCalculationResponseDTO(
            id=saved.id,
            employee_id=saved.employee_id,
            employee_name=employee.get("name", "Unknown"),
            payroll_period_id=saved.payroll_period_id,
            payroll_period=period.name if period else "",
            normal_hours=saved.normal_hours,
            overtime_hours=saved.overtime_hours,
            hourly_rate=saved.hourly_rate,
            overtime_multiplier=saved.overtime_multiplier,
            base_salary=saved.base_salary,
            overtime_salary=saved.overtime_salary,
            gross_salary=saved.gross_salary,
            total_deductions=saved.total_deductions,
            net_salary=saved.net_salary,
            status=saved.status.value,
            calculated_at=saved.calculated_at,
            approved_by=saved.approved_by,
            approved_at=saved.approved_at,
            paid_at=saved.paid_at,
        )
    
    def mark_payroll_paid(self, payroll_id: str) -> PayrollCalculationResponseDTO:
        """
        Mark payroll as paid.
        
        Args:
            payroll_id: ID of payroll to mark as paid
            
        Returns:
            Updated PayrollCalculationResponseDTO
        """
        payroll = self.repository.get_payroll_calculation_by_id(payroll_id)
        if not payroll:
            raise ValueError(f"Payroll not found: {payroll_id}")
        
        payroll.set_paid()
        saved = self.repository.save_payroll_calculation(payroll)
        
        # Build response
        employee = self.user_repo.get_user_by_id(saved.employee_id)
        period = self.repository.get_payroll_period_by_id(saved.payroll_period_id)
        
        return PayrollCalculationResponseDTO(
            id=saved.id,
            employee_id=saved.employee_id,
            employee_name=employee.get("name", "Unknown"),
            payroll_period_id=saved.payroll_period_id,
            payroll_period=period.name if period else "",
            normal_hours=saved.normal_hours,
            overtime_hours=saved.overtime_hours,
            hourly_rate=saved.hourly_rate,
            overtime_multiplier=saved.overtime_multiplier,
            base_salary=saved.base_salary,
            overtime_salary=saved.overtime_salary,
            gross_salary=saved.gross_salary,
            total_deductions=saved.total_deductions,
            net_salary=saved.net_salary,
            status=saved.status.value,
            calculated_at=saved.calculated_at,
            approved_by=saved.approved_by,
            approved_at=saved.approved_at,
            paid_at=saved.paid_at,
        )
