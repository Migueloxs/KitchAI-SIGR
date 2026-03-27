"""
Attendance Service - Use cases for attendance management
Implements CA1, CA2, CA3 requirements:
- CA1: Allow employees to mark entry/exit from secure interface
- CA2: Generate automatic alerts for missing check-ins
- CA3: Store attendance records for report generation
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
import uuid

from src.modules.Attendance.domain.entities import (
    AttendanceRecord,
    AttendanceStatus,
    AttendanceAlert,
    AlertType,
    AlertSeverity,
)
from src.modules.Attendance.infrastructure.repositories.attendance_repository import AttendanceRepository
from src.modules.Attendance.application.dto import (
    CheckInRequestDTO,
    CheckOutRequestDTO,
    AttendanceRecordResponseDTO,
    AttendanceAlertResponseDTO,
    AcknowledgeAlertRequestDTO,
    AttendanceSummaryDTO,
    AttendanceReportDTO,
    AttendanceStatisticsDTO,
)
from src.shared.infrastructure.database.turso_connection import get_turso_client


class AttendanceService:
    """Service for attendance management"""
    
    def __init__(self):
        self.repository = AttendanceRepository()
        self.client = get_turso_client()
        self.tolerance_minutes = 15  # Default tolerance for late arrivals
    
    # ============= CA1: Check-In / Check-Out Operations =============
    
    def check_in(self, request: CheckInRequestDTO) -> AttendanceRecordResponseDTO:
        """
        CA1: Employee checks in
        Creates an attendance record for the day
        """
        check_in_time = request.check_in_time or datetime.now()
        record_id = str(uuid.uuid4())
        
        # Get shift assignment for today
        shift_assignment = self._get_employee_shift_for_today(request.employee_id)
        
        # Create attendance record
        record = AttendanceRecord(
            id=record_id,
            employee_id=request.employee_id,
            shift_assignment_id=shift_assignment.get("id") if shift_assignment else None,
            check_in_time=check_in_time,
            status=AttendanceStatus.CHECKED_IN,
            notes=request.notes,
        )
        
        # Check if late
        if shift_assignment:
            is_late, late_by_minutes = self._check_if_late(
                check_in_time,
                shift_assignment.get("start_time"),
                self.tolerance_minutes,
            )
            if is_late:
                record.mark_late(late_by_minutes)
        
        # Save record
        self.repository.create_attendance_record(record)
        
        # Auto-resolve any pending NO_CHECK_IN alerts for this employee today
        self._auto_resolve_no_checkin_alerts(request.employee_id)
        
        return self._record_to_response_dto(record)
    
    def check_out(self, request: CheckOutRequestDTO) -> AttendanceRecordResponseDTO:
        """
        CA1: Employee checks out
        Updates the attendance record with checkout time
        """
        check_out_time = request.check_out_time or datetime.now()
        
        # Get and validate record
        record = self.repository.get_attendance_record_by_id(request.record_id)
        if not record:
            raise ValueError(f"Attendance record {request.record_id} not found")
        
        if record.employee_id != request.employee_id:
            raise ValueError("Employee ID does not match the attendance record")
        
        if record.check_out_time is not None:
            raise ValueError("Employee has already checked out")
        
        # Update checkout
        updated_record = self.repository.update_checkout(
            request.record_id,
            check_out_time,
            duration_minutes=int((check_out_time - record.check_in_time).total_seconds() / 60),
        )
        
        if updated_record is None:
            raise ValueError("Failed to update attendance record")
        
        return self._record_to_response_dto(updated_record)
    
    def get_today_attendance(self, employee_id: str) -> Optional[AttendanceRecordResponseDTO]:
        """Get today's attendance record for an employee"""
        record = self.repository.get_today_attendance_for_employee(employee_id)
        return self._record_to_response_dto(record) if record else None
    
    def get_attendance_history(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[AttendanceRecordResponseDTO], int]:
        """Get attendance history for an employee"""
        records, total = self.repository.get_attendance_records_for_date_range(
            employee_id=employee_id,
            start_date=start_date or (date.today() - timedelta(days=30)),
            end_date=end_date or date.today(),
            limit=limit,
            offset=offset,
        )
        
        return [self._record_to_response_dto(r) for r in records], total
    
    # ============= CA2: Alert Management =============
    
    def generate_no_checkin_alerts(self) -> List[AttendanceAlertResponseDTO]:
        """
        CA2: Generate automatic alerts for employees who haven't checked in
        This should be called periodically (e.g., every 15 minutes)
        """
        alerts_created = []
        
        # Get all active shift assignments for today
        today_assignments = self._get_active_shift_assignments_for_today()
        
        for assignment in today_assignments:
            employee_id = assignment.get("employee_id")
            shift_start = assignment.get("start_time")
            
            # Calculate tolerance end time
            tolerance_end = self._add_minutes_to_time(shift_start, self.tolerance_minutes)
            current_time_str = datetime.now().strftime("%H:%M")
            
            # Check if current time is past tolerance window
            if current_time_str <= tolerance_end:
                continue
            
            # Check if employee already checked in
            today_attendance = self.repository.get_today_attendance_for_employee(employee_id)
            if today_attendance:
                continue
            
            # Create alert
            alert = AttendanceAlert(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                alert_type=AlertType.NO_CHECK_IN,
                description=f"Employee did not check in by {tolerance_end} on their shift starting at {shift_start}",
                severity=AlertSeverity.WARNING,
                shift_assignment_id=assignment.get("id"),
            )
            
            self.repository.create_alert(alert)
            alerts_created.append(self._alert_to_response_dto(alert))
        
        return alerts_created
    
    def generate_late_arrival_alert(self, record_id: str) -> AttendanceAlertResponseDTO:
        """Generate alert for a late arrival"""
        record = self.repository.get_attendance_record_by_id(record_id)
        if not record:
            raise ValueError(f"Attendance record {record_id} not found")
        
        if not record.is_late:
            raise ValueError("This attendance record is not marked as late")
        
        alert = AttendanceAlert(
            id=str(uuid.uuid4()),
            employee_id=record.employee_id,
            alert_type=AlertType.LATE_ARRIVAL,
            description=f"Employee checked in {record.late_by_minutes} minutes late",
            severity=AlertSeverity.INFO,
            shift_assignment_id=record.shift_assignment_id,
            referenced_attendance_id=record_id,
        )
        
        self.repository.create_alert(alert)
        return self._alert_to_response_dto(alert)
    
    def acknowledge_alert(self, request: AcknowledgeAlertRequestDTO, manager_id: str) -> AttendanceAlertResponseDTO:
        """Acknowledge an alert"""
        alert = self.repository.acknowledge_alert(
            request.alert_id,
            manager_id,
        )
        
        if alert is None:
            raise ValueError(f"Alert {request.alert_id} not found")
        
        return self._alert_to_response_dto(alert)
    
    def get_pending_alerts(self, employee_id: Optional[str] = None) -> List[AttendanceAlertResponseDTO]:
        """Get pending alerts"""
        alerts = self.repository.get_pending_alerts(employee_id)
        return [self._alert_to_response_dto(a) for a in alerts]
    
    def get_alerts_for_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[AttendanceAlertResponseDTO], int]:
        """Get alerts for an employee"""
        alerts, total = self.repository.get_alerts_for_employee(
            employee_id,
            start_date=start_date or (date.today() - timedelta(days=30)),
            end_date=end_date or date.today(),
            limit=limit,
            offset=offset,
        )
        
        return [self._alert_to_response_dto(a) for a in alerts], total
    
    # ============= CA3: Reports and Statistics =============
    
    def get_today_attendance_summary(self) -> List[AttendanceSummaryDTO]:
        """Get summary of all employees' attendance for today"""
        result = self.client.execute(
            """
            SELECT
                employee_id,
                employee_name,
                email,
                check_in_time,
                check_out_time,
                is_late,
                status,
                pending_alerts
            FROM today_attendance_summary
            ORDER BY employee_name
            """
        )
        
        summaries = []
        for row in result.rows:
            summaries.append(AttendanceSummaryDTO(
                employee_id=row[0],
                employee_name=row[1],
                email=row[2],
                check_in_time=row[3],
                check_out_time=row[4],
                is_late=bool(row[5]),
                status=row[6],
                pending_alerts=row[7],
            ))
        
        return summaries
    
    def get_attendance_report(
        self,
        employee_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[AttendanceReportDTO], int]:
        """Get detailed attendance report"""
        query = "SELECT employee_id, employee_name, attendance_date, shift_name, scheduled_check_in, check_in_time, check_out_time, attendance_status, late_by_minutes, alert_count FROM attendance_report_summary WHERE 1=1"
        params = []
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        if start_date:
            query += " AND date(attendance_date) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date(attendance_date) <= ?"
            params.append(end_date.isoformat())
        
        # Get total count
        count_query = "SELECT COUNT(DISTINCT attendance_date, employee_id) as count FROM attendance_report_summary WHERE 1=1"
        count_params = []
        if employee_id:
            count_query += " AND employee_id = ?"
            count_params.append(employee_id)
        if start_date:
            count_query += " AND date(attendance_date) >= ?"
            count_params.append(start_date.isoformat())
        if end_date:
            count_query += " AND date(attendance_date) <= ?"
            count_params.append(end_date.isoformat())
        
        count_result = self.client.execute(count_query, count_params)
        total_count = count_result.rows[0][0] if count_result.rows else 0
        
        query += " ORDER BY attendance_date DESC, employee_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        result = self.client.execute(query, params)
        
        reports = []
        for row in result.rows:
            reports.append(AttendanceReportDTO(
                employee_id=row[0],
                employee_name=row[1],
                attendance_date=datetime.fromisoformat(row[2]) if row[2] else None,
                shift_name=row[3],
                scheduled_check_in=row[4],
                check_in_time=datetime.fromisoformat(row[5]) if row[5] else None,
                check_out_time=datetime.fromisoformat(row[6]) if row[6] else None,
                attendance_status=row[7],
                late_by_minutes=row[8],
                alert_count=row[9],
            ))
        
        return reports, total_count
    
    def get_employee_statistics(
        self,
        employee_id: str,
        days: int = 30,
    ) -> AttendanceStatisticsDTO:
        """Get attendance statistics for an employee"""
        start_date = date.today() - timedelta(days=days)
        
        # Get all attendance records for the period
        records, _ = self.repository.get_attendance_records_for_date_range(
            employee_id=employee_id,
            start_date=start_date,
            end_date=date.today(),
            limit=1000,
        )
        
        # Get employee info
        employee_result = self.client.execute(
            "SELECT name FROM users WHERE id = ?",
            [employee_id],
        )
        employee_name = employee_result.rows[0][0] if employee_result.rows else "Unknown"
        
        # Calculate statistics
        total_working_days = len(records)
        present_days = sum(1 for r in records if r.check_in_time)
        absent_days = total_working_days - present_days
        late_arrivals = sum(1 for r in records if r.is_late)
        no_checkout_count = sum(1 for r in records if r.check_in_time and not r.check_out_time)
        
        late_times = [r.late_by_minutes for r in records if r.late_by_minutes]
        avg_late = sum(late_times) / len(late_times) if late_times else None
        
        durations = [r.duration_minutes for r in records if r.duration_minutes]
        avg_duration = sum(durations) / len(durations) if durations else None
        
        return AttendanceStatisticsDTO(
            employee_id=employee_id,
            employee_name=employee_name,
            total_working_days=total_working_days,
            present_days=present_days,
            absent_days=absent_days,
            late_arrivals=late_arrivals,
            no_checkout_count=no_checkout_count,
            average_check_in_delay_minutes=avg_late,
            average_work_duration_minutes=avg_duration,
        )
    
    # ============= Helper Methods =============
    
    def _get_employee_shift_for_today(self, employee_id: str) -> Optional[dict]:
        """Get the shift assignment for an employee for today"""
        today = date.today()
        day_of_week = today.weekday()
        
        result = self.client.execute(
            """
            SELECT sa.id, s.start_time, s.end_time, s.name
            FROM shift_assignments sa
            JOIN shifts s ON sa.shift_id = s.id
            WHERE sa.employee_id = ?
            AND s.day_of_week = ?
            AND sa.start_date <= ?
            AND (sa.end_date IS NULL OR sa.end_date >= ?)
            LIMIT 1
            """,
            [employee_id, day_of_week, today.isoformat(), today.isoformat()],
        )
        
        if not result.rows:
            return None
        
        row = result.rows[0]
        return {
            "id": row[0],
            "start_time": row[1],
            "end_time": row[2],
            "name": row[3],
        }
    
    def _get_active_shift_assignments_for_today(self) -> List[dict]:
        """Get all active shift assignments for today"""
        today = date.today()
        day_of_week = today.weekday()
        
        result = self.client.execute(
            """
            SELECT sa.id, sa.employee_id, s.start_time, s.end_time, s.name, u.name as employee_name
            FROM shift_assignments sa
            JOIN shifts s ON sa.shift_id = s.id
            JOIN users u ON sa.employee_id = u.id
            WHERE s.day_of_week = ?
            AND sa.start_date <= ?
            AND (sa.end_date IS NULL OR sa.end_date >= ?)
            ORDER BY s.start_time
            """,
            [day_of_week, today.isoformat(), today.isoformat()],
        )
        
        assignments = []
        for row in result.rows:
            assignments.append({
                "id": row[0],
                "employee_id": row[1],
                "start_time": row[2],
                "end_time": row[3],
                "shift_name": row[4],
                "employee_name": row[5],
            })
        
        return assignments
    
    def _check_if_late(
        self,
        check_in_time: datetime,
        shift_start_time_str: str,
        tolerance_minutes: int,
    ) -> Tuple[bool, Optional[int]]:
        """Check if the check-in time is late"""
        # Parse shift start time
        shift_hour, shift_minute = map(int, shift_start_time_str.split(":"))
        shift_start = check_in_time.replace(hour=shift_hour, minute=shift_minute, second=0, microsecond=0)
        
        # Add tolerance
        tolerance_end = shift_start + timedelta(minutes=tolerance_minutes)
        
        if check_in_time > tolerance_end:
            late_minutes = int((check_in_time - shift_start).total_seconds() / 60)
            return True, late_minutes
        
        return False, None
    
    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string and return the result as HH:MM"""
        hour, minute = map(int, time_str.split(":"))
        total_minutes = hour * 60 + minute + minutes
        
        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60
        
        return f"{new_hour:02d}:{new_minute:02d}"
    
    def _auto_resolve_no_checkin_alerts(self, employee_id: str) -> None:
        """Auto-resolve pending NO_CHECK_IN alerts for an employee today"""
        alerts = self.repository.get_pending_alerts(employee_id)
        
        for alert in alerts:
            if alert.alert_type == AlertType.NO_CHECK_IN:
                # Check if the alert is from today
                if alert.created_at.date() == date.today():
                    self.repository.auto_resolve_alert(alert.id)
    
    def _record_to_response_dto(self, record: AttendanceRecord) -> AttendanceRecordResponseDTO:
        """Convert AttendanceRecord to response DTO"""
        return AttendanceRecordResponseDTO(
            id=record.id,
            employee_id=record.employee_id,
            shift_assignment_id=record.shift_assignment_id,
            check_in_time=record.check_in_time,
            check_out_time=record.check_out_time,
            duration_minutes=record.duration_minutes,
            status=record.status.value,
            is_late=record.is_late,
            late_by_minutes=record.late_by_minutes,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
    
    def _alert_to_response_dto(self, alert: AttendanceAlert) -> AttendanceAlertResponseDTO:
        """Convert AttendanceAlert to response DTO"""
        return AttendanceAlertResponseDTO(
            id=alert.id,
            employee_id=alert.employee_id,
            alert_type=alert.alert_type.value,
            description=alert.description,
            severity=alert.severity.value,
            shift_assignment_id=alert.shift_assignment_id,
            referenced_attendance_id=alert.referenced_attendance_id,
            is_acknowledged=alert.is_acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            auto_resolved=alert.auto_resolved,
            resolved_at=alert.resolved_at,
            created_at=alert.created_at,
            updated_at=alert.updated_at,
        )
