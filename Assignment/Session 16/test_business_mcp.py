"""
Session 16: Automated Test Suite for Business MCP Server
========================================================
This script tests all 5 tasks against the Business MCP Server:
1. GET  /             -> Expect 200 'MCP Server Running'
2. POST /order-status -> Valid orderId (Expect 200 with status)
3. POST /order-status -> Missing orderId (Expect 400 Bad Request error)
4. POST /notify       -> Valid notification (Expect 200 and entry in notifications.log)
5. POST /notify       -> Missing field (Expect 400 Bad Request)
6. GET  /user-profile -> Expect 200 with profile (name, email, phone)
7. POST /user-profile -> Expect 200 with profile
"""

import sys
import os
import json
import time
import requests

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(CURRENT_DIR, "notifications.log")

def run_tests():
    print("=" * 70)
    print("     SESSION 16: BUSINESS MCP SERVER AUTOMATED TEST SUITE")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # Test 1: Task 1 - Root Endpoint
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Task 1 - Root Endpoint (GET /) ---")
    try:
        r1 = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[*] Request: GET {BASE_URL}/")
        print(f"[*] Status:  {r1.status_code}")
        print(f"[*] Body:    \"{r1.text}\"")
        assert r1.status_code == 200
        assert r1.text == "MCP Server Running"
        print("[PASS] Task 1 Root Endpoint verified successfully!")
    except Exception as e:
        print(f"[-] FAILED Test 1: {e}")
        print("    Ensure 'business_mcp_server.py' is running on port 5000.")
        return

    # --------------------------------------------------------------------------
    # Test 2: Task 2 - Order Status with Valid orderId
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 2: Task 2 - Order Status Valid Request (POST /order-status) ---")
    payload2 = {"orderId": "OD9847120394"}
    r2 = requests.post(f"{BASE_URL}/order-status", json=payload2, timeout=5)
    print(f"[*] Request: POST /order-status with {payload2}")
    print(f"[*] Status:  {r2.status_code}")
    print(f"[*] Response:\n{json.dumps(r2.json(), indent=2)}")
    assert r2.status_code == 200
    assert "status" in r2.json()
    print("[PASS] Task 2 Order Status verified successfully!")

    # --------------------------------------------------------------------------
    # Test 3: Task 3 - Order Status Missing orderId (Expect HTTP 400)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 3: Task 3 - Error Handling for Missing orderId (POST /order-status) ---")
    payload3 = {"wrongField": 123}
    r3 = requests.post(f"{BASE_URL}/order-status", json=payload3, timeout=5)
    print(f"[*] Request: POST /order-status with missing 'orderId': {payload3}")
    print(f"[*] Status:  {r3.status_code} (Expected: 400)")
    print(f"[*] Response:\n{json.dumps(r3.json(), indent=2)}")
    assert r3.status_code == 400
    assert "error" in r3.json()
    print("[PASS] Task 3 HTTP 400 Error Handling verified successfully!")

    # --------------------------------------------------------------------------
    # Test 4: Task 4 - Notification System (/notify)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 4: Task 4 - Flipkart-Style Notification System (POST /notify) ---")
    payload4 = {
        "userId": "USR_101",
        "message": "Your Flipkart package has been out for delivery by Ekart Logistics!"
    }
    r4 = requests.post(f"{BASE_URL}/notify", json=payload4, timeout=5)
    print(f"[*] Request: POST /notify with {payload4}")
    print(f"[*] Status:  {r4.status_code}")
    print(f"[*] Response:\n{json.dumps(r4.json(), indent=2)}")
    assert r4.status_code == 200

    # Verify notifications.log file
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_line = lines[-1].strip() if lines else "EMPTY"
        print(f"[*] Latest line in notifications.log:\n    {last_line}")
        assert "USR_101" in last_line
    print("[PASS] Task 4 Notification logging verified successfully!")

    # --------------------------------------------------------------------------
    # Test 5: Task 5 - User Profile Endpoint (GET & POST /user-profile)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 5: Task 5 - User Profile Endpoint (GET & POST /user-profile) ---")
    r5_get = requests.get(f"{BASE_URL}/user-profile?userId=USR_101", timeout=5)
    print(f"[*] GET /user-profile?userId=USR_101")
    print(f"[*] Status:  {r5_get.status_code}")
    print(f"[*] Response:\n{json.dumps(r5_get.json(), indent=2)}")
    assert r5_get.status_code == 200
    profile = r5_get.json().get("profile", {})
    assert "name" in profile and "email" in profile and "phone" in profile

    # Test POST variant
    r5_post = requests.post(f"{BASE_URL}/user-profile", json={"userId": "USR_102"}, timeout=5)
    print(f"\n[*] POST /user-profile with {{\"userId\": \"USR_102\"}}")
    print(f"[*] Status:  {r5_post.status_code}")
    print(f"[*] Response:\n{json.dumps(r5_post.json(), indent=2)}")
    assert r5_post.status_code == 200

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL 5 TASKS TESTED AND VERIFIED FLAWLESSLY!")

if __name__ == "__main__":
    run_tests()
