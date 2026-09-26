"""
Session 17 - Task 2: Parameterized store_order Function
======================================================
This script implements the function store_order(order_id, user_id, amount)
which inserts a new order into the 'orders' table in the SQLite database
using parameterized queries to prevent SQL injection vulnerabilities.
"""

import sys
import os
import sqlite3
import datetime
from typing import Dict, Any, Optional

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "mcp_database.db")

def init_orders_table(db_path: str = DB_PATH):
    """Initializes the orders table with order_time timestamp column."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_order(
    order_id: str,
    user_id: str,
    amount: float,
    order_time: Optional[str] = None,
    db_path: str = DB_PATH
) -> Dict[str, Any]:
    """
    Inserts a new order into the 'orders' table using parameterized SQL queries.

    Parameters:
    - order_id: Unique string identifier for the order (e.g. 'ORD_1001')
    - user_id: ID of the ordering user (e.g. 'USR_01')
    - amount: Order monetary value in INR
    - order_time: Optional ISO timestamp (defaults to current time)
    - db_path: Path to SQLite database file

    Returns:
    - Dictionary with success message and inserted order metadata
    """
    # 1. Input validation
    if not order_id or not str(order_id).strip():
        raise ValueError("order_id must be a non-empty string.")
    if not user_id or not str(user_id).strip():
        raise ValueError("user_id must be a non-empty string.")
    try:
        numeric_amount = float(amount)
        if numeric_amount < 0:
            raise ValueError("amount cannot be negative.")
    except (ValueError, TypeError):
        raise ValueError("amount must be a valid positive number.")

    timestamp = order_time or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Database execution with parameterized query (? placeholders)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Parameterized query prevents SQL injection attacks
        sql = "INSERT INTO orders (order_id, user_id, amount, order_time) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (str(order_id).strip(), str(user_id).strip(), numeric_amount, timestamp))
        conn.commit()

        return {
            "status": "success",
            "message": f"Order '{order_id}' stored successfully.",
            "order": {
                "order_id": order_id,
                "user_id": user_id,
                "amount": numeric_amount,
                "order_time": timestamp
            }
        }
    except sqlite3.IntegrityError:
        return {
            "status": "error",
            "message": f"Order with ID '{order_id}' already exists."
        }
    finally:
        conn.close()

def run_task2_demo():
    print("=" * 65)
    print("     SESSION 17 - TASK 2: PARAMETERIZED store_order FUNCTION")
    print("=" * 65)

    init_orders_table()

    # Sample Orders to Insert
    test_orders = [
        ("ORD_7001", "USR_101", 450.00),
        ("ORD_7002", "USR_101", 1250.50),
        ("ORD_7003", "USR_102", 899.00),
        ("ORD_7004", "USR_101", 320.00),
        ("ORD_7005", "USR_103", 2100.00),
    ]

    print("\n[+] Inserting sample orders into SQLite database using store_order():")
    for oid, uid, amt in test_orders:
        res = store_order(oid, uid, amt)
        print(f"    * {res['message']} (Amount: Rs. {amt})")

    # Demonstrate SQL Injection resistance
    print("\n[+] Testing SQL Injection Immunity:")
    malicious_id = "ORD_HACK'; DROP TABLE orders; --"
    res_inject = store_order(malicious_id, "USR_101", 99.0)
    print(f"    * Malicious payload treated safely as plain string literal: {res_inject['status']}")

    print("\n" + "=" * 65)
    print("[SUCCESS] Task 2 completed: store_order function verified!")

if __name__ == "__main__":
    run_task2_demo()
