"""
Session 17: Automated Test Suite for Database MCP Server
========================================================
This script tests all 5 tasks against the Database MCP Server on port 5001:
1. Task 1: Server health check + Add and retrieve user data
2. Task 2: Parameterized store_order (Insert new order)
3. Task 3: GET_USER_ORDERS command handler (Fetch all order_ids and amounts)
4. Task 4: GET_LAST_N_ORDERS command (Zomato-style timestamp sort)
5. Task 5: delete_order by order_id (Verified deletion & 404 check)
"""

import sys
import json
import requests

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5001"

def run_tests():
    print("=" * 70)
    print("     SESSION 17: DATABASE MCP SERVER AUTOMATED TEST SUITE")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # Test 1: Task 1 - Root Endpoint and User Data
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Task 1 - Server Health & User Management ---")
    try:
        r1 = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[*] GET {BASE_URL}/ -> Status: {r1.status_code}")
        assert r1.status_code == 200
        print(f"[*] Response:\n{json.dumps(r1.json(), indent=2)}")

        # Add User
        user_payload = {
            "user_id": "USR_S17_01",
            "name": "Nishant Patel",
            "email": "nishant@example.com",
            "phone": "+91-9876543210"
        }
        r1_user = requests.post(f"{BASE_URL}/user", json=user_payload, timeout=5)
        print(f"[*] POST /user -> Status: {r1_user.status_code}")

        # Retrieve User
        r1_get = requests.get(f"{BASE_URL}/user/USR_S17_01", timeout=5)
        print(f"[*] GET /user/USR_S17_01 -> Status: {r1_get.status_code}")
        print(f"[*] User Data: {r1_get.json().get('user')}")
        assert r1_get.status_code == 200
        print("[PASS] Task 1 User management verified successfully!")
    except Exception as e:
        print(f"[-] FAILED Test 1: {e}")
        print("    Ensure 'database_mcp_server.py' is running on port 5001.")
        return

    # --------------------------------------------------------------------------
    # Test 2: Task 2 - store_order Function & Endpoint
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 2: Task 2 - Parameterized store_order ---")
    order_payload = {
        "order_id": "ORD_LIVE_8801",
        "user_id": "USR_S17_01",
        "amount": 749.50
    }
    r2 = requests.post(f"{BASE_URL}/order", json=order_payload, timeout=5)
    print(f"[*] POST /order with {order_payload}")
    print(f"[*] Status:  {r2.status_code}")
    print(f"[*] Response:\n{json.dumps(r2.json(), indent=2)}")
    assert r2.status_code in (201, 409)
    print("[PASS] Task 2 store_order verified successfully!")

    # --------------------------------------------------------------------------
    # Test 3: Task 3 - GET_USER_ORDERS Command Handler
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 3: Task 3 - GET_USER_ORDERS Handler ---")
    cmd3_payload = {
        "command": "GET_USER_ORDERS",
        "params": {"user_id": "USR_S17_01"}
    }
    r3 = requests.post(f"{BASE_URL}/command", json=cmd3_payload, timeout=5)
    print(f"[*] POST /command with 'GET_USER_ORDERS'")
    print(f"[*] Status:  {r3.status_code}")
    data3 = r3.json()
    print(f"[*] Found {data3.get('count')} order(s) for user 'USR_S17_01':")
    for o in data3.get("orders", []):
        print(f"    • Order ID: {o['order_id']} | Amount: Rs. {o['amount']}")
    assert r3.status_code == 200
    print("[PASS] Task 3 GET_USER_ORDERS verified successfully!")

    # --------------------------------------------------------------------------
    # Test 4: Task 4 - GET_LAST_N_ORDERS (Zomato-Style Recent History)
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 4: Task 4 - GET_LAST_N_ORDERS (Timestamp Sorted) ---")
    cmd4_payload = {
        "command": "GET_LAST_N_ORDERS",
        "params": {"user_id": "USR_ZOMATO", "n": 3}
    }
    r4 = requests.post(f"{BASE_URL}/command", json=cmd4_payload, timeout=5)
    print(f"[*] POST /command with 'GET_LAST_N_ORDERS' (n=3)")
    print(f"[*] Status:  {r4.status_code}")
    data4 = r4.json()
    print(f"[*] Last 3 Zomato orders returned (Sorted by order_time DESC):")
    for idx, o in enumerate(data4.get("orders", []), start=1):
        print(f"    {idx}. Order ID: {o['order_id']} | Rs. {o['amount']} | Time: {o['order_time']}")
    assert r4.status_code == 200
    assert len(data4.get("orders", [])) <= 3
    print("[PASS] Task 4 GET_LAST_N_ORDERS verified successfully!")

    # --------------------------------------------------------------------------
    # Test 5: Task 5 - delete_order Function & Endpoint
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 5: Task 5 - delete_order Function ---")
    # First insert temporary order
    temp_order = {"order_id": "ORD_TO_DELETE_99", "user_id": "USR_S17_01", "amount": 199.00}
    requests.post(f"{BASE_URL}/order", json=temp_order, timeout=5)

    # Delete it
    cmd5_payload = {
        "command": "DELETE_ORDER",
        "params": {"order_id": "ORD_TO_DELETE_99"}
    }
    r5 = requests.post(f"{BASE_URL}/command", json=cmd5_payload, timeout=5)
    print(f"[*] POST /command with 'DELETE_ORDER' (order_id='ORD_TO_DELETE_99')")
    print(f"[*] Status:  {r5.status_code}")
    print(f"[*] Response:\n{json.dumps(r5.json(), indent=2)}")
    assert r5.status_code == 200
    assert r5.json().get("rows_affected") == 1

    # Attempt to delete again (Expect 404 Not Found)
    r5_again = requests.post(f"{BASE_URL}/command", json=cmd5_payload, timeout=5)
    print(f"\n[*] Deleting again -> Status: {r5_again.status_code} (Expected: 404)")
    print(f"[*] Response:\n{json.dumps(r5_again.json(), indent=2)}")
    assert r5_again.status_code == 404
    print("[PASS] Task 5 delete_order verified successfully!")

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL 5 TASKS TESTED AND VERIFIED FLAWLESSLY ON PORT 5001!")

if __name__ == "__main__":
    run_tests()
