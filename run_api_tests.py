import urllib.request as request
import urllib.error as error
import json
import uuid

BASE_URL = "http://localhost:8000/api"

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    req = request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    
    if data:
        req.data = json.dumps(data).encode("utf-8")
        
    try:
        with request.urlopen(req) as res:
            body = res.read().decode("utf-8")
            return res.status, json.loads(body) if body else None
    except error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except:
            return e.code, body

def run_tests():
    print("Initiating API tests...\n")
    
    # 1. Registrar usuario
    email = f"tester_{uuid.uuid4().hex[:6]}@kitchai.com"
    print(f"[*] Registering {email}...")
    status, res = make_request("POST", "/auth/register", {
        "name": "Waiter Tester",
        "email": email,
        "password": "Password123!",
        "role_id": "uuid-role-waiter"
    })
    print(f"  -> HTTP {status}: Registered.")
    
    # 2. Login
    print("\n[*] Logging in...")
    status, res = make_request("POST", "/auth/login", {
        "email": email,
        "password": "Password123!"
    })
    print(f"  -> HTTP {status}: Token retrieved.")
    token = res.get("access_token")
    
    if not token:
         print("[X] Could not get token, aborting.")
         return

    print("\n[*] Creating a new order...")
    status, res_order = make_request("POST", "/orders/", {
        "customer_name": "Juan Perez",
        "customer_phone": "809-555-1234",
        "table_number": 5,
        "special_instructions": "Con mucho hielo",
        "items": [
            {
                "menu_item_id": "item-123",
                "menu_item_name": "Hamburguesa Clasica",
                "quantity": 2,
                "unit_price": 350.00,
                "special_notes": "Sin cebolla"
            }
        ] 
    }, token)
    print(f"  -> HTTP {status}")
    if status in (200, 201):
        order_id = res_order.get("id")
        print(f"     [OK] Created Order ID: {order_id}")
    else:
        print(f"     [X] Failed keeping order: {res_order}")
        return

    print("\n[*] Getting order Details...")
    status, res = make_request("GET", f"/orders/{order_id}", token=token)
    print(f"  -> HTTP {status}")

    print("\n[*] Listing Orders...")
    status, res = make_request("GET", f"/orders/", token=token)
    print(f"  -> HTTP {status}")

    print("\n[*] Modifying Order...")
    status, res = make_request("PATCH", f"/orders/{order_id}/status?status=ready", token=token)
    print(f"  -> HTTP {status}")

if __name__ == "__main__":
    run_tests()