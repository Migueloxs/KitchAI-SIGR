"""
API Tests for Attendance Module
Run this script to test the attendance endpoints
"""
import requests
import json
from datetime import datetime, date, timedelta
import sys

BASE_URL = "http://localhost:8000/api"
ADMIN_TOKEN = None  # Set after login
USER_TOKEN = None   # Set after login
ADMIN_ID = None
USER_ID = None
USER_EMAIL = "test_employee@restaurant.com"
ADMIN_EMAIL = "test_admin@restaurant.com"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")


def print_response(response, label="Response"):
    print(f"\n{YELLOW}=== {label} ==={RESET}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


# ===================== AUTHENTICATION =====================

def test_authentication():
    """Test user authentication"""
    print("\n" + "="*60)
    print("AUTHENTICATION TESTS")
    print("="*60)
    
    global ADMIN_TOKEN, USER_TOKEN, ADMIN_ID, USER_ID
    
    # Register admin
    print_info("Registering admin user...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "name": "Test Admin",
            "email": ADMIN_EMAIL,
            "password": "AdminPass123!"
        }
    )
    print_response(response, "Register Admin")
    
    if response.status_code == 201:
        admin_data = response.json()
        ADMIN_ID = admin_data.get("id")
        print_success("Admin registered")
    
    # Register employee
    print_info("Registering employee user...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "name": "Test Employee",
            "email": USER_EMAIL,
            "password": "EmpPass123!"
        }
    )
    print_response(response, "Register Employee")
    
    if response.status_code == 201:
        user_data = response.json()
        USER_ID = user_data.get("id")
        print_success("Employee registered")
    
    # Login admin
    print_info("Logging in admin...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": "AdminPass123!"
        }
    )
    print_response(response, "Login Admin")
    
    if response.status_code == 200:
        ADMIN_TOKEN = response.json().get("access_token")
        print_success(f"Admin logged in: {ADMIN_TOKEN[:20]}...")
    else:
        print_error("Failed to login admin")
        return False
    
    # Login employee
    print_info("Logging in employee...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": USER_EMAIL,
            "password": "EmpPass123!"
        }
    )
    print_response(response, "Login Employee")
    
    if response.status_code == 200:
        USER_TOKEN = response.json().get("access_token")
        print_success(f"Employee logged in: {USER_TOKEN[:20]}...")
    else:
        print_error("Failed to login employee")
        return False
    
    return True


# ===================== CHECK-IN / CHECK-OUT TESTS =====================

def test_check_in():
    """Test employee check-in"""
    print("\n" + "="*60)
    print("CHECK-IN / CHECK-OUT TESTS")
    print("="*60)
    
    # Check in
    print_info("Employee checking in...")
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = requests.post(
        f"{BASE_URL}/attendance/check-in",
        json={
            "employee_id": USER_ID,
            "notes": "Arrived on time"
        },
        headers=headers
    )
    print_response(response, "Check-In Response")
    
    if response.status_code == 201:
        record_data = response.json()
        record_id = record_data.get("id")
        print_success(f"Employee checked in: {record_id}")
        return record_id
    else:
        print_error("Failed to check in")
        return None


def test_get_today_attendance():
    """Test getting today's attendance"""
    print_info("Getting today's attendance...")
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = requests.get(
        f"{BASE_URL}/attendance/today?employee_id={USER_ID}",
        headers=headers
    )
    print_response(response, "Today's Attendance")
    
    if response.status_code == 200:
        print_success("Retrieved today's attendance")
    else:
        print_error("Failed to retrieve today's attendance")


def test_check_out(record_id):
    """Test employee check-out"""
    if not record_id:
        print_error("No record ID provided for check-out")
        return
    
    print_info("Employee checking out...")
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = requests.post(
        f"{BASE_URL}/attendance/check-out",
        json={
            "employee_id": USER_ID,
            "record_id": record_id,
            "notes": "End of shift"
        },
        headers=headers
    )
    print_response(response, "Check-Out Response")
    
    if response.status_code == 200:
        print_success("Employee checked out")
    else:
        print_error("Failed to check out")


def test_attendance_history():
    """Test getting attendance history"""
    print_info("Getting attendance history...")
    headers = {"Authorization": f"Bearer {USER_TOKEN}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = requests.get(
        f"{BASE_URL}/attendance/history?employee_id={USER_ID}&start_date={start_date}&end_date={end_date}&limit=10",
        headers=headers
    )
    print_response(response, "Attendance History")
    
    if response.status_code == 200:
        print_success("Retrieved attendance history")
    else:
        print_error("Failed to retrieve attendance history")


# ===================== ALERT TESTS =====================

def test_alerts():
    """Test alert functionality"""
    print("\n" + "="*60)
    print("ALERT TESTS")
    print("="*60)
    
    # Generate alerts
    print_info("Generating missing check-in alerts...")
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    response = requests.post(
        f"{BASE_URL}/attendance/alerts/check-missing-checkins",
        headers=headers
    )
    print_response(response, "Generate Alerts Response")
    
    if response.status_code == 200:
        alerts = response.json()
        print_success(f"Generated {len(alerts)} alerts")
    else:
        print_error("Failed to generate alerts")
    
    # Get pending alerts
    print_info("Getting pending alerts...")
    response = requests.get(
        f"{BASE_URL}/attendance/alerts/pending",
        headers=headers
    )
    print_response(response, "Pending Alerts")
    
    if response.status_code == 200:
        print_success("Retrieved pending alerts")
    else:
        print_error("Failed to retrieve pending alerts")


# ===================== REPORT TESTS =====================

def test_reports():
    """Test report functionality"""
    print("\n" + "="*60)
    print("REPORT TESTS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    
    # Today's summary
    print_info("Getting today's attendance summary...")
    response = requests.get(
        f"{BASE_URL}/attendance/reports/today",
        headers=headers
    )
    print_response(response, "Today's Summary")
    
    if response.status_code == 200:
        print_success("Retrieved today's attendance summary")
    else:
        print_error("Failed to retrieve today's summary")
    
    # Attendance report
    print_info("Getting attendance report...")
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    response = requests.get(
        f"{BASE_URL}/attendance/reports/attendance?start_date={start_date}&end_date={end_date}&limit=10",
        headers=headers
    )
    print_response(response, "Attendance Report")
    
    if response.status_code == 200:
        print_success("Retrieved attendance report")
    else:
        print_error("Failed to retrieve attendance report")
    
    # Employee statistics
    print_info("Getting employee statistics...")
    headers_user = {"Authorization": f"Bearer {USER_TOKEN}"}
    response = requests.get(
        f"{BASE_URL}/attendance/statistics",
        headers=headers_user
    )
    print_response(response, "Employee Statistics")
    
    if response.status_code == 200:
        print_success("Retrieved employee statistics")
    else:
        print_error("Failed to retrieve employee statistics")


# ===================== MAIN TEST RUNNER =====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("ATTENDANCE MODULE - API TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    try:
        # Authentication
        if not test_authentication():
            print_error("Authentication tests failed")
            return False
        
        # Check-in/Check-out
        print("\nTest 1: Check-in")
        record_id = test_check_in()
        
        print("\nTest 2: Get today's attendance")
        test_get_today_attendance()
        
        print("\nTest 3: Attendance history")
        test_attendance_history()
        
        print("\nTest 4: Check-out")
        test_check_out(record_id)
        
        # Alerts
        test_alerts()
        
        # Reports
        test_reports()
        
        print("\n" + "="*60)
        print_success("All tests completed!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
