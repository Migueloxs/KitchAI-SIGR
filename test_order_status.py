#!/usr/bin/env python3
"""
Test script for Order Status System
Tests all the acceptance criteria CA1-CA9
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def make_request(method, endpoint, data=None, token=None):
    """Helper function to make HTTP requests"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
    elif method.upper() == "PUT":
        response = requests.put(url, headers=headers, data=json.dumps(data) if data else None)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return response.status_code, response.json() if response.content else None

def test_order_status_system():
    """Test the complete order status system"""
    print("🧪 Testing Order Status System")
    print("=" * 50)

    # Test 1: Register and login
    print("\n📝 Test 1: User Registration and Login")
    status, reg_result = make_request("POST", "/api/auth/register", {
        "name": "Test Waiter",
        "email": "waiter@test.com",
        "password": "TestPass123!"
    })
    print(f"Registration: {status}")

    status, login_result = make_request("POST", "/api/auth/login", {
        "email": "waiter@test.com",
        "password": "TestPass123!"
    })
    print(f"Login: {status}")

    if status != 200:
        print("❌ Failed to login")
        return

    token = login_result.get("access_token")
    print(f"✅ Got token: {token[:20]}...")

    # Test 2: Create order
    print("\n📝 Test 2: Create Order")
    status, order_result = make_request("POST", "/api/orders/", {
        "customer_name": "Test Customer",
        "customer_phone": "+1234567890",
        "table_number": 5,
        "special_instructions": "No onions please",
        "items": [
            {
                "menu_item_id": "item-1",
                "menu_item_name": "Burger",
                "quantity": 2,
                "unit_price": 15.99,
                "special_notes": "Medium rare"
            },
            {
                "menu_item_id": "item-2",
                "menu_item_name": "Fries",
                "quantity": 1,
                "unit_price": 5.99,
                "special_notes": "Extra crispy"
            }
        ]
    }, token=token)

    print(f"Create Order: {status}")
    if status not in (200, 201):
        print(f"❌ Failed to create order: {order_result}")
        return

    order_id = order_result["id"]
    print(f"✅ Order created: {order_id} (Status: {order_result['status']})")

    # Test 3: CA1 - Valid status transitions
    print("\n📝 Test 3: CA1 - Valid Status Transitions")

    # pending -> preparing (should work)
    print("  Testing: pending -> preparing")
    status, update_result = make_request("PUT", f"/api/orders/{order_id}/status", {
        "new_status": "preparing"
    }, token=token)
    print(f"  Status: {status}")
    if status == 200:
        print(f"  ✅ Status changed to: {update_result['status']}")
        print(f"  ✅ preparation_started_at set: {update_result['preparation_started_at']}")
    else:
        print(f"  ❌ Failed: {update_result}")

    # preparing -> ready (should work)
    print("  Testing: preparing -> ready")
    status, update_result = make_request("PUT", f"/api/orders/{order_id}/status", {
        "new_status": "ready"
    }, token=token)
    print(f"  Status: {status}")
    if status == 200:
        print(f"  ✅ Status changed to: {update_result['status']}")
        print(f"  ✅ ready_at set: {update_result['ready_at']}")
        print(f"  ✅ preparation_time calculated: {update_result['preparation_time']} seconds")
    else:
        print(f"  ❌ Failed: {update_result}")

    # ready -> served (should work)
    print("  Testing: ready -> served")
    status, update_result = make_request("PUT", f"/api/orders/{order_id}/status", {
        "new_status": "served"
    }, token=token)
    print(f"  Status: {status}")
    if status == 200:
        print(f"  ✅ Status changed to: {update_result['status']}")
        print(f"  ✅ completed_at set: {update_result['completed_at']}")
        print(f"  ✅ total_time calculated: {update_result['total_time']} seconds")
        print(f"  ✅ payment_status changed to: {update_result['payment_status']}")
    else:
        print(f"  ❌ Failed: {update_result}")

    # Test 4: CA6 - Cancellation
    print("\n📝 Test 4: CA6 - Order Cancellation")

    # Create another order for cancellation test
    status, order2_result = make_request("POST", "/api/orders/", {
        "customer_name": "Cancel Test",
        "table_number": 10,
        "items": [
            {
                "menu_item_id": "item-1",
                "menu_item_name": "Pizza",
                "quantity": 1,
                "unit_price": 12.99
            }
        ]
    }, token=token)

    if status in (200, 201):
        order2_id = order2_result["id"]
        print(f"✅ Created order for cancellation: {order2_id}")

        # Cancel the order
        status, cancel_result = make_request("PUT", f"/api/orders/{order2_id}/status", {
            "new_status": "cancelled",
            "cancellation_reason": "Customer changed their mind"
        }, token=token)
        print(f"  Cancellation: {status}")
        if status == 200:
            print(f"  ✅ Order cancelled: {cancel_result['status']}")
            print(f"  ✅ cancelled_at set: {cancel_result['cancelled_at']}")
            print(f"  ✅ cancellation_reason: {cancel_result['cancellation_reason']}")
        else:
            print(f"  ❌ Failed to cancel: {cancel_result}")

    # Test 5: CA9 - Business Validations
    print("\n📝 Test 5: CA9 - Business Validations")

    # Create another order for validation tests
    status, order3_result = make_request("POST", "/api/orders/", {
        "customer_name": "Validation Test",
        "table_number": 15,
        "items": [
            {
                "menu_item_id": "item-1",
                "menu_item_name": "Salad",
                "quantity": 1,
                "unit_price": 8.99
            }
        ]
    }, token=token)

    if status in (200, 201):
        order3_id = order3_result["id"]
        print(f"✅ Created order for validation tests: {order3_id}")

        # Try invalid transition: pending -> ready (should fail)
        print("  Testing invalid: pending -> ready")
        status, invalid_result = make_request("PUT", f"/api/orders/{order3_id}/status", {
            "new_status": "ready"
        }, token=token)
        print(f"  Status: {status}")
        if status == 400:
            print("  ✅ Correctly rejected invalid transition")
        else:
            print(f"  ❌ Should have failed: {invalid_result}")

        # Try invalid transition: pending -> served (should fail)
        print("  Testing invalid: pending -> served")
        status, invalid_result = make_request("PUT", f"/api/orders/{order3_id}/status", {
            "new_status": "served"
        }, token=token)
        print(f"  Status: {status}")
        if status == 400:
            print("  ✅ Correctly rejected invalid transition")
        else:
            print(f"  ❌ Should have failed: {invalid_result}")

        # Try to cancel without reason (should fail)
        print("  Testing cancellation without reason")
        status, invalid_result = make_request("PUT", f"/api/orders/{order3_id}/status", {
            "new_status": "cancelled"
        }, token=token)
        print(f"  Status: {status}")
        if status == 400:
            print("  ✅ Correctly rejected cancellation without reason")
        else:
            print(f"  ❌ Should have failed: {invalid_result}")

    # Test 6: Get order details
    print("\n📝 Test 6: Get Order Details")
    status, get_result = make_request("GET", f"/api/orders/{order_id}", token=token)
    print(f"Get Order: {status}")
    if status == 200:
        print(f"✅ Retrieved order: {get_result['order_number']} - Status: {get_result['status']}")
        print(f"  Timestamps - Created: {get_result['created_at']}, Completed: {get_result.get('completed_at')}")
        print(f"  Times - Preparation: {get_result.get('preparation_time')}s, Total: {get_result.get('total_time')}s")
    else:
        print(f"❌ Failed to get order: {get_result}")

    print("\n🎉 Order Status System Tests Completed!")
    print("Check the results above for any issues.")

if __name__ == "__main__":
    # Check if server is running
    try:
        status, _ = make_request("GET", "/health")
        if status == 200:
            test_order_status_system()
        else:
            print("❌ Server not running. Please start the server first:")
            print("  python -m uvicorn main:app --reload")
    except:
        print("❌ Cannot connect to server. Please start the server first:")
        print("  python -m uvicorn main:app --reload")