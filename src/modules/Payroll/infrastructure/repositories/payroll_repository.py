"""
Payroll repository - Data access layer for payroll operations.

This repository handles all database operations for payroll management,
following the repository pattern for data abstraction.
"""

import uuid
from typing import List, Optional, Dict, Any
from src.shared.infrastructure.database.database_handler import DatabaseHandler
from src.modules.Payroll.domain.entities import (
    PayrollPeriod,
    WorkHours,
    PayrollAbsence,
    PayrollDeduction,
    PayrollCalculation,
    AbsenceType,
    DeductionType,
    PayrollStatus,
)


class PayrollRepository:
    """Repository for payroll data access."""
    
    def __init__(self, db_handler: DatabaseHandler):
        """
        Initialize payroll repository.
        
        Args:
            db_handler: DatabaseHandler instance for database operations
        """
        self.db = db_handler
    
    # ========================================================================
    # PAYROLL PERIOD OPERATIONS
    # ========================================================================
    
    def save_payroll_period(self, period: PayrollPeriod) -> PayrollPeriod:
        """Save a payroll period."""
        query = """
            INSERT INTO payroll_periods 
            (id, name, period_type, start_date, end_date, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                is_active = excluded.is_active,
                updated_at = excluded.updated_at
        """
        
        self.db.execute(
            query,
            (
                period.id,
                period.name,
                period.period_type.value,
                period.start_date,
                period.end_date,
                1 if period.is_active else 0,
                period.created_at,
                period.updated_at,
            ),
        )
        
        return period
    
    def get_payroll_period_by_id(self, period_id: str) -> Optional[PayrollPeriod]:
        """Get payroll period by ID."""
        query = """
            SELECT id, name, period_type, start_date, end_date, is_active, created_at, updated_at
            FROM payroll_periods
            WHERE id = ?
        """
        
        result = self.db.fetch_one(query, (period_id,))
        
        if not result:
            return None
        
        return self._row_to_payroll_period(result)
    
    def get_active_payroll_periods(self) -> List[PayrollPeriod]:
        """Get all active payroll periods."""
        query = """
            SELECT id, name, period_type, start_date, end_date, is_active, created_at, updated_at
            FROM payroll_periods
            WHERE is_active = 1
            ORDER BY start_date DESC
        """
        
        results = self.db.fetch_all(query)
        
        return [self._row_to_payroll_period(row) for row in results]
    
    def get_payroll_period_for_date(self, date_str: str) -> Optional[PayrollPeriod]:
        """Get payroll period containing a specific date."""
        query = """
            SELECT id, name, period_type, start_date, end_date, is_active, created_at, updated_at
            FROM payroll_periods
            WHERE start_date <= ? AND end_date >= ?
            LIMIT 1
        """
        
        result = self.db.fetch_one(query, (date_str, date_str))
        
        if not result:
            return None
        
        return self._row_to_payroll_period(result)
    
    def get_all_payroll_periods(self) -> List[PayrollPeriod]:
        """Get all payroll periods."""
        query = """
            SELECT id, name, period_type, start_date, end_date, is_active, created_at, updated_at
            FROM payroll_periods
            ORDER BY start_date DESC
        """
        
        results = self.db.fetch_all(query)
        
        return [self._row_to_payroll_period(row) for row in results]
    
    # ========================================================================
    # WORK HOURS OPERATIONS
    # ========================================================================
    
    def save_work_hours(self, work_hours: WorkHours) -> WorkHours:
        """Save work hours."""
        query = """
            INSERT INTO work_hours 
            (id, employee_id, payroll_period_id, normal_hours, overtime_hours, total_hours, 
             minutes_late, times_late, notes, calculated_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, payroll_period_id) DO UPDATE SET
                normal_hours = excluded.normal_hours,
                overtime_hours = excluded.overtime_hours,
                total_hours = excluded.total_hours,
                minutes_late = excluded.minutes_late,
                times_late = excluded.times_late,
                notes = excluded.notes,
                calculated_at = excluded.calculated_at,
                updated_at = excluded.updated_at
        """
        
        self.db.execute(
            query,
            (
                work_hours.id,
                work_hours.employee_id,
                work_hours.payroll_period_id,
                work_hours.normal_hours,
                work_hours.overtime_hours,
                work_hours.total_hours,
                work_hours.minutes_late,
                work_hours.times_late,
                work_hours.notes,
                work_hours.calculated_at,
                work_hours.created_at,
                work_hours.updated_at,
            ),
        )
        
        return work_hours
    
    def get_work_hours(
        self,
        employee_id: str,
        payroll_period_id: str,
    ) -> Optional[WorkHours]:
        """Get work hours for employee and period."""
        query = """
            SELECT id, employee_id, payroll_period_id, normal_hours, overtime_hours, total_hours,
                   minutes_late, times_late, notes, calculated_at, created_at, updated_at
            FROM work_hours
            WHERE employee_id = ? AND payroll_period_id = ?
        """
        
        result = self.db.fetch_one(query, (employee_id, payroll_period_id))
        
        if not result:
            return None
        
        return self._row_to_work_hours(result)
    
    def get_or_create_work_hours(
        self,
        employee_id: str,
        payroll_period_id: str,
    ) -> WorkHours:
        """Get existing work hours or create new one."""
        existing = self.get_work_hours(employee_id, payroll_period_id)
        
        if existing:
            return existing
        
        # Create new
        work_hours = WorkHours(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            payroll_period_id=payroll_period_id,
            normal_hours=0.0,
            overtime_hours=0.0,
            total_hours=0.0,
            minutes_late=0,
            times_late=0,
        )
        
        return self.save_work_hours(work_hours)
    
    def get_work_hours_for_period(
        self,
        payroll_period_id: str,
    ) -> List[WorkHours]:
        """Get work hours for all employees in a period."""
        query = """
            SELECT id, employee_id, payroll_period_id, normal_hours, overtime_hours, total_hours,
                   minutes_late, times_late, notes, calculated_at, created_at, updated_at
            FROM work_hours
            WHERE payroll_period_id = ?
            ORDER BY employee_id
        """
        
        results = self.db.fetch_all(query, (payroll_period_id,))
        
        return [self._row_to_work_hours(row) for row in results]
    
    # ========================================================================
    # ABSENCE OPERATIONS
    # ========================================================================
    
    def save_absence(self, absence: PayrollAbsence) -> PayrollAbsence:
        """Save an absence record."""
        query = """
            INSERT INTO payroll_absences
            (id, employee_id, absence_date, absence_type, reason, description, 
             is_paid, payroll_period_id, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                absence_type = excluded.absence_type,
                reason = excluded.reason,
                description = excluded.description,
                is_paid = excluded.is_paid,
                updated_at = excluded.updated_at
        """
        
        self.db.execute(
            query,
            (
                absence.id,
                absence.employee_id,
                absence.absence_date,
                absence.absence_type.value,
                absence.reason,
                absence.description,
                1 if absence.is_paid else 0,
                absence.payroll_period_id,
                absence.created_by,
                absence.created_at,
                absence.updated_at,
            ),
        )
        
        return absence
    
    def get_absences_for_period(
        self,
        employee_id: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """Get absence records for employee in date range."""
        query = """
            SELECT id, employee_id, absence_date, absence_type, reason, description,
                   is_paid, payroll_period_id, created_at, updated_at
            FROM payroll_absences
            WHERE employee_id = ? AND absence_date >= ? AND absence_date <= ?
            ORDER BY absence_date
        """
        
        results = self.db.fetch_all(query, (employee_id, start_date, end_date))
        
        return [self._row_dict(row) for row in results]
    
    def get_absences_by_type(
        self,
        employee_id: str,
        payroll_period_id: str,
        absence_type: str,
    ) -> List[Dict[str, Any]]:
        """Get absences of specific type."""
        query = """
            SELECT id, employee_id, absence_date, absence_type, reason, description,
                   is_paid, payroll_period_id, created_at, updated_at
            FROM payroll_absences
            WHERE employee_id = ? AND payroll_period_id = ? AND absence_type = ?
            ORDER BY absence_date
        """
        
        results = self.db.fetch_all(
            query,
            (employee_id, payroll_period_id, absence_type),
        )
        
        return [self._row_dict(row) for row in results]
    
    # ========================================================================
    # DEDUCTION OPERATIONS
    # ========================================================================
    
    def save_deduction(self, deduction: PayrollDeduction) -> PayrollDeduction:
        """Save a deduction."""
        query = """
            INSERT INTO payroll_deductions
            (id, employee_id, payroll_period_id, deduction_type, amount, reason, 
             description, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(
            query,
            (
                deduction.id,
                deduction.employee_id,
                deduction.payroll_period_id,
                deduction.deduction_type.value,
                deduction.amount,
                deduction.reason,
                deduction.description,
                deduction.created_by,
                deduction.created_at,
                deduction.updated_at,
            ),
        )
        
        return deduction
    
    def get_deductions(
        self,
        employee_id: str,
        payroll_period_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all deductions for employee in period."""
        query = """
            SELECT id, employee_id, payroll_period_id, deduction_type, amount, reason,
                   description, created_by, created_at, updated_at
            FROM payroll_deductions
            WHERE employee_id = ? AND payroll_period_id = ?
            ORDER BY created_at
        """
        
        results = self.db.fetch_all(query, (employee_id, payroll_period_id))
        
        return [self._row_dict(row) for row in results]
    
    def get_deductions_by_type(
        self,
        employee_id: str,
        payroll_period_id: str,
        deduction_type: str,
    ) -> List[Dict[str, Any]]:
        """Get deductions of specific type."""
        query = """
            SELECT id, employee_id, payroll_period_id, deduction_type, amount, reason,
                   description, created_by, created_at, updated_at
            FROM payroll_deductions
            WHERE employee_id = ? AND payroll_period_id = ? AND deduction_type = ?
            ORDER BY created_at
        """
        
        results = self.db.fetch_all(
            query,
            (employee_id, payroll_period_id, deduction_type),
        )
        
        return [self._row_dict(row) for row in results]
    
    # ========================================================================
    # PAYROLL CALCULATION OPERATIONS
    # ========================================================================
    
    def save_payroll_calculation(
        self,
        calculation: PayrollCalculation,
    ) -> PayrollCalculation:
        """Save payroll calculation."""
        query = """
            INSERT INTO payroll_calculations
            (id, employee_id, payroll_period_id, normal_hours, overtime_hours, hourly_rate,
             overtime_multiplier, base_salary, overtime_salary, gross_salary, total_deductions,
             net_salary, status, calculated_at, approved_by, approved_at, paid_at,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                total_deductions = excluded.total_deductions,
                net_salary = excluded.net_salary,
                approved_by = excluded.approved_by,
                approved_at = excluded.approved_at,
                paid_at = excluded.paid_at,
                updated_at = excluded.updated_at
        """
        
        self.db.execute(
            query,
            (
                calculation.id,
                calculation.employee_id,
                calculation.payroll_period_id,
                calculation.normal_hours,
                calculation.overtime_hours,
                calculation.hourly_rate,
                calculation.overtime_multiplier,
                calculation.base_salary,
                calculation.overtime_salary,
                calculation.gross_salary,
                calculation.total_deductions,
                calculation.net_salary,
                calculation.status.value,
                calculation.calculated_at,
                calculation.approved_by,
                calculation.approved_at,
                calculation.paid_at,
                calculation.created_at,
                calculation.updated_at,
            ),
        )
        
        return calculation
    
    def get_payroll_calculation_by_id(self, payroll_id: str) -> Optional[PayrollCalculation]:
        """Get payroll calculation by ID."""
        query = """
            SELECT id, employee_id, payroll_period_id, normal_hours, overtime_hours, hourly_rate,
                   overtime_multiplier, base_salary, overtime_salary, gross_salary, total_deductions,
                   net_salary, status, calculated_at, approved_by, approved_at, paid_at,
                   created_at, updated_at
            FROM payroll_calculations
            WHERE id = ?
        """
        
        result = self.db.fetch_one(query, (payroll_id,))
        
        if not result:
            return None
        
        return self._row_to_payroll_calculation(result)
    
    def get_payroll_calculation(
        self,
        employee_id: str,
        payroll_period_id: str,
    ) -> Optional[PayrollCalculation]:
        """Get payroll calculation for employee and period."""
        query = """
            SELECT id, employee_id, payroll_period_id, normal_hours, overtime_hours, hourly_rate,
                   overtime_multiplier, base_salary, overtime_salary, gross_salary, total_deductions,
                   net_salary, status, calculated_at, approved_by, approved_at, paid_at,
                   created_at, updated_at
            FROM payroll_calculations
            WHERE employee_id = ? AND payroll_period_id = ?
            LIMIT 1
        """
        
        result = self.db.fetch_one(query, (employee_id, payroll_period_id))
        
        if not result:
            return None
        
        return self._row_to_payroll_calculation(result)
    
    def get_payroll_calculations_for_period(
        self,
        payroll_period_id: str,
    ) -> List[PayrollCalculation]:
        """Get all payroll calculations for a period."""
        query = """
            SELECT id, employee_id, payroll_period_id, normal_hours, overtime_hours, hourly_rate,
                   overtime_multiplier, base_salary, overtime_salary, gross_salary, total_deductions,
                   net_salary, status, calculated_at, approved_by, approved_at, paid_at,
                   created_at, updated_at
            FROM payroll_calculations
            WHERE payroll_period_id = ?
            ORDER BY employee_id
        """
        
        results = self.db.fetch_all(query, (payroll_period_id,))
        
        return [self._row_to_payroll_calculation(row) for row in results]
    
    def get_payroll_calculations_by_status(
        self,
        payroll_period_id: str,
        status: str,
    ) -> List[PayrollCalculation]:
        """Get payroll calculations with specific status."""
        query = """
            SELECT id, employee_id, payroll_period_id, normal_hours, overtime_hours, hourly_rate,
                   overtime_multiplier, base_salary, overtime_salary, gross_salary, total_deductions,
                   net_salary, status, calculated_at, approved_by, approved_at, paid_at,
                   created_at, updated_at
            FROM payroll_calculations
            WHERE payroll_period_id = ? AND status = ?
            ORDER BY employee_id
        """
        
        results = self.db.fetch_all(query, (payroll_period_id, status))
        
        return [self._row_to_payroll_calculation(row) for row in results]
    
    # ========================================================================
    # VIEW DATA RETRIEVAL (for reports)
    # ========================================================================
    
    def get_employee_hours_summary(
        self,
        employee_id: Optional[str] = None,
        payroll_period_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query employee_hours_summary view."""
        query = "SELECT * FROM employee_hours_summary WHERE 1=1"
        params = []
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        if payroll_period_id:
            query += " AND payroll_period_id = ?"
            params.append(payroll_period_id)
        
        query += " ORDER BY employee_name"
        
        results = self.db.fetch_all(query, tuple(params))
        
        return [self._row_dict(row) for row in results]
    
    def get_employee_absences_summary(
        self,
        employee_id: Optional[str] = None,
        payroll_period_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query employee_absences_summary view."""
        query = "SELECT * FROM employee_absences_summary WHERE 1=1"
        params = []
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        if payroll_period_id:
            query += " AND payroll_period_id = ?"
            params.append(payroll_period_id)
        
        query += " ORDER BY employee_name"
        
        results = self.db.fetch_all(query, tuple(params))
        
        return [self._row_dict(row) for row in results]
    
    def get_payroll_export_summary(
        self,
        payroll_period_id: str,
        employee_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query payroll_export_summary view."""
        query = "SELECT * FROM payroll_export_summary WHERE payroll_period_id = ?"
        params = [payroll_period_id]
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        query += " ORDER BY employee_name"
        
        results = self.db.fetch_all(query, tuple(params))
        
        return [self._row_dict(row) for row in results]
    
    # ========================================================================
    # HELPER METHODS FOR DATA CONVERSION
    # ========================================================================
    
    def _row_to_payroll_period(self, row: tuple) -> PayrollPeriod:
        """Convert database row to PayrollPeriod entity."""
        return PayrollPeriod(
            id=row[0],
            name=row[1],
            period_type=row[2],
            start_date=row[3],
            end_date=row[4],
            is_active=bool(row[5]),
            created_at=row[6],
            updated_at=row[7],
        )
    
    def _row_to_work_hours(self, row: tuple) -> WorkHours:
        """Convert database row to WorkHours entity."""
        return WorkHours(
            id=row[0],
            employee_id=row[1],
            payroll_period_id=row[2],
            normal_hours=row[3],
            overtime_hours=row[4],
            total_hours=row[5],
            minutes_late=row[6],
            times_late=row[7],
            notes=row[8],
            calculated_at=row[9],
            created_at=row[10],
            updated_at=row[11],
        )
    
    def _row_to_payroll_calculation(self, row: tuple) -> PayrollCalculation:
        """Convert database row to PayrollCalculation entity."""
        return PayrollCalculation(
            id=row[0],
            employee_id=row[1],
            payroll_period_id=row[2],
            normal_hours=row[3],
            overtime_hours=row[4],
            hourly_rate=row[5],
            overtime_multiplier=row[6],
            base_salary=row[7],
            overtime_salary=row[8],
            gross_salary=row[9],
            total_deductions=row[10],
            net_salary=row[11],
            status=PayrollStatus(row[12]),
            calculated_at=row[13],
            approved_by=row[14],
            approved_at=row[15],
            paid_at=row[16],
            created_at=row[17],
            updated_at=row[18],
        )
    
    def _row_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert row tuple to dictionary using column names."""
        # This is a simple implementation - you may need to adapt based on your DB handler
        if hasattr(row, "keys"):
            return dict(row)
        return {}
