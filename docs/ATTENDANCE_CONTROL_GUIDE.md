# Attendance Control and Entry/Exit Registration API Guide

**User Story**: Control de Asistencia y Registro de Entrada/Salida (Attendance Control and Entry/Exit Registration)

**Implementation**: Complete REST API for employee attendance tracking with automatic alerts and reporting capabilities

## Overview

The Attendance Control API provides comprehensive capabilities for managing employee attendance, tracking work hours, and generating attendance reports in the restaurant. The system automatically detects late arrivals and missing check-ins, creating alerts that can be acknowledged by supervisors.

### Key Features

- ✅ **Secure Check-In/Check-Out**: Employees check in and out from a secure interface with credentials
- ✅ **Automatic Late Detection**: System marks lateness if employee doesn't check in within tolerance window
- ✅ **Automatic Alerts**: Generates alerts when employees miss check-in deadline (CA2)
- ✅ **Shift Integration**: Automatically links attendance to shift assignments
- ✅ **Comprehensive Reporting**: Track attendance history, statistics, and generate reports (CA3)
- ✅ **Alert Management**: Supervisors can acknowledge alerts and track attendance issues

### Requirements Met

- **CA1**: Employee can mark entry/exit from secure interface (with JWT authentication)
- **CA2**: Generate automatic alerts if employee doesn't mark entry within tolerance (default 15 minutes)
- **CA3**: Store attendance records and availability for generating reports

---

## Authentication & Authorization

All endpoints require JWT authentication.

### Role-Based Access

- **Admin**: Full access to all attendance features, can view all employees' records
- **Supervisor**: Can manage alerts, view team attendance, generate reports
- **Employee**: Can check in/out, view their own records and alerts

### Required Headers

