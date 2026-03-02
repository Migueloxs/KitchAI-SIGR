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
    output = []
    
    email = f"tester_{uuid.uuid4().hex[:6]}@kitchai.com"
    status, res = make_request("POST", "/auth/register", {
        "name": "Waiter Tester",
        "email": email,
        "password": "Password123!",
        "role_id": "uuid-role-waiter"
    })
    output.append(f"Reg: {status}")
    
    status, res = make_request("POST", "/auth/login", {
        "email": email,
        "password": "Password123!"
    })
    output.append(f"Login: {status}")
    token = res.get("access_token") if isinstance(res, dict) else None
    
    if not token:
        with open("test_results.txt", "w") as f: f.write("\n".join(output))
        return

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
    output.append(f"Create Order: {status} -> {res_order}")
    
    if status in (200, 201):
        order_id = res_order.get("id")
        
        status, res = make_request("GET", f"/orders/{order_id}", token=token)
        output.append(f"Get Order: {status}")

    with open("test_results.txt", "w", encoding='utf-8') as f: f.write("\n".join(output))

if __name__ == "__main__":
    run_tests()