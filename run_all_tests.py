#!/usr/bin/env python
"""
Run all test files and generate a comprehensive report.
"""

import subprocess
import sys

test_files = [
    "test_payroll_unit.py",
    "test_payroll_api.py",
    "test_attendance_module.py",
    "test_attendance_api.py",
    "test_financial_reports.py",
    "test_finances_calculations.py",
    "test_inventory_crud.py",
    "test_inventory_auto_update.py",
    "test_inventory_auto_update_service.py",
    "test_inventory_min_stock_alerts.py",
    "test_shifts_module.py",
    "test_sales_autoregistration.py",
    "test_service_modalities.py",
    "test_order_status.py",
    "test_order_status_complete.py",
    "test_turso_connection.py",
    "test_server.py",
]

print("=" * 70)
print("COMPREHENSIVE TEST REPORT")
print("=" * 70)

total_passed = 0
total_failed = 0
results = []

for test_file in test_files:
    print(f"\nRunning {test_file}...", end=" ")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        # Parse output
        output = result.stdout + result.stderr
        
        # Look for test summary
        if "passed" in output:
            # Extract numbers
            lines = output.split("\n")
            for line in lines:
                if "passed" in line:
                    # Try to extract passed count
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            try:
                                passed = int(parts[i-1])
                                total_passed += passed
                                results.append((test_file, passed, 0, "PASS"))
                                print(f"PASS ({passed} tests)")
                                break
                            except (ValueError, IndexError):
                                pass
                    break
            else:
                if result.returncode == 0:
                    results.append((test_file, 0, 0, "PASS (0 tests)"))
                    print("PASS (0 tests)")
                else:
                    results.append((test_file, 0, 1, "FAIL"))
                    print("FAIL")
                    total_failed += 1
        elif result.returncode == 0:
            results.append((test_file, 0, 0, "PASS (0 tests)"))
            print("PASS (0 tests)")
        else:
            results.append((test_file, 0, 1, "FAIL"))
            print("FAIL")
            total_failed += 1
            
    except subprocess.TimeoutExpired:
        results.append((test_file, 0, 1, "TIMEOUT"))
        print("TIMEOUT")
        total_failed += 1
    except Exception as e:
        results.append((test_file, 0, 1, f"ERROR: {str(e)}"))
        print(f"ERROR: {e}")
        total_failed += 1

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
for test_file, passed, failed, status in results:
    print(f"{test_file:40} {status}")

print("\n" + "=" * 70)
print(f"TOTAL: {total_passed} passed")
print("=" * 70)

sys.exit(0 if total_failed == 0 else 1)
