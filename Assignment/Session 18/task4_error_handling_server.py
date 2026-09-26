"""
Session 18 - Task 4: Error Handling on File Access
=================================================
This script adds comprehensive error handling using try-except blocks:
If a client requests a file that does not exist, or uses directory traversal
characters, the server catches FileNotFoundError and sends a custom error
message instead of crashing.
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

def safe_download_file(filename: str, client_socket: socket.socket):
    """
    Safely opens and sends a file with try-except error handling.
    Catches:
    - FileNotFoundError (Custom user-friendly response)
    - PermissionError
    - Path traversal attempts
    """
    clean_name = filename.strip()

    # Security check: Prevent path traversal attacks
    if ".." in clean_name or "/" in clean_name or "\\" in clean_name:
        err_msg = f"ERR: SECURITY_VIOLATION: Path traversal is not allowed. Filename: '{clean_name}'\n"
        client_socket.sendall(err_msg.encode("utf-8"))
        print(f"[-] Blocked path traversal attempt: {clean_name}")
        return

    filepath = os.path.join(MUSIC_DIR, clean_name)

    # Core try-except error handling
    try:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File '{clean_name}' does not exist.")

        file_size = os.path.getsize(filepath)
        header = f"OK: FILE {clean_name} SIZE {file_size}\n"
        client_socket.sendall(header.encode("utf-8"))

        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                client_socket.sendall(chunk)

        print(f"[+] Download complete: '{clean_name}' ({file_size} bytes)")

    except FileNotFoundError:
        # Custom error response as requested in Task 4
        error_response = f"ERR: FILE_NOT_FOUND: The requested file '{clean_name}' was not found in the music library.\n"
        client_socket.sendall(error_response.encode("utf-8"))
        print(f"[-] Handled FileNotFoundError for: '{clean_name}'")

    except PermissionError:
        error_response = f"ERR: PERMISSION_DENIED: Access denied when reading '{clean_name}'.\n"
        client_socket.sendall(error_response.encode("utf-8"))
        print(f"[-] Handled PermissionError for: '{clean_name}'")

    except Exception as e:
        # Catch-all to prevent server crash
        error_response = f"ERR: SERVER_ERROR: An unexpected error occurred: {str(e)}\n"
        client_socket.sendall(error_response.encode("utf-8"))
        print(f"[-] General error handling '{clean_name}': {e}")

def handle_client(client_socket: socket.socket, client_address):
    print(f"[+] Client connected: {client_address}")
    try:
        client_socket.sendall(b"MCP File Server (with Error Handling). Commands: LIST, GET <filename>, EXIT\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            line = data.decode("utf-8").strip()

            if line.upper() == "LIST":
                try:
                    files = [f for f in os.listdir(MUSIC_DIR) if os.path.isfile(os.path.join(MUSIC_DIR, f))]
                    res = f"OK: {len(files)} files: " + ", ".join(files) + "\n"
                    client_socket.sendall(res.encode("utf-8"))
                except Exception as e:
                    client_socket.sendall(f"ERR: Could not list directory: {e}\n".encode("utf-8"))

            elif line.upper().startswith("GET "):
                parts = line.split(" ", 1)
                safe_download_file(parts[1], client_socket)

            elif line.upper() == "EXIT":
                client_socket.sendall(b"BYE\n")
                break
            else:
                client_socket.sendall(b"ERR: Unrecognized command. Available: LIST, GET <file>, EXIT\n")
    except Exception as e:
        print(f"[-] Connection error: {e}")
    finally:
        client_socket.close()
        print(f"[-] Client disconnected: {client_address}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("=" * 65)
    print("     SESSION 18 - TASK 4: ERROR HANDLING FILE SERVER")
    print("=" * 65)
    print(f"[*] Server listening on {HOST}:{PORT}")
    print("[*] Protected with try-except blocks against FileNotFoundError")
    print("=" * 65)

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
