"""
Session 16 - Task 5: User Profile Endpoint (/user-profile)
==========================================================
This script implements and tests the '/user-profile' endpoint generated
via ChatGPT/Copilot and integrated into the MCP Server.
Given a 'userId', it returns a mock user profile with name, email, and phone.
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

# Predefined Mock User Profiles Database
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

@app.route("/", methods=["GET"])
def root():
    return "MCP Server Running", 200

@app.route("/user-profile", methods=["GET", "POST"])
def user_profile():
    """
    Retrieves mock user profile by userId.
    Supports:
    - GET /user-profile?userId=USR_101
    - POST /user-profile with body { "userId": "USR_101" }
    """
    user_id = None

    if request.method == "POST":
        data = request.get_json(silent=True)
        if data:
            user_id = data.get("userId")
    else:
        user_id = request.args.get("userId")

    # Error handling: Missing userId
    if not user_id or not str(user_id).strip():
        return jsonify({
            "error": "Bad Request",
            "message": "Missing required parameter: 'userId'",
            "statusCode": 400
        }), 400

    clean_user_id = str(user_id).strip()

    # Lookup profile or dynamically synthesize realistic mock profile
    if clean_user_id in USER_PROFILES_DB:
        profile = USER_PROFILES_DB[clean_user_id]
    else:
        profile = {
            "name": f"User {clean_user_id}",
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
    print("     SESSION 16 - TASK 5: USER PROFILE ENDPOINT")
    print("=" * 65)
    print("[*] Server running on: http://127.0.0.1:5000/")
    print("[*] Endpoint:          GET/POST /user-profile")
    print("[*] Press Ctrl+C to stop.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    start_server()
