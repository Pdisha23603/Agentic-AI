"""
Session 18 - Task 5: File Deletion Command ('DELETE filename')
=============================================================
This script integrates and hardens the 'DELETE filename' command
generated via ChatGPT/Copilot with directory traversal protection,
FileNotFoundError handling, and confirmation messaging.
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

def handle_delete(filename: str, client_socket: socket.socket):
    clean_name = os.path.basename(filename.strip())
    if not clean_name:
        client_socket.sendall(b"ERR: Missing filename. Usage: DELETE <filename>\n")
        return

    filepath = os.path.join(MUSIC_DIR, clean_name)

    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{clean_name}' does not exist.")
        if not os.path.isfile(filepath):
            client_socket.sendall(f"ERR: '{clean_name}' is not a regular file.\n".encode("utf-8"))
            return

        os.remove(filepath)
        response = f"OK: DELETED: File '{clean_name}' has been successfully removed from server.\n"
        client_socket.sendall(response.encode("utf-8"))
        print(f"[+] Deleted file: '{clean_name}'")

    except FileNotFoundError:
        client_socket.sendall(f"ERR: FILE_NOT_FOUND: Cannot delete '{clean_name}' as it does not exist.\n".encode("utf-8"))
        print(f"[-] Delete failed - file not found: '{clean_name}'")
    except Exception as e:
        client_socket.sendall(f"ERR: DELETE_FAILED: {e}\n".encode("utf-8"))
        print(f"[-] Delete error: {e}")

def handle_client(client_socket: socket.socket, client_address):
    print(f"[+] Client connected: {client_address}")
    try:
        client_socket.sendall(b"MCP File Server (with DELETE support). Commands: LIST, DELETE <file>, EXIT\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            line = data.decode("utf-8").strip()

            if line.upper() == "LIST":
                files = os.listdir(MUSIC_DIR)
                client_socket.sendall(f"OK: Files: {', '.join(files)}\n".encode("utf-8"))
            elif line.upper().startswith("DELETE "):
                parts = line.split(" ", 1)
                handle_delete(parts[1], client_socket)
            elif line.upper() == "EXIT":
                client_socket.sendall(b"BYE\n")
                break
            else:
                client_socket.sendall(b"ERR: Unrecognized command.\n")
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[*] Task 5 Server listening on {HOST}:{PORT}")
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
