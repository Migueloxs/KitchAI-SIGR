#!/usr/bin/env python3
"""Quick test to verify server is running and Shifts module is integrated"""
import requests
import time
import sys

# Wait for server to fully start
print("Waiting for server to start...")
time.sleep(3)

try:
    print("Testing Swagger UI endpoint...")
    response = requests.get("http://localhost:8001/docs", timeout=10)
    
    if response.status_code == 200:
        print("✅ Server is running!")
        
        if "Turnos" in response.text or "Shifts" in response.text or "/api/shifts" in response.text:
            print("✅ Shifts module is integrated in Swagger UI!")
            print("\nEndpoints found:")
            if "/api/shifts/shifts" in response.text:
                print("  - Shift management endpoints")
            if "/api/shifts/assignments" in response.text:
                print("  - Shift assignment endpoints")
            if "/api/shifts/calendar" in response.text:
                print("  - Calendar endpoints")
            sys.exit(0)
        else:
            print("⚠️ Shifts module not found in Swagger UI")
            print("Response snippet:", response.text[2000:2500])
            sys.exit(1)
    else:
        print(f"✅ Server returned status {response.status_code}")
        sys.exit(1)
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Cannot connect to server: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
