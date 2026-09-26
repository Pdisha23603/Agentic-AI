"""
Session 17 - Task 5: Refined delete_order Function
=================================================
This script tests and demonstrates the refined delete_order(order_id)
function generated via ChatGPT/Copilot and hardened with:
- Parameterized SQL query
- cursor.rowcount verification (handling non-existent order_id)
- Input validation and resource cleanup
"""

import sys
import os
import sqlite3
from typing import Dict, Any

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "mcp_database.db")

def delete_order(order_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Deletes an order by order_id from the SQLite database.

    Parameters:
    - order_id: Unique identifier of the order to delete.
    - db_path: Path to the SQLite database.

    Returns:
    - Dictionary with status, message, and rows_affected.
    """
    if not order_id or not str(order_id).strip():
        return {
            "status": "error",
            "message": "order_id must be a non-empty string.",
            "statusCode": 400
        }

    clean_order_id = str(order_id).strip()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Parameterized query protects against SQL injection
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (clean_order_id,))
        conn.commit()

        if cursor.rowcount > 0:
            return {
                "status": "success",
                "message": f"Order '{clean_order_id}' was successfully deleted.",
                "deleted_order_id": clean_order_id,
                "rows_affected": cursor.rowcount,
                "statusCode": 200
            }
        else:
            return {
                "status": "error",
                "message": f"Order with ID '{clean_order_id}' not found. No rows deleted.",
                "statusCode": 404
            }
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error while deleting order: {e}",
            "statusCode": 500
        }
    finally:
        conn.close()

def run_task5_demo():
    print("=" * 65)
    print("     SESSION 17 - TASK 5: REFINED delete_order FUNCTION")
    print("=" * 65)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO orders (order_id, user_id, amount, order_time) VALUES (?, ?, ?, ?)",
        ("ORD_DEL_TEST_01", "USR_101", 599.00, "2026-09-26 14:00:00")
    )
    conn.commit()
    conn.close()
    print("[+] Prepared test order 'ORD_DEL_TEST_01' in database.")

    # Test 1: Successful deletion
    print("\n--- Test 1: Deleting Existing Order 'ORD_DEL_TEST_01' ---")
    res1 = delete_order("ORD_DEL_TEST_01")
    print(f"[*] Status:         {res1['status']}")
    print(f"[*] Message:        {res1['message']}")
    print(f"[*] Rows Affected:  {res1.get('rows_affected')}")

    # Test 2: Deleting non-existent order
    print("\n" + "-" * 65)
    print("--- Test 2: Deleting Non-Existent Order (Second Attempt) ---")
    res2 = delete_order("ORD_DEL_TEST_01")
    print(f"[*] Status:         {res2['status']}")
    print(f"[*] Message:        {res2['message']}")
    print(f"[*] Status Code:    {res2.get('statusCode')}")

    # Test 3: SQL Injection Prevention Test
    print("\n" + "-" * 65)
    print("--- Test 3: Testing SQL Injection Prevention on Deletion ---")
    malicious_delete = "' OR '1'='1"
    res3 = delete_order(malicious_delete)
    print(f"[*] Status:         {res3['status']}")
    print(f"[*] Message:        {res3['message']}")

    print("\n" + "=" * 65)
    print("[SUCCESS] Task 5 completed: delete_order function tested and refined!")

if __name__ == "__main__":
    run_task5_demo()
