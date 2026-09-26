"""
Session 17: Integrated Database MCP Server (Tasks 1 to 5)
=========================================================
This is the complete, integrated SQLite-backed Multi-Channel Processing (MCP)
server combining all tasks of Session 17 on Port 5001:

Features & Endpoints:
1. GET    /                        -> Server Health Check (Task 1)
2. POST   /user                    -> Add User (Task 1)
3. GET    /user/<user_id>          -> Retrieve User (Task 1)
4. POST   /order                   -> store_order() with parameterization (Task 2)
5. GET    /orders/user/<user_id>   -> GET_USER_ORDERS handler (Task 3)
6. GET    /orders/recent           -> GET_LAST_N_ORDERS (Zomato-style timestamp sort) (Task 4)
7. DELETE /order/<order_id>        -> delete_order() with rowcount check (Task 5)
8. POST   /command                 -> Universal Command Dispatcher (Handles string commands)
"""

import sys
import os
import sqlite3
import datetime
from flask import Flask, request, jsonify

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)
PORT = 5001
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "mcp_database.db")

# ==============================================================================
# Database Initialization
# ==============================================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Orders Table with timestamp constraint
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

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==============================================================================
# TASK 1: Root & User Endpoints
# ==============================================================================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "online",
        "server": "Integrated-Database-MCP-Server",
        "database": "SQLite3",
        "port": PORT,
        "capabilities": [
            "User Management",
            "store_order (Parameterized)",
            "GET_USER_ORDERS",
            "GET_LAST_N_ORDERS (Timestamp Sorted)",
            "delete_order (Verified Deletion)"
        ]
    }), 200

@app.route("/user", methods=["POST"])
def add_user():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone", "")

    if not user_id or not name or not email:
        return jsonify({"error": "Bad Request", "message": "Missing user_id, name, or email"}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, name, email, phone) VALUES (?, ?, ?, ?)",
            (user_id, name, email, phone)
        )
        conn.commit()
        return jsonify({"status": "success", "message": f"User '{name}' added successfully."}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Conflict", "message": f"User '{user_id}' already exists."}), 409
    finally:
        conn.close()

@app.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not Found", "message": f"User '{user_id}' not found."}), 404
    return jsonify({"status": "success", "user": dict(row)}), 200

# ==============================================================================
# TASK 2: store_order Function & Endpoint
# ==============================================================================
def store_order(order_id: str, user_id: str, amount: float, order_time: str = None) -> dict:
    timestamp = order_time or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO orders (order_id, user_id, amount, order_time) VALUES (?, ?, ?, ?)",
            (order_id, user_id, float(amount), timestamp)
        )
        conn.commit()
        return {
            "status": "success",
            "message": f"Order '{order_id}' stored successfully.",
            "order": {"order_id": order_id, "user_id": user_id, "amount": float(amount), "order_time": timestamp}
        }
    except sqlite3.IntegrityError:
        return {"status": "error", "message": f"Order ID '{order_id}' already exists."}
    finally:
        conn.close()

@app.route("/order", methods=["POST"])
def endpoint_store_order():
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    user_id = data.get("user_id")
    amount = data.get("amount")
    order_time = data.get("order_time")

    if not order_id or not user_id or amount is None:
        return jsonify({"error": "Bad Request", "message": "Missing order_id, user_id, or amount"}), 400

    result = store_order(order_id, user_id, amount, order_time)
    status_code = 201 if result["status"] == "success" else 409
    return jsonify(result), status_code

# ==============================================================================
# TASK 3: GET_USER_ORDERS Handler & Endpoint
# ==============================================================================
def get_user_orders(user_id: str) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT order_id, amount, order_time FROM orders WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    orders_list = [{"order_id": r["order_id"], "amount": float(r["amount"]), "order_time": r["order_time"]} for r in rows]
    return {
        "status": "success",
        "command": "GET_USER_ORDERS",
        "user_id": user_id,
        "count": len(orders_list),
        "orders": orders_list
    }

@app.route("/orders/user/<user_id>", methods=["GET"])
def endpoint_get_user_orders(user_id):
    return jsonify(get_user_orders(user_id)), 200

# ==============================================================================
# TASK 4: Zomato-Style GET_LAST_N_ORDERS Handler & Endpoint
# ==============================================================================
def get_last_n_orders(user_id: str, n: int = 3) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, user_id, amount, order_time
        FROM orders
        WHERE user_id = ?
        ORDER BY order_time DESC
        LIMIT ?
    """, (user_id, int(n)))
    rows = cursor.fetchall()
    conn.close()

    orders = [dict(r) for r in rows]
    return {
        "status": "success",
        "command": "GET_LAST_N_ORDERS",
        "user_id": user_id,
        "limit": int(n),
        "count": len(orders),
        "orders": orders
    }

@app.route("/orders/recent", methods=["GET"])
def endpoint_get_last_n_orders():
    user_id = request.args.get("user_id")
    limit = request.args.get("limit", 3)
    if not user_id:
        return jsonify({"error": "Bad Request", "message": "Query param 'user_id' is required"}), 400
    return jsonify(get_last_n_orders(user_id, int(limit))), 200

# ==============================================================================
# TASK 5: delete_order Function & Endpoint
# ==============================================================================
def delete_order(order_id: str) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {
                "status": "success",
                "message": f"Order '{order_id}' deleted successfully.",
                "rows_affected": cursor.rowcount,
                "statusCode": 200
            }
        else:
            return {
                "status": "error",
                "message": f"Order '{order_id}' not found.",
                "statusCode": 404
            }
    finally:
        conn.close()

@app.route("/order/<order_id>", methods=["DELETE"])
def endpoint_delete_order(order_id):
    res = delete_order(order_id)
    return jsonify(res), res["statusCode"]

# ==============================================================================
# Universal MCP Command Dispatcher (POST /command)
# ==============================================================================
@app.route("/command", methods=["POST"])
def mcp_command_dispatcher():
    data = request.get_json(silent=True) or {}
    cmd = (data.get("command") or "").upper()
    params = data.get("params") or {}

    if cmd == "GET_USER_ORDERS":
        uid = params.get("user_id")
        if not uid:
            return jsonify({"error": "Missing params.user_id"}), 400
        return jsonify(get_user_orders(uid)), 200

    elif cmd == "GET_LAST_N_ORDERS":
        uid = params.get("user_id")
        n = params.get("n", 3)
        if not uid:
            return jsonify({"error": "Missing params.user_id"}), 400
        return jsonify(get_last_n_orders(uid, n)), 200

    elif cmd == "STORE_ORDER":
        res = store_order(params.get("order_id"), params.get("user_id"), params.get("amount"))
        return jsonify(res), 200

    elif cmd == "DELETE_ORDER":
        res = delete_order(params.get("order_id"))
        return jsonify(res), res["statusCode"]

    return jsonify({"error": f"Unknown command: '{cmd}'"}), 400

def start_server():
    init_db()
    print("=" * 65)
    print("     SESSION 17: INTEGRATED DATABASE MCP SERVER")
    print("=" * 65)
    print(f"[*] Port:        http://127.0.0.1:{PORT}/")
    print(f"[*] Database:    {DB_PATH}")
    print("[*] Features:    Users, store_order, GET_USER_ORDERS,")
    print("                 GET_LAST_N_ORDERS (Zomato style), delete_order")
    print("[*] Press Ctrl+C to terminate.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=PORT, debug=False)

if __name__ == "__main__":
    start_server()
