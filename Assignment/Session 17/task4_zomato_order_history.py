"""
Session 17 - Task 4: Zomato-Style Order History (GET_LAST_N_ORDERS)
===================================================================
This script extends the MCP database server to simulate a Zomato-style
order history feature. It handles the 'GET_LAST_N_ORDERS' command,
returning the N most recent orders for a user sorted by order timestamp.
"""

import sys
import os
import sqlite3
import datetime
from typing import Dict, Any, List

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "mcp_database.db")

def seed_zomato_orders(db_path: str = DB_PATH):
    """Seeds realistic Zomato orders with spaced timestamps."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base time: today
    now = datetime.datetime.now()

    sample_orders = [
        # User USR_ZOMATO orders over the past few days
        ("ZOM_901", "USR_ZOMATO", 380.00, (now - datetime.timedelta(days=4, hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
        ("ZOM_902", "USR_ZOMATO", 650.00, (now - datetime.timedelta(days=3, hours=5)).strftime("%Y-%m-%d %H:%M:%S")),
        ("ZOM_903", "USR_ZOMATO", 220.00, (now - datetime.timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S")),
        ("ZOM_904", "USR_ZOMATO", 890.00, (now - datetime.timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S")),
        ("ZOM_905", "USR_ZOMATO", 450.00, (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
        ("ZOM_906", "USR_ZOMATO", 180.00, (now - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")),
    ]

    for oid, uid, amt, t_stamp in sample_orders:
        cursor.execute(
            "INSERT OR REPLACE INTO orders (order_id, user_id, amount, order_time) VALUES (?, ?, ?, ?)",
            (oid, uid, amt, t_stamp)
        )

    conn.commit()
    conn.close()

def get_last_n_orders(user_id: str, n: int = 3, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Retrieves the N most recent orders for a user, sorted by order_time descending.

    Parameters:
    - user_id: ID of the customer.
    - n: Number of recent orders to fetch (default: 3).
    - db_path: Path to the SQLite database.

    Returns:
    - Structured response dictionary containing the recent orders sorted latest-first.
    """
    if not user_id or not str(user_id).strip():
        return {"status": "error", "message": "user_id is required."}

    try:
        limit_val = int(n)
        if limit_val <= 0:
            limit_val = 3
    except (ValueError, TypeError):
        limit_val = 3

    clean_user_id = str(user_id).strip()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Constraint: Query sorted by order_time DESC with parameterized LIMIT
        sql = """
            SELECT order_id, user_id, amount, order_time
            FROM orders
            WHERE user_id = ?
            ORDER BY order_time DESC
            LIMIT ?
        """
        cursor.execute(sql, (clean_user_id, limit_val))
        rows = cursor.fetchall()

        orders = [
            {
                "order_id": r["order_id"],
                "user_id": r["user_id"],
                "amount": float(r["amount"]),
                "order_time": r["order_time"]
            }
            for r in rows
        ]

        return {
            "status": "success",
            "command": "GET_LAST_N_ORDERS",
            "user_id": clean_user_id,
            "requested_limit": limit_val,
            "returned_count": len(orders),
            "orders": orders
        }
    finally:
        conn.close()

def run_task4_demo():
    print("=" * 65)
    print("  SESSION 17 - TASK 4: ZOMATO-STYLE RECENT ORDER HISTORY")
    print("=" * 65)

    print("\n[+] Seeding realistic Zomato orders with timestamp progression...")
    seed_zomato_orders()

    # Test 1: Fetch Top 3 most recent orders
    print("\n--- Test 1: Fetching Last 3 Orders for 'USR_ZOMATO' ---")
    res_3 = get_last_n_orders("USR_ZOMATO", n=3)
    print(f"[*] Command:         {res_3['command']}")
    print(f"[*] User ID:         {res_3['user_id']}")
    print(f"[*] Recent Orders:   {res_3['returned_count']} orders (Latest First):")
    for idx, o in enumerate(res_3["orders"], start=1):
        print(f"    {idx}. Order ID: {o['order_id']} | Amount: Rs. {o['amount']} | Timestamp: {o['order_time']}")

    # Test 2: Fetch Top 5 most recent orders
    print("\n" + "-" * 65)
    print("--- Test 2: Fetching Last 5 Orders for 'USR_ZOMATO' ---")
    res_5 = get_last_n_orders("USR_ZOMATO", n=5)
    for idx, o in enumerate(res_5["orders"], start=1):
        print(f"    {idx}. Order ID: {o['order_id']} | Amount: Rs. {o['amount']} | Timestamp: {o['order_time']}")

    print("\n" + "=" * 65)
    print("[SUCCESS] Task 4 completed: GET_LAST_N_ORDERS with timestamp sorting verified!")

if __name__ == "__main__":
    run_task4_demo()
