import requests
import json
import time

def test_auth():
    base_url = "http://127.0.0.1:8000"
    
    # Check OpenAPI schema first
    try:
        openapi = requests.get(f"{base_url}/openapi.json").json()
        print("--- OpenAPI Schema Check ---")
        register_schema = openapi["paths"]["/auth/register"]["post"].get("requestBody")
        login_schema = openapi["paths"]["/auth/login"]["post"].get("requestBody")
        
        if register_schema and login_schema:
            print("✓ OpenAPI correctly shows request body schemas for /auth/register and /auth/login")
        else:
            print("✗ Missing requestBody in OpenAPI spec")
            print("Register:", register_schema)
            print("Login:", login_schema)
    except Exception as e:
        print("Failed to fetch OpenAPI:", e)

    print("\n--- Test Auth Flow ---")
    email = f"demo_{int(time.time())}@example.com"
    password = "password123"
    auth_data = {"email": email, "password": password}
    
    # 1) Register new user
    res = requests.post(f"{base_url}/auth/register", json=auth_data)
    print("POST /auth/register ->", res.status_code)
    if res.status_code == 200 or res.status_code == 201: # 200 OK or 201 Created expected
        print("✓ Registration successful")
    else:
        print("✗ Registration failed:", res.text)
        
    # 2) Login
    res = requests.post(f"{base_url}/auth/login", json=auth_data)
    print("POST /auth/login ->", res.status_code)
    if res.status_code == 200:
        token = res.json().get("access_token")
        if token:
            print(f"✓ Login successful! Token received: {token[:15]}...")
        else:
            print("✗ Login succeeded but no token returned")
    else:
        print("✗ Login failed:", res.text)

if __name__ == "__main__":
    test_auth()
