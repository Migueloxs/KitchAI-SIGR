"""
Attendance Repository - Data access layer for attendance records and alerts
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
import uuid

from src.modules.Attendance.domain.entities import AttendanceRecord, AttendanceStatus, AttendanceAlert, AlertType, AlertSeverity
from src.shared.infrastructure.database.turso_connection import get_turso_client


class AttendanceRepository:
    """Repository for Attendance Records and Alerts"""
    
    def __init__(self):
        self.client = get_turso_client()
    
    # ============= ATTENDANCE RECORD OPERATIONS =============
    
    def create_attendance_record(self, record: AttendanceRecord) -> AttendanceRecord:
        """Create a new attendance record (check-in)"""
        self.client.execute(
            """
            INSERT INTO attendance_records 
            (id, employee_id, shift_assignment_id, check_in_time, status, is_late, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                record.id,
                record.employee_id,
                record.shift_assignment_id,
                record.check_in_time.isoformat(),
                record.status.value,
                1 if record.is_late else 0,
                record.created_at.isoformat(),
                record.updated_at.isoformat(),
            ],
        )
        return record
    
    def update_checkout(
        self, 
        record_id: str, 
        check_out_time: datetime,
        duration_minutes: Optional[int] = None
    ) -> Optional[AttendanceRecord]:
        """Update check-out time for an attendance record"""
        self.client.execute(
            """
            UPDATE attendance_records 
            SET check_out_time = ?, status = ?, duration_minutes = ?, updated_at = ?
            WHERE id = ?
            """,
            [
                check_out_time.isoformat(),
                AttendanceStatus.CHECKED_OUT.value,
                duration_minutes,
                datetime.now().isoformat(),
                record_id,
            ],
        )
        return self.get_attendance_record_by_id(record_id)
    
    def get_attendance_record_by_id(self, record_id: str) -> Optional[AttendanceRecord]:
        """Get an attendance record by ID"""
        result = self.client.execute(
            """
            SELECT id, employee_id, shift_assignment_id, check_in_time, check_out_time, 
                   duration_minutes, status, is_late, late_by_minutes, notes, created_at, updated_at
            FROM attendance_records
            WHERE id = ?
            """,
            [record_id],
        )
        
        if not result.rows:
            return None
        
        return self._map_to_attendance_record(result.rows[0])
    
    def get_today_attendance_for_employee(self, employee_id: str) -> Optional[AttendanceRecord]:
        """Get today's attendance record for an employee"""
        result = self.client.execute(
            """
            SELECT id, employee_id, shift_assignment_id, check_in_time, check_out_time, 
                   duration_minutes, status, is_late, late_by_minutes, notes, created_at, updated_at
            FROM attendance_records
            WHERE employee_id = ? AND date(check_in_time) = date('now')
            ORDER BY check_in_time DESC
            LIMIT 1
            """,
            [employee_id],
        )
        
        if not result.rows:
            return None
        
        return self._map_to_attendance_record(result.rows[0])
    
    def get_attendance_records_for_date_range(
        self,
        employee_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[AttendanceRecord], int]:
        """Get attendance records for a date range"""
        query = "SELECT id, employee_id, shift_assignment_id, check_in_time, check_out_time, duration_minutes, status, is_late, late_by_minutes, notes, created_at, updated_at FROM attendance_records WHERE 1=1"
        params = []
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        if start_date:
            query += " AND date(check_in_time) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date(check_in_time) <= ?"
            params.append(end_date.isoformat())
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM attendance_records WHERE 1=1"
        if employee_id:
            count_query += " AND employee_id = ?"
        if start_date:
            count_query += " AND date(check_in_time) >= ?"
        if end_date:
            count_query += " AND date(check_in_time) <= ?"
        
        count_result = self.client.execute(count_query, params)
        total_count = count_result.rows[0][0] if count_result.rows else 0
        
        query += " ORDER BY check_in_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        result = self.client.execute(query, params)
        
        records = [self._map_to_attendance_record(row) for row in result.rows]
        
        return records, total_count
    
    def mark_as_late(self, record_id: str, late_minutes: int) -> Optional[AttendanceRecord]:
        """Mark an attendance record as late"""
        self.client.execute(
            """
            UPDATE attendance_records 
            SET is_late = 1, late_by_minutes = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            [
                late_minutes,
                AttendanceStatus.LATE.value,
                datetime.now().isoformat(),
                record_id,
            ],
        )
        return self.get_attendance_record_by_id(record_id)
    
    def _map_to_attendance_record(self, row: tuple) -> AttendanceRecord:
        """Map database row to AttendanceRecord entity"""
        return AttendanceRecord(
            id=row[0],
            employee_id=row[1],
            shift_assignment_id=row[2],
            check_in_time=datetime.fromisoformat(row[3]) if isinstance(row[3], str) else row[3],
            check_out_time=datetime.fromisoformat(row[4]) if row[4] and isinstance(row[4], str) else row[4],
            duration_minutes=row[5],
            status=AttendanceStatus(row[6]),
            is_late=bool(row[7]),
            late_by_minutes=row[8],
            notes=row[9],
            created_at=datetime.fromisoformat(row[10]) if isinstance(row[10], str) else row[10],
            updated_at=datetime.fromisoformat(row[11]) if isinstance(row[11], str) else row[11],
        )
    
    # ============= ATTENDANCE ALERT OPERATIONS =============
    
    def create_alert(self, alert: AttendanceAlert) -> AttendanceAlert:
        """Create a new attendance alert"""
        self.client.execute(
            """
            INSERT INTO attendance_alerts 
            (id, employee_id, alert_type, description, severity, shift_assignment_id, 
             referenced_attendance_id, is_acknowledged, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                alert.id,
                alert.employee_id,
                alert.alert_type.value,
                alert.description,
                alert.severity.value,
                alert.shift_assignment_id,
                alert.referenced_attendance_id,
                1 if alert.is_acknowledged else 0,
                alert.created_at.isoformat(),
                alert.updated_at.isoformat(),
            ],
        )
        return alert
    
    def get_alert_by_id(self, alert_id: str) -> Optional[AttendanceAlert]:
        """Get an alert by ID"""
        result = self.client.execute(
            """
            SELECT id, employee_id, alert_type, description, severity, shift_assignment_id,
                   referenced_attendance_id, is_acknowledged, acknowledged_by, acknowledged_at,
                   auto_resolved, resolved_at, created_at, updated_at
            FROM attendance_alerts
            WHERE id = ?
            """,
            [alert_id],
        )
        
        if not result.rows:
            return None
        
        return self._map_to_alert(result.rows[0])
    
    def get_pending_alerts(self, employee_id: Optional[str] = None) -> List[AttendanceAlert]:
        """Get pending (unacknowledged) alerts"""
        query = "SELECT id, employee_id, alert_type, description, severity, shift_assignment_id, referenced_attendance_id, is_acknowledged, acknowledged_by, acknowledged_at, auto_resolved, resolved_at, created_at, updated_at FROM attendance_alerts WHERE is_acknowledged = 0 AND auto_resolved = 0"
        params = []
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        query += " ORDER BY created_at DESC"
        
        result = self.client.execute(query, params)
        
        return [self._map_to_alert(row) for row in result.rows]
    
    def get_alerts_for_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[AttendanceAlert], int]:
        """Get alerts for an employee in a date range"""
        query = "SELECT id, employee_id, alert_type, description, severity, shift_assignment_id, referenced_attendance_id, is_acknowledged, acknowledged_by, acknowledged_at, auto_resolved, resolved_at, created_at, updated_at FROM attendance_alerts WHERE employee_id = ?"
        params = [employee_id]
        
        if start_date:
            query += " AND date(created_at) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date(created_at) <= ?"
            params.append(end_date.isoformat())
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM attendance_alerts WHERE employee_id = ?"
        count_params = [employee_id]
        if start_date:
            count_query += " AND date(created_at) >= ?"
            count_params.append(start_date.isoformat())
        if end_date:
            count_query += " AND date(created_at) <= ?"
            count_params.append(end_date.isoformat())
        
        count_result = self.client.execute(count_query, count_params)
        total_count = count_result.rows[0][0] if count_result.rows else 0
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        result = self.client.execute(query, params)
        
        alerts = [self._map_to_alert(row) for row in result.rows]
        
        return alerts, total_count
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        acknowledged_at: Optional[datetime] = None,
    ) -> Optional[AttendanceAlert]:
        """Acknowledge an alert"""
        ack_time = (acknowledged_at or datetime.now()).isoformat()
        self.client.execute(
            """
            UPDATE attendance_alerts 
            SET is_acknowledged = 1, acknowledged_by = ?, acknowledged_at = ?, updated_at = ?
            WHERE id = ?
            """,
            [
                acknowledged_by,
                ack_time,
                datetime.now().isoformat(),
                alert_id,
            ],
        )
        return self.get_alert_by_id(alert_id)
    
    def auto_resolve_alert(self, alert_id: str) -> Optional[AttendanceAlert]:
        """Auto-resolve an alert (e.g., employee checks in before manual action)"""
        self.client.execute(
            """
            UPDATE attendance_alerts 
            SET auto_resolved = 1, resolved_at = ?, updated_at = ?
            WHERE id = ?
            """,
            [
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                alert_id,
            ],
        )
        return self.get_alert_by_id(alert_id)
    
    def _map_to_alert(self, row: tuple) -> AttendanceAlert:
        """Map database row to AttendanceAlert entity"""
        return AttendanceAlert(
            id=row[0],
            employee_id=row[1],
            alert_type=AlertType(row[2]),
            description=row[3],
            severity=AlertSeverity(row[4]),
            shift_assignment_id=row[5],
            referenced_attendance_id=row[6],
            is_acknowledged=bool(row[7]),
            acknowledged_by=row[8],
            acknowledged_at=datetime.fromisoformat(row[9]) if row[9] and isinstance(row[9], str) else row[9],
            auto_resolved=bool(row[10]),
            resolved_at=datetime.fromisoformat(row[11]) if row[11] and isinstance(row[11], str) else row[11],
            created_at=datetime.fromisoformat(row[12]) if isinstance(row[12], str) else row[12],
            updated_at=datetime.fromisoformat(row[13]) if isinstance(row[13], str) else row[13],
        )
