"""
Session 16 - Task 3: Error Handling on /order-status (HTTP 400)
==============================================================
This script adds error handling to the '/order-status' endpoint:
If the JSON payload is missing, or the required key 'orderId' is absent or empty,
it returns a structured JSON error response with HTTP Status Code 400 Bad Request.
"""

import sys
from flask import Flask, request, jsonify

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)

STATUS_CHOICES = ["Delivered", "In Transit", "Cancelled", "Out for Delivery"]

@app.route("/", methods=["GET"])
def root():
    return "MCP Server Running", 200

@app.route("/order-status", methods=["POST"])
def order_status_with_error_handling():
    """
    POST /order-status
    Validates that:
    1. Content-Type is JSON and request body is valid JSON.
    2. 'orderId' key exists and is non-empty.
    Returns:
    - 200 OK with order details if valid.
    - 400 Bad Request with JSON error message if invalid.
    """
    data = request.get_json(silent=True)

    # Error Check 1: Missing JSON Body
    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Request payload must be a valid JSON object.",
            "statusCode": 400
        }), 400

    # Error Check 2: Missing or Empty 'orderId' field
    if "orderId" not in data or not str(data["orderId"]).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required field: 'orderId'",
            "requiredFields": ["orderId"],
            "statusCode": 400
        }), 400

    order_id = str(data["orderId"]).strip()
    status = STATUS_CHOICES[hash(order_id) % len(STATUS_CHOICES)]

    return jsonify({
        "orderId": order_id,
        "status": status,
        "carrier": "Ekart Logistics",
        "timestamp": "2026-09-26T14:20:00Z"
    }), 200

def start_server():
    print("=" * 65)
    print("     SESSION 16 - TASK 3: ERROR HANDLING (/order-status)")
    print("=" * 65)
    print("[*] Server running on: http://127.0.0.1:5000/")
    print("[*] Endpoint:          POST /order-status")
    print("[*] Validation:        Returns HTTP 400 if 'orderId' is missing")
    print("[*] Press Ctrl+C to stop.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    start_server()
