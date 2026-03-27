# Attendance Control System - Implementation Summary

## Overview

A complete attendance tracking and control system has been implemented for the KitchAI SIGR restaurant management API. The system automatically registers employee entry/exit times, detects late arrivals, generates alerts, and provides comprehensive attendance reporting.

## Acceptance Criteria Met

✅ **CA1**: Employees can mark entry/exit from a secure interface with JWT authentication
- POST `/api/attendance/check-in` - Register arrival
- POST `/api/attendance/check-out` - Register departure
- All endpoints require valid JWT token

✅ **CA2**: Automatic alerts for missing check-ins within tolerance window
- Default tolerance: 15 minutes after shift start
- Automatic alert generation via `POST /api/attendance/alerts/check-missing-checkins`
- Alert types: NO_CHECK_IN, LATE_ARRIVAL, NO_CHECK_OUT, EARLY_DEPARTURE, ABSENT
- Auto-resolution when employee checks in despite alert

✅ **CA3**: Store attendance records and availability for reporting
- Complete attendance history stored in database
- Multiple report endpoints for analytics
- Statistics calculations (present days, absences, late arrivals, etc.)
- Export-ready data format

## Architecture

### Database Schema (Migration 008)

**Tables Created:**
1. `attendance_records` - All check-in/check-out events
2. `attendance_alerts` - Automatic and manual alerts
3. `attendance_check_log` - Daily check-in status tracking

**Views Created:**
1. `today_attendance_summary` - Real-time attendance status
2. `attendance_report_summary` - Historical attendance data

**Relationships:**
- attendance_records → users (employee_id)
- attendance_records → shift_assignments (automatic shift lookup)
- attendance_alerts → users (employee_id, acknowledged_by)
- attendance_alerts → attendance_records (referenced_attendance_id)

### Module Structure

```
src/modules/Attendance/
├── domain/
│   ├── entities/
│   │   ├── attendance_record.py (AttendanceRecord, AttendanceStatus)
│   │   └── attendance_alert.py (AttendanceAlert, AlertType, AlertSeverity)
│   └── __init__.py
├── application/
│   ├── dto/
│   │   └── __init__.py (All request/response DTOs)
│   ├── usecases/
│   │   ├── attendance_service.py (Business logic)
│   │   └── __init__.py
│   └── __init__.py
├── infrastructure/
│   ├── api/
│   │   ├── attendance_router.py (REST endpoints)
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── attendance_repository.py (Database access)
│   │   └── __init__.py
│   └── __init__.py
└── __init__.py
```

### Hexagonal Architecture Applied

- **Domain Layer**: Business entities (AttendanceRecord, AttendanceAlert)
- **Application Layer**: Use cases (AttendanceService) and DTOs
- **Infrastructure Layer**: Repositories and REST API

## API Endpoints

### Check-In / Check-Out (CA1)
- `POST /api/attendance/check-in` - Register arrival
- `POST /api/attendance/check-out` - Register departure
- `GET /api/attendance/today` - View today's record
- `GET /api/attendance/history` - View attendance history

### Alerts (CA2)
- `POST /api/attendance/alerts/check-missing-checkins` - Generate alerts
- `GET /api/attendance/alerts/pending` - View pending alerts
- `POST /api/attendance/alerts/{alert_id}/acknowledge` - Supervisor acknowledgment
- `GET /api/attendance/alerts` - View all alerts for employee

### Reports (CA3)
- `GET /api/attendance/reports/today` - Today's summary (admin/supervisor)
- `GET /api/attendance/reports/attendance` - Detailed report
- `GET /api/attendance/statistics` - Employee statistics

## Key Features Implemented

### 1. Automatic Late Detection
- Compares check-in time with shift start time
- Uses configurable tolerance window (default: 15 minutes)
- Marks attendance as LATE if beyond tolerance
- Records minutes late for reporting

### 2. Alert Generation System
- Automatic alerts when tolerance window expires
- Alert types: NO_CHECK_IN, LATE_ARRIVAL, NO_CHECK_OUT, EARLY_DEPARTURE, ABSENT
- Severity levels: INFO, WARNING, CRITICAL
- Auto-resolution when issue is resolved

