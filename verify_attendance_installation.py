"""
Verification script for Attendance module installation
Checks all imports and basic functionality
"""
import sys
import traceback


def check_imports():
    """Check if all modules can be imported"""
    print("Checking imports...")
    errors = []
    
    try:
        from src.modules.Attendance.domain.entities import (
            AttendanceRecord,
            AttendanceStatus,
            AttendanceAlert,
            AlertType,
            AlertSeverity,
        )
        print("✓ Domain entities imported successfully")
    except Exception as e:
        errors.append(f"Domain entities import failed: {e}")
    
    try:
        from src.modules.Attendance.application.dto import (
            CheckInRequestDTO,
            CheckOutRequestDTO,
            AttendanceRecordResponseDTO,
            AttendanceAlertResponseDTO,
        )
        print("✓ DTOs imported successfully")
    except Exception as e:
        errors.append(f"DTOs import failed: {e}")
    
    try:
        from src.modules.Attendance.infrastructure.repositories.attendance_repository import (
            AttendanceRepository
        )
        print("✓ Repository imported successfully")
    except Exception as e:
        errors.append(f"Repository import failed: {e}")
    
    try:
        from src.modules.Attendance.application.usecases.attendance_service import (
            AttendanceService
        )
        print("✓ Service imported successfully")
    except Exception as e:
        errors.append(f"Service import failed: {e}")
    
    try:
        from src.modules.Attendance.infrastructure.api.attendance_router import (
            attendance_router
        )
        print("✓ API Router imported successfully")
    except Exception as e:
        errors.append(f"API Router import failed: {e}")
    
    return errors


def check_entities():
    """Check if entities work correctly"""
    print("\nChecking entities...")
    errors = []
    
    try:
        from src.modules.Attendance.domain.entities import (
            AttendanceRecord,
            AttendanceStatus,
        )
        from datetime import datetime
        
        # Create a test record
        record = AttendanceRecord(
            id="test-123",
            employee_id="emp-123",
            shift_assignment_id="shift-123",
            check_in_time=datetime.now(),
        )
        
        assert record.status == AttendanceStatus.CHECKED_IN
        assert record.is_late is False
        print("✓ AttendanceRecord entity works correctly")
    except Exception as e:
        errors.append(f"AttendanceRecord entity check failed: {e}")
    
    try:
        from src.modules.Attendance.domain.entities import (
            AttendanceAlert,
            AlertType,
            AlertSeverity,
        )
        
        alert = AttendanceAlert(
            id="alert-123",
            employee_id="emp-123",
            alert_type=AlertType.NO_CHECK_IN,
            description="Test alert",
            severity=AlertSeverity.WARNING,
        )
        
        assert alert.is_acknowledged is False
        print("✓ AttendanceAlert entity works correctly")
    except Exception as e:
        errors.append(f"AttendanceAlert entity check failed: {e}")
    
    return errors


def check_main_integration():
    """Check if attendance router is integrated in main.py"""
    print("\nChecking main.py integration...")
    errors = []
    
    try:
        with open("main.py", "r") as f:
            content = f.read()
            
        if "from src.modules.Attendance.infrastructure.api.attendance_router import attendance_router" in content:
            print("✓ Attendance router import found in main.py")
        else:
            errors.append("Attendance router import NOT found in main.py")
        
        if "app.include_router(attendance_router)" in content:
            print("✓ Attendance router included in app")
        else:
            errors.append("Attendance router NOT included in app")
        
        if '"Asistencia"' in content:
            print("✓ Asistencia tag added to OpenAPI")
        else:
            errors.append("Asistencia tag NOT found in OpenAPI tags")
    
    except Exception as e:
        errors.append(f"Main.py check failed: {e}")
    
    return errors


def check_migration_file():
    """Check if migration file exists"""
    print("\nChecking migration file...")
    errors = []
    
    from pathlib import Path
    
    migration_file = Path("src/shared/infrastructure/database/migrations/versions/008_create_attendance_tables.sql")
    
    if migration_file.exists():
        print(f"✓ Migration file exists: {migration_file}")
        
        # Check if it has the expected tables
        content = migration_file.read_text()
        
        expected_tables = [
            "attendance_records",
            "attendance_alerts",
            "attendance_check_log",
            "today_attendance_summary",
            "attendance_report_summary",
        ]
        
        for table in expected_tables:
            if table in content:
                print(f"  ✓ Table/View '{table}' defined")
            else:
                errors.append(f"Table/View '{table}' NOT found in migration")
    else:
        errors.append(f"Migration file NOT found: {migration_file}")
    
    return errors


def check_documentation():
    """Check if documentation exists"""
    print("\nChecking documentation...")
    errors = []
    
    from pathlib import Path
    
    doc_file = Path("docs/ATTENDANCE_CONTROL_GUIDE.md")
    
    if doc_file.exists():
        print(f"✓ Documentation file exists: {doc_file}")
        content = doc_file.read_text()
        
        required_sections = [
            "Overview",
            "Authentication & Authorization",
            "Database Schema",
            "API Endpoints",
            "Check-In",
            "Check-Out",
            "Alerts",
            "Reports",
        ]
        
        for section in required_sections:
            if section in content:
                print(f"  ✓ Section '{section}' found")
            else:
                errors.append(f"Section '{section}' NOT found in documentation")
    else:
        errors.append(f"Documentation file NOT found: {doc_file}")
    
    return errors


def main():
    """Run all checks"""
    print("="*60)
    print("ATTENDANCE MODULE VERIFICATION")
    print("="*60)
    
    all_errors = []
    
    # Run checks
    all_errors.extend(check_imports())
    all_errors.extend(check_entities())
    all_errors.extend(check_main_integration())
    all_errors.extend(check_migration_file())
    all_errors.extend(check_documentation())
    
    # Summary
    print("\n" + "="*60)
    if all_errors:
        print("❌ VERIFICATION FAILED")
        print("="*60)
        print("\nErrors found:")
        for i, error in enumerate(all_errors, 1):
            print(f"{i}. {error}")
        return 1
    else:
        print("✅ ALL CHECKS PASSED")
        print("="*60)
        print("\nThe Attendance module is properly installed and configured!")
        print("Ready for migrations and API testing.")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Verification failed with exception: {e}")
        traceback.print_exc()
        sys.exit(1)
