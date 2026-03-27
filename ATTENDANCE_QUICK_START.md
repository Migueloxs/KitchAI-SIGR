# Attendance Control System - Quick Start Guide

## What Was Implemented

A complete **Attendance Control and Entry/Exit Registration System** for KitchAI SIGR with:

✅ **Check-In/Check-Out** - Employees register arrival and departure with secure JWT authentication
✅ **Automatic Late Detection** - System marks late arrivals within configurable tolerance (default: 15 min)
✅ **Alert System** - Automatic alerts when employees miss check-in deadline (CA2)
✅ **Comprehensive Reports** - Attendance history, statistics, and daily summaries (CA3)
✅ **Shift Integration** - Automatic linking to employee shift assignments
✅ **Role-Based Access** - Admin, Supervisor, and Employee permission levels

## File Structure

```
src/modules/Attendance/
├── domain/entities/
│   ├── attendance_record.py - Check-in/check-out records
│   └── attendance_alert.py - Alert management
├── application/
│   ├── dto/__init__.py - All request/response DTOs
│   └── usecases/attendance_service.py - Business logic
├── infrastructure/
│   ├── api/attendance_router.py - REST endpoints (11 endpoints)
│   └── repositories/attendance_repository.py - Database access
```

## Database Changes

**Migration File**: `src/shared/infrastructure/database/migrations/versions/008_create_attendance_tables.sql`

**Tables Created**:
- `attendance_records` - Check-in/check-out events
- `attendance_alerts` - Alerts and acknowledgments
- `attendance_check_log` - Daily check-in status

**Views Created**:
- `today_attendance_summary` - Real-time attendance status
- `attendance_report_summary` - Historical data

## Key API Endpoints

### Check-In / Check-Out (Employee)
```
POST   /api/attendance/check-in          Check in for the day
POST   /api/attendance/check-out         Check out from work
GET    /api/attendance/today             View today's record
GET    /api/attendance/history           View attendance history
```

### Alerts (Supervisor/Admin)
```
POST   /api/attendance/alerts/check-missing-checkins   Generate missing check-in alerts
GET    /api/attendance/alerts/pending                  View pending alerts
POST   /api/attendance/alerts/{id}/acknowledge         Acknowledge an alert
GET    /api/attendance/alerts                          View all alerts
```

### Reports (Supervisor/Admin)
```
GET    /api/attendance/reports/today           Today's attendance summary
GET    /api/attendance/reports/attendance      Detailed attendance report
GET    /api/attendance/statistics              Employee attendance statistics
```

## How To Use

### 1. Deploy Database Migration

The migration will run automatically when the API starts if you have migrations enabled:

```python
# In main.py (already done)
from src.shared.infrastructure.database.migrations.migration_runner import run_migrations
run_migrations(turso_db)
```

### 2. Employee Check-In

```bash
curl -X POST http://localhost:8000/api/attendance/check-in \
  -H "Authorization: Bearer {employee_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "notes": "Arrived on time"
  }'
```

Response (201 Created):
```json
{
  "id": "att-rec-123",
  "employee_id": "emp-123",
  "status": "CHECKED_IN",
  "check_in_time": "2026-03-26T08:00:00",
  "is_late": false,
  "created_at": "2026-03-26T08:00:00"
}
```

### 3. Generate Alerts (Run Periodically)

Should be called every 15 minutes via cron or scheduler:

```bash
curl -X POST http://localhost:8000/api/attendance/alerts/check-missing-checkins \
  -H "Authorization: Bearer {admin_token}"
```

### 4. View Today's Summary (Supervisor)

```bash
curl -X GET http://localhost:8000/api/attendance/reports/today \
  -H "Authorization: Bearer {supervisor_token}"
```

Response:
```json
{
  "data": [
    {
      "employee_id": "emp-123",
      "employee_name": "Juan García",
      "status": "CHECKED_IN",
      "check_in_time": "2026-03-26T08:00:00",
      "pending_alerts": 0
    }
  ],
  "total": 1,
  "checked_in_count": 1,
  "absent_count": 0
}
```

## Configuration

### Change Tolerance Window

Default is 15 minutes after shift start. To change:

```python
from src.modules.Attendance.application.usecases.attendance_service import AttendanceService

service = AttendanceService()
service.tolerance_minutes = 20  # 20 minutes
```

### Set Up Alert Generation Scheduler

Using APScheduler (add to your app startup):

```python
from apscheduler.schedulers.background import BackgroundScheduler
from src.modules.Attendance.application.usecases.attendance_service import AttendanceService

scheduler = BackgroundScheduler()

def generate_alerts():
    service = AttendanceService()
    service.generate_no_checkin_alerts()

# Run every 15 minutes
scheduler.add_job(generate_alerts, 'interval', minutes=15)
scheduler.start()
```

