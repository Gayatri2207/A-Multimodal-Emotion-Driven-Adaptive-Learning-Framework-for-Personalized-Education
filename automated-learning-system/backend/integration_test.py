import requests
import json

def test_integration():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test Health
    res = requests.get(f"{base_url}/health")
    print("Health:", res.status_code, res.json())
    
    # 2. Test Registration
    email = "integration_test_user@example.com"
    password = "password123"
    
    auth_data = {"email": email, "password": password}
    
    res = requests.post(f"{base_url}/auth/register", json=auth_data)
    print("Register:", res.status_code, res.text)
    
    # 3. Test Login
    res = requests.post(f"{base_url}/auth/login", json=auth_data)
    print("Login:", res.status_code, res.text)
    
    if res.status_code == 200:
        token = res.json().get("access_token")
        print(f"Got Token: {token[:10]}...")
    
    # 4. Test Analytics
    res = requests.get(f"{base_url}/analytics/summary")
    print("Analytics:", res.status_code, res.json())

if __name__ == "__main__":
    test_integration()
