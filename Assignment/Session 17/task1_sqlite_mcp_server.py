"""
Session 17 - Task 1: SQLite Database MCP Server
===============================================
This script sets up a basic SQLite-backed Multi-Channel Processing (MCP)
server. It initializes an SQLite database and handles basic commands to
add and retrieve user data.
"""

import sys
import os
import sqlite3
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

def init_db():
    """Initializes the SQLite database with users table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "online",
        "server": "Database-MCP-Server",
        "database": "SQLite",
        "port": PORT
    }), 200

@app.route("/user", methods=["POST"])
def add_user():
    """Command/Endpoint to add user data."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone", "")

    if not user_id or not name or not email:
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required fields: user_id, name, email"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, name, email, phone) VALUES (?, ?, ?, ?)",
            (user_id, name, email, phone)
        )
        conn.commit()
        return jsonify({
            "status": "success",
            "message": f"User '{name}' (ID: {user_id}) created successfully."
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Conflict",
            "message": f"User with ID '{user_id}' already exists."
        }), 409
    finally:
        conn.close()

@app.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    """Command/Endpoint to retrieve user data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, phone, created_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({
            "error": "Not Found",
            "message": f"User with ID '{user_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "user": dict(row)
    }), 200

def start_server():
    init_db()
    print("=" * 65)
    print("     SESSION 17 - TASK 1: SQLITE DATABASE MCP SERVER")
    print("=" * 65)
    print(f"[*] Database Path:  {DB_PATH}")
    print(f"[*] Listening on:   http://127.0.0.1:{PORT}/")
    print(f"[*] Endpoints:      POST /user | GET /user/<user_id>")
    print("[*] Press Ctrl+C to terminate.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=PORT, debug=False)

if __name__ == "__main__":
    start_server()