Or use cron:
```bash
*/15 * * * * curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/api/attendance/alerts/check-missing-checkins
```

## Testing

### Run Unit Tests
```bash
pytest test_attendance_module.py -v
```

### Run API Tests (server must be running)
```bash
python test_attendance_api.py
```

### Verify Installation
```bash
python verify_attendance_installation.py
```

## Documentation

For complete API reference and examples, see:
- **[docs/ATTENDANCE_CONTROL_GUIDE.md](docs/ATTENDANCE_CONTROL_GUIDE.md)** - Full API documentation
- **[ATTENDANCE_IMPLEMENTATION.md](ATTENDANCE_IMPLEMENTATION.md)** - Implementation details

## Integration Points

### With Shifts Module
- Attendance automatically links to shift assignments
- Uses shift start/end times for late detection
- Validates employee is scheduled for the day

### With User Module
- Uses JWT authentication
- Enforces role-based permissions
- Logs all actions with user IDs

### With Database
- Uses Turso database with libsql client
- Follows existing migration pattern
- Implements proper indexes for performance

## Supported Alert Types

| Alert Type | Trigger | Severity |
|------------|---------|----------|
| `NO_CHECK_IN` | Employee doesn't check in within tolerance | WARNING |
| `LATE_ARRIVAL` | Employee checks in after tolerance | INFO |
| `NO_CHECK_OUT` | Employee doesn't check out by end of shift | WARNING |
| `EARLY_DEPARTURE` | Employee checks out too early | INFO |
| `ABSENT` | Employee no-show for scheduled shift | CRITICAL |

## Performance Considerations

- **Database Indexes**: Created on frequently queried columns
- **Query Pagination**: All report endpoints support limit/offset
- **Automatic Cleanup**: Auto-resolution of alerts when issue resolves
- **Efficient Lookups**: Shift associations cached in attendance record

## Security & Compliance

✅ JWT authentication required for all endpoints
✅ Role-based access control enforced
✅ Audit trail: All actions logged with user/timestamp
✅ Foreign key constraints maintain data integrity
✅ Timezone-aware timestamp handling
✅ No sensitive data in error messages

## Troubleshooting

### Alerts not generating?
1. Check that employees have shift assignments for today
2. Verify `/api/attendance/alerts/check-missing-checkins` is being called
3. Check tolerance window setting (default 15 minutes)

### Late arrivals not detected?
1. Verify shift assignment exists and is active
2. Check shift start time in database
3. Verify system time is correct

### No data in reports?
1. Confirm attendance records exist
2. Check date format in query parameters (YYYY-MM-DD)
3. Verify permissions (regular employees can only see their own data)

## What's Next

1. **Deploy Migration**: Run migrations against Turso database
2. **Configure Scheduler**: Set up cron or APScheduler for alerts
3. **Create Shift Assignments**: Assign shifts to all employees
4. **Test Workflow**: Test complete check-in/check-out flow
5. **Train Staff**: Show employees how to use check-in system
6. **Monitor**: Review alerts and attendance patterns regularly
7. **Adjust**: Fine-tune tolerance window based on actual usage

## Files Summary

### Core Implementation (9 files)
- `src/modules/Attendance/domain/entities/attendance_record.py`
- `src/modules/Attendance/domain/entities/attendance_alert.py`
- `src/modules/Attendance/application/dto/__init__.py`
- `src/modules/Attendance/application/usecases/attendance_service.py`
- `src/modules/Attendance/infrastructure/api/attendance_router.py`
- `src/modules/Attendance/infrastructure/repositories/attendance_repository.py`
- `src/shared/infrastructure/database/migrations/versions/008_create_attendance_tables.sql`

### Documentation & Tests (6 files)
- `docs/ATTENDANCE_CONTROL_GUIDE.md` - Complete API reference
- `ATTENDANCE_IMPLEMENTATION.md` - Implementation summary
- `test_attendance_module.py` - Unit tests
- `test_attendance_api.py` - Integration tests
- `verify_attendance_installation.py` - Installation verification

### Modified Files (1 file)
- `main.py` - Added attendance router and API tag

## Support & Questions

- **API Documentation**: See [docs/ATTENDANCE_CONTROL_GUIDE.md](docs/ATTENDANCE_CONTROL_GUIDE.md)
- **Examples**: Check [test_attendance_api.py](test_attendance_api.py)
- **Code Quality**: Follows hexagonal architecture pattern
- **Testing**: Run `pytest test_attendance_module.py -v`

---

**Status**: ✅ Ready for Production
**Last Updated**: March 26, 2026
**Version**: 1.0.0
