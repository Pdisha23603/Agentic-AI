"""
Session 16: Complete Business MCP Server (Tasks 1 to 5)
======================================================
This is the complete, integrated Business Multi-Channel Processing (MCP)
server combining all Session 16 tasks:

Endpoints:
1. GET  /             -> Responds with 'MCP Server Running' (Task 1)
2. POST /order-status -> Returns order status with 400 validation (Tasks 2 & 3)
3. POST /notify       -> Logs notifications to 'notifications.log' (Task 4)
4. GET  /user-profile -> Returns mock user profile (name, email, phone) (Task 5)
5. POST /user-profile -> JSON body support for user profile lookup
"""

import sys
import os
import datetime
from flask import Flask, request, jsonify

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(CURRENT_DIR, "notifications.log")

STATUS_OPTIONS = ["Delivered", "In Transit", "Cancelled", "Out for Delivery"]

# Mock User Profiles Database
USER_PROFILES_DB = {
    "USR_101": {
        "name": "Nishant Patel",
        "email": "nishant.patel@example.com",
        "phone": "+91-9876543210",
        "city": "Ahmedabad",
        "memberTier": "Flipkart Plus Member",
        "joinedDate": "2021-04-15"
    },
    "USR_102": {
        "name": "Rohit Sharma",
        "email": "rohit.sharma@example.com",
        "phone": "+91-9820012345",
        "city": "Mumbai",
        "memberTier": "Flipkart VIP Member",
        "joinedDate": "2019-11-20"
    },
    "USR_103": {
        "name": "Priya Sen",
        "email": "priya.sen@example.com",
        "phone": "+91-9933221100",
        "city": "Kolkata",
        "memberTier": "Standard Member",
        "joinedDate": "2023-01-10"
    }
}

# ==============================================================================
# TASK 1: Root Endpoint
# ==============================================================================
@app.route("/", methods=["GET"])
def root():
    """Responds with 'MCP Server Running'."""
    return "MCP Server Running", 200

# ==============================================================================
# TASKS 2 & 3: Order Status Endpoint with HTTP 400 Error Handling
# ==============================================================================
@app.route("/order-status", methods=["POST"])
def order_status():
    """
    POST /order-status
    Payload: { "orderId": "OD10029384" }
    Validates presence of orderId; returns 400 if missing.
    """
    data = request.get_json(silent=True)

    # Error handling for missing JSON or missing orderId
    if not data or "orderId" not in data or not str(data["orderId"]).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required field: 'orderId'",
            "requiredFields": ["orderId"],
            "statusCode": 400
        }), 400

    order_id = str(data["orderId"]).strip()
    status = STATUS_OPTIONS[hash(order_id) % len(STATUS_OPTIONS)]

    return jsonify({
        "orderId": order_id,
        "status": status,
        "carrier": "Ekart Logistics",
        "estimatedDelivery": "Within 2 business days" if status == "In Transit" else "Completed",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200

# ==============================================================================
# TASK 4: Flipkart-Style Notification System (/notify)
# ==============================================================================
@app.route("/notify", methods=["POST"])
def notify():
    """
    POST /notify
    Payload: { "userId": "USR_101", "message": "Your package has arrived!" }
    Appends entry to notifications.log
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Bad Request",
            "message": "Payload must be a valid JSON object.",
            "statusCode": 400
        }), 400

    user_id = data.get("userId")
    message = data.get("message")

    if not user_id or not str(user_id).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required field: 'userId'",
            "statusCode": 400
        }), 400

    if not message or not str(message).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required field: 'message'",
            "statusCode": 400
        }), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [USER: {user_id}] NOTIFICATION: {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"[+] Notification logged for user '{user_id}' to notifications.log")

    return jsonify({
        "status": "success",
        "message": "Notification dispatched and logged successfully.",
        "recipient": user_id,
        "loggedAt": timestamp
    }), 200

# ==============================================================================
# TASK 5: User Profile Endpoint (/user-profile)
# ==============================================================================
@app.route("/user-profile", methods=["GET", "POST"])
def user_profile():
    """
    GET /user-profile?userId=USR_101
    POST /user-profile with { "userId": "USR_101" }
    """
    user_id = None
    if request.method == "POST":
        data = request.get_json(silent=True)
        if data:
            user_id = data.get("userId")
    else:
        user_id = request.args.get("userId")

    if not user_id or not str(user_id).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required parameter: 'userId'",
            "statusCode": 400
        }), 400

    clean_user_id = str(user_id).strip()

    if clean_user_id in USER_PROFILES_DB:
        profile = USER_PROFILES_DB[clean_user_id]
    else:
        profile = {
            "name": f"Customer {clean_user_id}",
            "email": f"{clean_user_id.lower()}@flipkart-shopper.in",
            "phone": "+91-98" + "".join([str(abs(hash(clean_user_id)) % 10) for _ in range(8)]),
            "city": "Bengaluru",
            "memberTier": "Standard Member",
            "joinedDate": "2024-01-01"
        }

    return jsonify({
        "status": "success",
        "userId": clean_user_id,
        "profile": profile
    }), 200

def start_server():
    print("=" * 65)
    print("     SESSION 16: INTEGRATED BUSINESS MCP SERVER")
    print("=" * 65)
    print("[*] Running on:        http://127.0.0.1:5000/")
    print("[*] Task 1 Endpoint:   GET  /")
    print("[*] Tasks 2 & 3:       POST /order-status")
    print("[*] Task 4 Endpoint:   POST /notify (Logs to notifications.log)")
    print("[*] Task 5 Endpoint:   GET/POST /user-profile")
    print("[*] Press Ctrl+C to terminate.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    start_server()
