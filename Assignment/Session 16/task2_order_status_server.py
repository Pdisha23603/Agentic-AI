"""
Session 16 - Task 2: MCP Server with /order-status Endpoint
===========================================================
This script adds the '/order-status' endpoint to the MCP server.
It accepts a POST request with a JSON payload containing 'orderId'
and returns a simulated order status ('Delivered', 'In Transit', or 'Cancelled').
"""

import sys
import random
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
def order_status():
    """
    POST /order-status
    Accepts: { "orderId": "OD12345678" }
    Returns: Simulated order tracking status
    """
    data = request.get_json(silent=True) or {}
    order_id = data.get("orderId", "UNKNOWN")

    # Consistent deterministic or randomized simulation
    # Hash order_id for stable status, or select from list
    status = STATUS_CHOICES[hash(order_id) % len(STATUS_CHOICES)]

    response_payload = {
        "orderId": order_id,
        "status": status,
        "carrier": "Ekart Logistics",
        "estimatedDelivery": "Within 2 business days" if status == "In Transit" else "Completed"
    }

    return jsonify(response_payload), 200

def start_server():
    print("=" * 65)
    print("     SESSION 16 - TASK 2: MCP SERVER (/order-status)")
    print("=" * 65)
    print("[*] Server running on: http://127.0.0.1:5000/")
    print("[*] Endpoint:          POST /order-status")
    print("[*] Press Ctrl+C to stop.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    start_server()
