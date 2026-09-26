"""
Session 18 - Task 2: File Listing Command ('LIST')
==================================================
This script modifies the MCP server to handle file listing requests:
When a client sends the command 'LIST', the server responds with
the names and sizes of all files in the 'music' folder (simulating
a mini Spotify backend).
"""

import sys
import os
import socket
import threading

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HOST = "127.0.0.1"
PORT = 6500
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(CURRENT_DIR, "music")

def get_file_list() -> str:
    """Scans the music directory and formats the file list."""
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR, exist_ok=True)

    files = [f for f in os.listdir(MUSIC_DIR) if os.path.isfile(os.path.join(MUSIC_DIR, f))]
    if not files:
        return "OK: The music directory is currently empty.\n"

    lines = [f"OK: {len(files)} file(s) available in music repository:"]
    for f in sorted(files):
        fpath = os.path.join(MUSIC_DIR, f)
        size = os.path.getsize(fpath)
        lines.append(f"  • {f} ({size} bytes)")
    return "\n".join(lines) + "\n"

def handle_client(client_socket: socket.socket, client_address):
    print(f"[+] Client connected from {client_address}")
    try:
        client_socket.sendall(b"MCP Music Server Ready. Send 'LIST' or 'EXIT'.\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            command = data.decode("utf-8").strip()
            print(f"[{client_address}] Command: '{command}'")

            if command.upper() == "LIST":
                response = get_file_list()
                client_socket.sendall(response.encode("utf-8"))
            elif command.upper() == "EXIT":
                client_socket.sendall(b"BYE: Connection closed.\n")
                break
            else:
                client_socket.sendall(f"ERR: Unrecognized command '{command}'. Try 'LIST'.\n".encode("utf-8"))
    except Exception as e:
        print(f"[-] Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[-] Client disconnected: {client_address}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print("=" * 65)
    print("     SESSION 18 - TASK 2: FILE LISTING SERVER ('LIST')")
    print("=" * 65)
    print(f"[*] MCP Server listening on {HOST}:{PORT}")
    print(f"[*] Music Folder: {MUSIC_DIR}")
    print("[*] Ready to process 'LIST' command...")
    print("=" * 65)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            t = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
