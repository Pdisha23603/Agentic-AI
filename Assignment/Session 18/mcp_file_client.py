"""
Session 18: Interactive MCP File Server Client
==============================================
This script provides an interactive terminal client to connect to the
MCP File Server on port 6500. It allows sending commands:
- LIST
- GET <filename>
- DELETE <filename>
- HELP
- EXIT
"""

import sys
import socket

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HOST = "127.0.0.1"
PORT = 6500

def run_client():
    print("=" * 65)
    print("    SESSION 18: MCP FILE SERVER INTERACTIVE CLIENT")
    print("=" * 65)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        banner = s.recv(2048).decode("utf-8")
        print(banner)

        while True:
            cmd = input("MCP-Server> ").strip()
            if not cmd:
                continue

            s.sendall((cmd + "\n").encode("utf-8"))

            if cmd.upper() == "EXIT":
                res = s.recv(1024).decode("utf-8")
                print(res)
                break

            response = s.recv(4096).decode("utf-8", errors="replace")
            print(response)

    except ConnectionRefusedError:
        print(f"[-] Could not connect to {HOST}:{PORT}. Ensure 'mcp_file_server.py' is running.")
    except Exception as e:
        print(f"[-] Client error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    run_client()