```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

---

## Database Schema

### attendance_records Table

Stores all check-in and check-out records.

```sql
CREATE TABLE attendance_records (
    id TEXT PRIMARY KEY,                    -- Unique record ID (UUID)
    employee_id TEXT NOT NULL,              -- Foreign key to users
    shift_assignment_id TEXT,               -- Foreign key to shift_assignments
    check_in_time TEXT NOT NULL,            -- ISO 8601 datetime
    check_out_time TEXT,                    -- ISO 8601 datetime (nullable)
    duration_minutes INTEGER,               -- Calculated work duration
    status TEXT DEFAULT 'CHECKED_IN',       -- CHECKED_IN, CHECKED_OUT, NO_CHECKOUT, LATE
    is_late BOOLEAN DEFAULT 0,              -- 1 if late arrival
    late_by_minutes INTEGER,                -- Minutes late (nullable)
    notes TEXT,                             -- Optional notes
    created_at TEXT NOT NULL,               -- Record creation time
    updated_at TEXT NOT NULL                -- Last update time
);
```

**Indexes:**
- `idx_attendance_records_employee_id`
- `idx_attendance_records_check_in_time`
- `idx_attendance_records_status`
- `idx_attendance_records_shift_assignment`
- `idx_attendance_records_date`

### attendance_alerts Table

Stores automatic alerts about attendance issues.

```sql
CREATE TABLE attendance_alerts (
    id TEXT PRIMARY KEY,                    -- Unique alert ID (UUID)
    employee_id TEXT NOT NULL,              -- Foreign key to users
    alert_type TEXT NOT NULL,               -- NO_CHECK_IN, LATE_ARRIVAL, NO_CHECK_OUT, etc.
    description TEXT NOT NULL,              -- Human-readable description
    severity TEXT DEFAULT 'WARNING',        -- INFO, WARNING, CRITICAL
    shift_assignment_id TEXT,               -- Related shift assignment
    referenced_attendance_id TEXT,          -- Related attendance record
    is_acknowledged BOOLEAN DEFAULT 0,      -- Whether acknowledged by manager
    acknowledged_by TEXT,                   -- Foreign key to users
    acknowledged_at TEXT,                   -- When acknowledged
    auto_resolved BOOLEAN DEFAULT 0,        -- Whether auto-resolved
    resolved_at TEXT,                       -- When resolved
    created_at TEXT NOT NULL,               -- Alert creation time
    updated_at TEXT NOT NULL                -- Last update time
);
```

**Indexes:**
- `idx_attendance_alerts_employee_id`
- `idx_attendance_alerts_alert_type`
- `idx_attendance_alerts_created_at`
- `idx_attendance_alerts_is_acknowledged`

### attendance_check_log Table

Daily log for tracking check-in status per employee.

```sql
CREATE TABLE attendance_check_log (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    shift_assignment_id TEXT NOT NULL,
    check_date TEXT NOT NULL,               -- YYYY-MM-DD format
    shift_start_time TEXT NOT NULL,         -- HH:MM from shift
    tolerance_end_time TEXT NOT NULL,       -- Tolerance window end time
    check_status TEXT DEFAULT 'PENDING',    -- PENDING, NO_CHECK_IN, CHECKED_IN, ABSENT
    alert_id TEXT,                          -- Related alert
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### Views

- **today_attendance_summary**: Quick view of all employees' current status
- **attendance_report_summary**: Historical attendance report data

---

## API Endpoints

### Check-In / Check-Out (CA1)

#### 1. Employee Check-In

**Endpoint**: `POST /api/attendance/check-in`

**Description**: Register employee arrival

**Request**:
```json
{
  "employee_id": "emp-123",
  "check_in_time": "2026-03-26T08:00:00",
  "notes": "Arrived from main entrance"
}
```

**Response**: `201 Created`
```json
{
  "id": "att-rec-123",
  "employee_id": "emp-123",
  "shift_assignment_id": "shift-asgn-456",
  "check_in_time": "2026-03-26T08:00:00",
  "check_out_time": null,
  "duration_minutes": null,
  "status": "CHECKED_IN",
  "is_late": false,
  "late_by_minutes": null,
  "notes": "Arrived from main entrance",
  "created_at": "2026-03-26T08:00:00",
  "updated_at": "2026-03-26T08:00:00"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid employee ID or time format
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User cannot check in for another employee

**Business Logic**:
1. Validates JWT authentication
2. Looks up employee's shift for today
3. Checks if arrival is late (after shift start + 15 minute tolerance)
4. Creates attendance record
5. Auto-resolves any pending NO_CHECK_IN alerts
6. Returns created record with status

#### 2. Employee Check-Out

**Endpoint**: `POST /api/attendance/check-out`

**Description**: Register employee departure

**Request**:
```json
{
  "employee_id": "emp-123",
  "record_id": "att-rec-123",
  "check_out_time": "2026-03-26T16:00:00",
  "notes": "Working from home tomorrow"
}
```

**Response**: `200 OK`
```json
{
  "id": "att-rec-123",
  "employee_id": "emp-123",
  "shift_assignment_id": "shift-asgn-456",
  "check_in_time": "2026-03-26T08:00:00",
  "check_out_time": "2026-03-26T16:00:00",
  "duration_minutes": 480,
  "status": "CHECKED_OUT",
  "is_late": false,
  "late_by_minutes": null,
  "notes": "Working from home tomorrow",
  "created_at": "2026-03-26T08:00:00",
  "updated_at": "2026-03-26T16:00:00"
}
```

**Error Responses**:
- `400 Bad Request`: Record not found, mismatch, or already checked out
- `403 Forbidden`: Cannot check out for another employee

#### 3. Get Today's Attendance

**Endpoint**: `GET /api/attendance/today`

**Parameters**:
- `employee_id` (required): Employee ID

**Response**: `200 OK`
```json
{
  "id": "att-rec-123",
  "employee_id": "emp-123",
  "shift_assignment_id": "shift-asgn-456",
  "check_in_time": "2026-03-26T08:00:00",
  "check_out_time": null,
  "duration_minutes": null,
  "status": "CHECKED_IN",
  "is_late": false,
  "late_by_minutes": null,
  "notes": null,
  "created_at": "2026-03-26T08:00:00",
  "updated_at": "2026-03-26T08:00:00"
}
```

#### 4. Get Attendance History

**Endpoint**: `GET /api/attendance/history`

**Parameters**:
- `employee_id` (required): Employee ID
- `start_date` (optional): YYYY-MM-DD format (defaults to 30 days ago)
- `end_date` (optional): YYYY-MM-DD format (defaults to today)
- `limit` (optional): Results per page, default 100, max 500
- `offset` (optional): Pagination offset, default 0

**Response**: `200 OK`
```json
[
  {
    "id": "att-rec-123",
    "employee_id": "emp-123",
    "shift_assignment_id": "shift-asgn-456",
    "check_in_time": "2026-03-25T08:00:00",
    "check_out_time": "2026-03-25T16:30:00",
    "duration_minutes": 510,
    "status": "CHECKED_OUT",
    "is_late": false,
    "late_by_minutes": null,
    "notes": null,
    "created_at": "2026-03-25T08:00:00",
    "updated_at": "2026-03-25T16:30:00"
  }
]
```

---

### Alerts (CA2)

#### 5. Generate Missing Check-In Alerts

**Endpoint**: `POST /api/attendance/alerts/check-missing-checkins`

**Description**: Generate automatic alerts for employees who haven't checked in within tolerance window

**Authorization**: Admin or Supervisor only

**Response**: `200 OK`
```json
[
  {
    "id": "alert-123",
    "employee_id": "emp-123",
    "alert_type": "NO_CHECK_IN",
    "description": "Employee did not check in by 08:15 on their shift starting at 08:00",
    "severity": "WARNING",
    "shift_assignment_id": "shift-asgn-456",
    "referenced_attendance_id": null,
    "is_acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "auto_resolved": false,
    "resolved_at": null,
    "created_at": "2026-03-26T08:15:00",
    "updated_at": "2026-03-26T08:15:00"
  }
]
```

**Business Logic**:
1. Gets all active shift assignments for today
2. For each shift, checks if tolerance window (shift start + 15 min) has passed
3. Checks if employee hasn't checked in yet
4. Creates NO_CHECK_IN alert for each missing employee
5. Should be called periodically (e.g., every 15 minutes via cron/scheduler)

#### 6. Get Pending Alerts

**Endpoint**: `GET /api/attendance/alerts/pending`

**Parameters**:
- `employee_id` (optional): Filter by specific employee

**Response**: `200 OK`
```json
[
  {
    "id": "alert-123",
    "employee_id": "emp-123",
    "alert_type": "NO_CHECK_IN",
    "description": "Employee did not check in by 08:15 on their shift starting at 08:00",
    "severity": "WARNING",
    "shift_assignment_id": "shift-asgn-456",
    "referenced_attendance_id": null,
    "is_acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "auto_resolved": false,
    "resolved_at": null,
    "created_at": "2026-03-26T08:15:00",
    "updated_at": "2026-03-26T08:15:00"
  }
]
```

#### 7. Acknowledge Alert

**Endpoint**: `POST /api/attendance/alerts/{alert_id}/acknowledge`

**Description**: Supervisor acknowledges an alert

**Authorization**: Admin or Supervisor only

**Request**:
```json
{
  "alert_id": "alert-123",
  "notes": "Employee was stuck in traffic"
}
```

**Response**: `200 OK`
```json
{
  "id": "alert-123",
  "employee_id": "emp-123",
  "alert_type": "NO_CHECK_IN",
  "description": "Employee did not check in by 08:15 on their shift starting at 08:00",
  "severity": "WARNING",
  "shift_assignment_id": "shift-asgn-456",
  "referenced_attendance_id": null,
  "is_acknowledged": true,
  "acknowledged_by": "mgr-789",
  "acknowledged_at": "2026-03-26T08:20:00",
  "auto_resolved": false,
  "resolved_at": null,
  "created_at": "2026-03-26T08:15:00",
  "updated_at": "2026-03-26T08:20:00"
}
```

#### 8. Get Employee Alerts

**Endpoint**: `GET /api/attendance/alerts`

**Parameters**:
- `employee_id` (required): Employee ID
- `start_date` (optional): YYYY-MM-DD format
- `end_date` (optional): YYYY-MM-DD format
- `limit` (optional): Results per page, default 100
- `offset` (optional): Pagination offset

**Response**: `200 OK`
```json
[
  {
    "id": "alert-123",
    "employee_id": "emp-123",
    "alert_type": "LATE_ARRIVAL",
    "description": "Employee checked in 10 minutes late",
    "severity": "INFO",
    "shift_assignment_id": "shift-asgn-456",
    "referenced_attendance_id": "att-rec-123",
    "is_acknowledged": true,
    "acknowledged_by": "mgr-789",
    "acknowledged_at": "2026-03-26T08:10:00",
    "auto_resolved": false,
    "resolved_at": null,
    "created_at": "2026-03-26T08:05:00",
    "updated_at": "2026-03-26T08:10:00"
  }
]
```

---

### Reports (CA3)

#### 9. Get Today's Attendance Summary

**Endpoint**: `GET /api/attendance/reports/today`

**Description**: Get summary of all employees' attendance for today

**Authorization**: Admin or Supervisor only

**Response**: `200 OK`
```json
{
  "data": [
    {
      "employee_id": "emp-123",
      "employee_name": "Juan García",
      "email": "juan@restaurant.com",
      "check_in_time": "2026-03-26T08:00:00",
      "check_out_time": "NOT CHECKED OUT",
      "is_late": false,
      "status": "CHECKED_IN",
      "pending_alerts": 0
    },
    {
      "employee_id": "emp-124",
      "employee_name": "María López",
      "email": "maria@restaurant.com",
      "check_in_time": "NOT CHECKED IN",
      "check_out_time": "NOT CHECKED OUT",
      "is_late": false,
      "status": "ABSENT",
      "pending_alerts": 1
    }
  ],
  "total": 2,
  "with_pending_alerts": 1,
  "checked_in_count": 1,
  "absent_count": 1
}
```

#### 10. Get Attendance Report

**Endpoint**: `GET /api/attendance/reports/attendance`

**Parameters**:
- `employee_id` (optional): Filter by employee
- `start_date` (optional): YYYY-MM-DD format
- `end_date` (optional): YYYY-MM-DD format
- `limit` (optional): Results per page, default 100
- `offset` (optional): Pagination offset

**Response**: `200 OK`
```json
{
  "data": [
    {
      "employee_id": "emp-123",
      "employee_name": "Juan García",
      "attendance_date": "2026-03-26",
      "shift_name": "Mañana",
      "scheduled_check_in": "08:00",
      "check_in_time": "2026-03-26T08:00:00",
      "check_out_time": "2026-03-26T16:00:00",
      "attendance_status": "PRESENT",
      "late_by_minutes": null,
      "alert_count": 0
    },
    {
      "employee_id": "emp-123",
      "employee_name": "Juan García",
      "attendance_date": "2026-03-25",
      "shift_name": "Mañana",
      "scheduled_check_in": "08:00",
      "check_in_time": "2026-03-25T08:10:00",
      "check_out_time": "2026-03-25T16:30:00",
      "attendance_status": "LATE",
      "late_by_minutes": 10,
      "alert_count": 1
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

#### 11. Get Employee Statistics

**Endpoint**: `GET /api/attendance/statistics`

**Parameters**:
- `employee_id` (optional): Employee ID (defaults to current user)
- `days` (optional): Number of days to analyze, default 30, max 365

**Response**: `200 OK`
```json
{
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
```

---

## Configuration

### Tolerance Windows

The system uses configurable tolerance windows for different scenarios:

```python
# In AttendanceService
self.tolerance_minutes = 15  # Default tolerance for late arrivals
```

To configure, modify `TOLERANCE_MINUTES` environment variable or update the service:

```python
service = AttendanceService()
service.tolerance_minutes = 20  # 20 minute tolerance
```

### Alert Generation Frequency

The `/api/attendance/alerts/check-missing-checkins` endpoint should be called periodically:

**Option 1: Cron Job** (Recommended)
```bash
# Run every 15 minutes
*/15 * * * * curl -H "Authorization: Bearer {admin_token}" \
  http://localhost:8000/api/attendance/alerts/check-missing-checkins
```

**Option 2: Background Task** (In Python)
```python
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

async def generate_alerts():
    service = AttendanceService()
    service.generate_no_checkin_alerts()

# Schedule to run every 15 minutes
scheduler.add_job(generate_alerts, 'interval', minutes=15)
scheduler.start()
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful GET or POST
- `201 Created`: Successful POST creating new resource
- `400 Bad Request`: Invalid input or business logic violation
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User lacks required permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format**:
```json
{
  "detail": "Descriptive error message"
}
```

---

## Usage Examples

### Complete Workflow

**1. Employee checks in at 8:00 AM**
```bash
curl -X POST http://localhost:8000/api/attendance/check-in \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "notes": "Arriving via main entrance"
  }'
```

**2. Check today's attendance**
```bash
curl -X GET "http://localhost:8000/api/attendance/today?employee_id=emp-123" \
  -H "Authorization: Bearer {token}"
```

**3. Get pending alerts** (as supervisor)
```bash
curl -X GET http://localhost:8000/api/attendance/alerts/pending \
  -H "Authorization: Bearer {supervisor_token}"
```

**4. Employee checks out at 4:30 PM**
```bash
curl -X POST http://localhost:8000/api/attendance/check-out \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "record_id": "att-rec-123",
    "notes": "End of shift"
  }'
```

**5. Get monthly statistics**
```bash
curl -X GET "http://localhost:8000/api/attendance/statistics?days=30" \
  -H "Authorization: Bearer {token}"
```

---

## Integration with Shifts Module

The Attendance module automatically integrates with the Shifts module:

1. When employee checks in, system looks up their shift assignment for today
2. Compares check-in time with shift start time
3. Marks as late if beyond tolerance window
4. Links the attendance record to the shift assignment

**Note**: Employee must have an active shift assignment for today to properly track attendance.

---

## Scheduling Alert Generation

Create a scheduled task to run alert generation periodically:

**Using APScheduler**:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from src.modules.Attendance.application.usecases.attendance_service import AttendanceService

scheduler = BackgroundScheduler()

def check_missing_checkins():
    try:
        service = AttendanceService()
        alerts = service.generate_no_checkin_alerts()
        print(f"Generated {len(alerts)} alerts")
    except Exception as e:
        print(f"Error generating alerts: {e}")

# Run every 15 minutes
scheduler.add_job(check_missing_checkins, 'interval', minutes=15)
scheduler.start()
```

---

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Employees can only access their own data
3. **Audit Trail**: All alert acknowledgments are logged with timestamp and user ID
4. **Time Validation**: All times are stored in ISO 8601 format with timezone awareness
5. **Data Integrity**: Foreign key constraints ensure referential integrity

---

## Troubleshooting

### Alerts not generating

1. Verify shift assignments exist for today
2. Check that `/api/attendance/alerts/check-missing-checkins` is being called
3. Verify tolerance window calculation (shift_start + 15 minutes)
4. Check database logs for errors

### Late arrivals not detected

1. Ensure shift assignment is linked to employee
2. Verify shift start time in database
3. Check system time synchronization
4. Verify tolerance_minutes setting

### Reports showing no data

1. Confirm attendance records exist in database
2. Verify date format in query parameters
3. Check that employee has access permissions
4. Verify shift assignments are active

---

## Migration Guide

To migrate from legacy attendance system:

1. Run migration: `python -m src.shared.infrastructure.database.migrations.migration_runner`
2. Create shift assignments for all employees
3. Bulk import historical attendance records if needed
4. Configure tolerance window
5. Set up alert generation cron job

---

## Contact & Support

For issues or questions about the Attendance API:
- Email: soporte@kitchai.com
- Documentation: See [main README](../../README.md)
