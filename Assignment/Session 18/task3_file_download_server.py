"""
Session 18 - Task 3: File Download Support ('GET filename')
===========================================================
This script extends the MCP server to support file downloading:
When a client sends 'GET filename', the server reads the file in binary
mode and sends its contents back to the client.
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

def handle_get_command(filename: str, client_socket: socket.socket):
    """Handles GET filename: transmits file contents to client."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(MUSIC_DIR, safe_filename)

    if not os.path.exists(filepath):
        client_socket.sendall(f"ERR: File '{safe_filename}' not found.\n".encode("utf-8"))
        return

    file_size = os.path.getsize(filepath)
    # Header format: OK: FILE <filename> SIZE <bytes>\n
    header = f"OK: FILE {safe_filename} SIZE {file_size}\n"
    client_socket.sendall(header.encode("utf-8"))

    # Transmit file data
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            client_socket.sendall(chunk)
    print(f"[+] Successfully sent '{safe_filename}' ({file_size} bytes)")

def handle_client(client_socket: socket.socket, client_address):
    print(f"[+] Client connected from {client_address}")
    try:
        client_socket.sendall(b"MCP File Server Ready. Commands: LIST, GET <filename>, EXIT\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            line = data.decode("utf-8").strip()
            print(f"[{client_address}] Command: '{line}'")

            if line.upper() == "LIST":
                files = os.listdir(MUSIC_DIR)
                res = "OK: Files: " + ", ".join(files) + "\n"
                client_socket.sendall(res.encode("utf-8"))
            elif line.upper().startswith("GET "):
                parts = line.split(" ", 1)
                if len(parts) > 1:
                    handle_get_command(parts[1].strip(), client_socket)
                else:
                    client_socket.sendall(b"ERR: Usage: GET <filename>\n")
            elif line.upper() == "EXIT":
                client_socket.sendall(b"BYE\n")
                break
            else:
                client_socket.sendall(b"ERR: Unknown command.\n")
    except Exception as e:
        print(f"[-] Client error: {e}")
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[*] Task 3 Server listening on http://{HOST}:{PORT} (Music Dir: {MUSIC_DIR})")
    try:
        while True:
            c, a = server_socket.accept()
            threading.Thread(target=handle_client, args=(c, a), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
