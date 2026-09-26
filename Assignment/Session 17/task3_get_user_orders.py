"""
Session 17 - Task 3: GET_USER_ORDERS Command Handler
====================================================
This script implements a command handler to process 'GET_USER_ORDERS',
which takes a user_id and returns all order_ids and amounts for that user
from the SQLite database.
"""

import sys
import os
import sqlite3
from typing import Dict, Any, List

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "mcp_database.db")

def get_user_orders(user_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Retrieves all order_ids and amounts for a given user_id.

    Parameters:
    - user_id: ID of the user whose orders are being queried.
    - db_path: Path to the SQLite database.

    Returns:
    - Structured response with list of {order_id, amount}.
    """
    if not user_id or not str(user_id).strip():
        return {
            "status": "error",
            "message": "user_id is required."
        }

    clean_user_id = str(user_id).strip()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Parameterized query to select all order_ids and amounts for this user
        query = "SELECT order_id, amount FROM orders WHERE user_id = ?"
        cursor.execute(query, (clean_user_id,))
        rows = cursor.fetchall()

        orders_list = [{"order_id": r[0], "amount": float(r[1])} for r in rows]
        total_spent = sum(item["amount"] for item in orders_list)

        return {
            "status": "success",
            "command": "GET_USER_ORDERS",
            "user_id": clean_user_id,
            "order_count": len(orders_list),
            "total_spent": round(total_spent, 2),
            "orders": orders_list
        }
    finally:
        conn.close()

def handle_mcp_command(command: str, params: Dict[str, Any], db_path: str = DB_PATH) -> Dict[str, Any]:
    """MCP Command dispatcher handling GET_USER_ORDERS."""
    if command.upper() == "GET_USER_ORDERS":
        user_id = params.get("user_id")
        return get_user_orders(user_id, db_path=db_path)
    else:
        return {
            "status": "error",
            "message": f"Unknown command: '{command}'"
        }

def run_task3_demo():
    print("=" * 65)
    print("     SESSION 17 - TASK 3: GET_USER_ORDERS COMMAND HANDLER")
    print("=" * 65)

    # Test 1: Query user USR_101
    print("\n--- Test 1: Querying Orders for User 'USR_101' ---")
    res1 = handle_mcp_command("GET_USER_ORDERS", {"user_id": "USR_101"})
    print(f"[*] Command:    {res1.get('command')}")
    print(f"[*] User ID:    {res1.get('user_id')}")
    print(f"[*] Orders:     {res1.get('order_count')} order(s) found | Total: Rs. {res1.get('total_spent')}")
    for item in res1.get("orders", []):
        print(f"    • Order ID: {item['order_id']}  ➔  Amount: Rs. {item['amount']}")

    # Test 2: Query user USR_102
    print("\n" + "-" * 65)
    print("--- Test 2: Querying Orders for User 'USR_102' ---")
    res2 = handle_mcp_command("GET_USER_ORDERS", {"user_id": "USR_102"})
    for item in res2.get("orders", []):
        print(f"    • Order ID: {item['order_id']}  ➔  Amount: Rs. {item['amount']}")

    # Test 3: Query user with no orders
    print("\n" + "-" * 65)
    print("--- Test 3: Querying Non-existent User 'USR_999' ---")
    res3 = handle_mcp_command("GET_USER_ORDERS", {"user_id": "USR_999"})
    print(f"[*] Orders found: {res3.get('order_count')} orders")

    print("\n" + "=" * 65)
    print("[SUCCESS] Task 3 completed: GET_USER_ORDERS handler verified!")

if __name__ == "__main__":
    run_task3_demo()
