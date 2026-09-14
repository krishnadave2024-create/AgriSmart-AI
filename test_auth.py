import requests
import json
import random

BASE_URL = 'http://localhost:8000/api'

def test_auth():
    suffix = random.randint(1000, 9999)
    username = f"testuser_{suffix}"
    email = f"test_{suffix}@example.com"
    password = "StrongPassword123!"
    
    print("--- 1. REGISTER ---")
    reg_payload = {
        "username": username,
        "email": email,
        "full_name": "Test User",
        "password": password,
        "confirm_password": password
    }
    print(f"Payload: {json.dumps(reg_payload)}")
    res = requests.post(f"{BASE_URL}/auth/register/", json=reg_payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    print("\n--- 2. LOGIN ---")
    login_payload = {
        "username": username,
        "password": password
    }
    print(f"Payload: {json.dumps(login_payload)}")
    res_login = requests.post(f"{BASE_URL}/auth/login/", json=login_payload)
    print(f"Status: {res_login.status_code}")
    print(f"Response: {res_login.text}")

    print("\n--- 3. REGISTER DUPLICATE ---")
    res_dup = requests.post(f"{BASE_URL}/auth/register/", json=reg_payload)
    print(f"Status: {res_dup.status_code}")
    print(f"Response: {res_dup.text}")

if __name__ == '__main__':
    test_auth()
