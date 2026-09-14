import requests
import json
import random

BASE_URL = 'http://localhost:8000/api'

def test_case_sensitivity():
    suffix = random.randint(1000, 9999)
    username = f"JohnDoe_{suffix}"
    email = f"john_{suffix}@example.com"
    password = "StrongPassword123!"
    
    print("--- 1. REGISTER ---")
    reg_payload = {
        "username": username,
        "email": email,
        "full_name": "John Doe",
        "password": password,
        "confirm_password": password
    }
    res = requests.post(f"{BASE_URL}/auth/register/", json=reg_payload)
    print(f"Status: {res.status_code}")
    
    print("\n--- 2. LOGIN WITH LOWERCASE USERNAME ---")
    login_payload_lower = {
        "username": username.lower(),
        "password": password
    }
    res_login_lower = requests.post(f"{BASE_URL}/auth/login/", json=login_payload_lower)
    print(f"Status: {res_login_lower.status_code}")

    print("\n--- 3. LOGIN WITH EMAIL ---")
    login_payload_email = {
        "username": email,
        "password": password
    }
    res_login_email = requests.post(f"{BASE_URL}/auth/login/", json=login_payload_email)
    print(f"Status: {res_login_email.status_code}")

if __name__ == '__main__':
    test_case_sensitivity()
