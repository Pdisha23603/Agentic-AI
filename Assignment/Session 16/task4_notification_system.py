"""
Session 16 - Task 4: Flipkart-Style Notification System (/notify)
================================================================
This script adds the '/notify' endpoint to the MCP server.
It accepts a JSON payload with 'userId' and 'message', then logs
the notification event with a timestamp to 'notifications.log'.
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

@app.route("/", methods=["GET"])
def root():
    return "MCP Server Running", 200

@app.route("/order-status", methods=["POST"])
def order_status():
    data = request.get_json(silent=True)
    if not data or "orderId" not in data or not str(data["orderId"]).strip():
        return jsonify({"error": "Bad Request", "message": "Missing required field: 'orderId'"}), 400
    return jsonify({"orderId": data["orderId"], "status": "In Transit"}), 200

@app.route("/notify", methods=["POST"])
def notify():
    """
    POST /notify
    Payload: { "userId": "user_101", "message": "Your Flipkart order has shipped!" }
    Logs notification to 'notifications.log'
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Payload must be valid JSON.",
            "statusCode": 400
        }), 400

    user_id = data.get("userId")
    message = data.get("message")

    # Validate required fields
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

    # Format log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [USER: {user_id}] NOTIFICATION: {message}\n"

    # Append to notifications.log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"[+] Logged notification for user '{user_id}' to {os.path.basename(LOG_FILE)}")

    return jsonify({
        "status": "success",
        "message": "Notification dispatched and logged successfully.",
        "loggedAt": timestamp,
        "recipient": user_id
    }), 200

def start_server():
    print("=" * 65)
    print("     SESSION 16 - TASK 4: NOTIFICATION SYSTEM (/notify)")
    print("=" * 65)
    print(f"[*] Server running on: http://127.0.0.1:5000/")
    print(f"[*] Notification Log:  {LOG_FILE}")
    print("[*] Endpoint:          POST /notify")
    print("[*] Press Ctrl+C to stop.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    start_server()
