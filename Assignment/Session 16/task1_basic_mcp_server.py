"""
Session 16 - Task 1: Basic Flask MCP Server
============================================
This script sets up a basic Multi-Channel Processing (MCP) server using
Python and Flask that listens on port 5000 and responds with
'MCP Server Running' when accessed at the root endpoint ('/').
"""

import sys
from flask import Flask

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    """Root endpoint responding with a confirmation message."""
    return "MCP Server Running", 200

def start_server():
    print("=" * 65)
    print("       SESSION 16 - TASK 1: BASIC FLASK MCP SERVER")
    print("=" * 65)
    print("[*] Server running on: http://127.0.0.1:5000/")
    print("[*] Root Endpoint:     GET / -> 'MCP Server Running'")
    print("[*] Press Ctrl+C to stop.")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    start_server()