### 3. Shift Integration
- Automatically links attendance to shift assignments
- Validates employee is scheduled for the day
- Uses shift times for late detection
- Handles multiple shift patterns (daily, weekly, etc.)

### 4. Comprehensive Reporting
- Daily attendance summaries
- Historical records with date filtering
- Employee statistics (present/absent days, late arrivals, work duration)
- Alert tracking per employee

### 5. Role-Based Access Control
- Employees: Check in/out, view own records
- Supervisors: View team records, acknowledge alerts
- Admins: Full access to all records and alerts

## Security Measures

1. **Authentication**: JWT token required for all endpoints
2. **Authorization**: Role-based access control enforced
3. **Data Integrity**: Foreign key constraints in database
4. **Time Handling**: ISO 8601 format with timezone awareness
5. **Audit Trail**: All alert acknowledgments logged with user ID and timestamp

## Configuration

### Tolerance Window
Default: 15 minutes after shift start time

To change:
```python
service = AttendanceService()
service.tolerance_minutes = 20  # 20 minute tolerance
```

### Alert Generation Scheduling
Should be run every 15 minutes via cron or scheduler:

```bash
*/15 * * * * curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/attendance/alerts/check-missing-checkins
```

## Testing

### Unit Tests
- `test_attendance_module.py` - Domain entities, DTOs, service logic
- Tests for: check-in, check-out, alerts, statistics

### API Tests
- `test_attendance_api.py` - End-to-end API testing
- Tests all endpoints with real HTTP requests

### Running Tests
```bash
# Unit tests
pytest test_attendance_module.py -v

# API tests (requires running server)
python test_attendance_api.py
```

## Documentation

Comprehensive API documentation created in `docs/ATTENDANCE_CONTROL_GUIDE.md`:
- Complete endpoint reference
- Request/response examples
- Error handling
- Configuration guide
- Troubleshooting section
- Integration with Shifts module
- Migration guide

## Database Migration

Migration file: `src/shared/infrastructure/database/migrations/versions/008_create_attendance_tables.sql`

**To run migration:**
```bash
python -m src.shared.infrastructure.database.migrations.migration_runner
```

**Tables created:**
- attendance_records (with 5 indexes)
- attendance_alerts (with 4 indexes)
- attendance_check_log (with 2 indexes)
- 2 views for quick reporting

## Integration Points

### 1. Shifts Module
- Attendance system automatically finds employee's shift for the day
- Uses shift start/end times for late detection
- Links attendance records to shift assignments

### 2. User Module
- Uses JWT authentication from auth_router
- Enforces role-based permissions
- Logs actions with user IDs

### 3. Database
- Uses Turso database with libsql client
- Follows existing connection pattern
- Implements proper migration versioning

## Files Modified/Created

### New Files
1. `src/modules/Attendance/` - Complete module
2. `src/shared/infrastructure/database/migrations/versions/008_create_attendance_tables.sql`
3. `test_attendance_module.py` - Unit tests
4. `test_attendance_api.py` - API tests
5. `docs/ATTENDANCE_CONTROL_GUIDE.md` - Documentation

### Modified Files
1. `main.py` - Added attendance router and API tag

## Ready for Production

✅ Database migrations ready
✅ All endpoints tested
✅ Role-based access control implemented
✅ Error handling comprehensive
✅ Documentation complete
✅ Security measures in place
✅ Integration with existing modules verified
✅ Performance indexes created
✅ Code follows hexagonal architecture pattern

## Next Steps

1. Deploy migration to Turso database
2. Configure alert generation cron job
3. Set up shift assignments for employees
4. Train staff on check-in/check-out process
5. Monitor alerts and attendance patterns
6. Adjust tolerance window based on business needs

## Support

For issues or questions:
- See `docs/ATTENDANCE_CONTROL_GUIDE.md` for API reference
- Check `test_attendance_api.py` for usage examples
- Run tests to verify functionality: `pytest test_attendance_module.py -v`
