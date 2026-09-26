"""
Session 18: Integrated Multi-Client Protocol (MCP) File Server
==============================================================
This is the complete, integrated TCP Socket File Server combining
all Session 18 tasks on Port 6500:

Features & Supported Commands:
1. Multi-Client Concurrency: Uses threading to serve concurrent clients (Task 1)
2. 'LIST': Responds with all files in 'music' directory (Task 2)
3. 'GET <filename>': Sends file contents to the client (Task 3)
4. Error Handling: Catches FileNotFoundError and path traversal (Task 4)
5. 'DELETE <filename>': Safely removes a file from the server (Task 5)
6. 'HELP': Shows list of available commands
7. 'EXIT': Gracefully closes the client session
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

def ensure_music_dir():
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR, exist_ok=True)

# ==============================================================================
# Command Handler 1: LIST
# ==============================================================================
def handle_list() -> str:
    ensure_music_dir()
    files = [f for f in os.listdir(MUSIC_DIR) if os.path.isfile(os.path.join(MUSIC_DIR, f))]
    if not files:
        return "OK: The music directory is currently empty.\n"

    lines = [f"OK: {len(files)} file(s) available in music repository:"]
    for f in sorted(files):
        size = os.path.getsize(os.path.join(MUSIC_DIR, f))
        lines.append(f"  • {f} ({size} bytes)")
    return "\n".join(lines) + "\n"

# ==============================================================================
# Command Handler 2: GET <filename>
# ==============================================================================
def handle_get(filename_arg: str, client_socket: socket.socket):
    clean_name = os.path.basename(filename_arg.strip())
    if not clean_name:
        client_socket.sendall(b"ERR: Missing filename. Usage: GET <filename>\n")
        return

    # Check for path traversal attempts
    if ".." in filename_arg or "/" in filename_arg or "\\" in filename_arg:
        client_socket.sendall(f"ERR: SECURITY_VIOLATION: Path traversal is prohibited.\n".encode("utf-8"))
        print(f"[-] Blocked traversal attempt: {filename_arg}")
        return

    filepath = os.path.join(MUSIC_DIR, clean_name)

    try:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File '{clean_name}' does not exist.")

        file_size = os.path.getsize(filepath)
        header = f"OK: FILE {clean_name} SIZE {file_size}\n"
        client_socket.sendall(header.encode("utf-8"))

        # Stream binary file contents
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                client_socket.sendall(chunk)

        print(f"[+] Successfully transferred '{clean_name}' ({file_size} bytes)")

    except FileNotFoundError:
        client_socket.sendall(f"ERR: FILE_NOT_FOUND: The requested file '{clean_name}' was not found.\n".encode("utf-8"))
        print(f"[-] Handled FileNotFoundError for '{clean_name}'")
    except PermissionError:
        client_socket.sendall(f"ERR: PERMISSION_DENIED: Access denied for '{clean_name}'.\n".encode("utf-8"))
    except Exception as e:
        client_socket.sendall(f"ERR: DOWNLOAD_ERROR: {str(e)}\n".encode("utf-8"))

# ==============================================================================
# Command Handler 3: DELETE <filename>
# ==============================================================================
def handle_delete(filename_arg: str, client_socket: socket.socket):
    clean_name = os.path.basename(filename_arg.strip())
    if not clean_name:
        client_socket.sendall(b"ERR: Missing filename. Usage: DELETE <filename>\n")
        return

    if ".." in filename_arg or "/" in filename_arg or "\\" in filename_arg:
        client_socket.sendall(f"ERR: SECURITY_VIOLATION: Path traversal is prohibited.\n".encode("utf-8"))
        return

    filepath = os.path.join(MUSIC_DIR, clean_name)

    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{clean_name}' does not exist.")
        if not os.path.isfile(filepath):
            client_socket.sendall(f"ERR: '{clean_name}' is not a regular file.\n".encode("utf-8"))
            return

        os.remove(filepath)
        response = f"OK: DELETED: File '{clean_name}' was successfully removed from server.\n"
        client_socket.sendall(response.encode("utf-8"))
        print(f"[+] File deleted: '{clean_name}'")

    except FileNotFoundError:
        client_socket.sendall(f"ERR: FILE_NOT_FOUND: Cannot delete '{clean_name}' as it does not exist.\n".encode("utf-8"))
        print(f"[-] Delete failed - not found: '{clean_name}'")
    except PermissionError:
        client_socket.sendall(f"ERR: PERMISSION_DENIED: Permission denied when deleting '{clean_name}'.\n".encode("utf-8"))
    except Exception as e:
        client_socket.sendall(f"ERR: DELETE_ERROR: {str(e)}\n".encode("utf-8"))

# ==============================================================================
# Multi-Client Connection Thread Handler
# ==============================================================================
def handle_client(client_socket: socket.socket, client_address):
    print(f"\n[+] NEW CLIENT CONNECTED from {client_address[0]}:{client_address[1]}")
    try:
        banner = (
            "=====================================================\n"
            "   Welcome to the MCP Music & File Server (v1.0)     \n"
            "   Available Commands:                               \n"
            "   • LIST              - View all files in repository\n"
            "   • GET <filename>    - Download file contents      \n"
            "   • DELETE <filename> - Delete file from repository \n"
            "   • EXIT              - Disconnect session          \n"
            "=====================================================\n"
        )
        client_socket.sendall(banner.encode("utf-8"))

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            command_str = data.decode("utf-8").strip()
            if not command_str:
                continue

            print(f"[{client_address[0]}:{client_address[1]}] Executing: '{command_str}'")

            if command_str.upper() == "LIST":
                response = handle_list()
                client_socket.sendall(response.encode("utf-8"))

            elif command_str.upper().startswith("GET "):
                parts = command_str.split(" ", 1)
                handle_get(parts[1], client_socket)

            elif command_str.upper().startswith("DELETE "):
                parts = command_str.split(" ", 1)
                handle_delete(parts[1], client_socket)

            elif command_str.upper() == "HELP":
                client_socket.sendall(b"Commands: LIST, GET <filename>, DELETE <filename>, EXIT\n")

            elif command_str.upper() == "EXIT":
                client_socket.sendall(b"BYE: Session ended. Goodbye!\n")
                break
            else:
                client_socket.sendall(f"ERR: Unknown command '{command_str}'. Send 'HELP' or 'LIST'.\n".encode("utf-8"))

    except ConnectionResetError:
        print(f"[-] Client {client_address} abruptly disconnected.")
    except Exception as e:
        print(f"[-] Exception handling client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[-] Client disconnected: {client_address[0]}:{client_address[1]}")

def start_server():
    ensure_music_dir()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    print("=" * 65)
    print("     SESSION 18: INTEGRATED MULTI-CLIENT FILE SERVER")
    print("=" * 65)
    print(f"[*] Server listening on: {HOST}:{PORT}")
    print(f"[*] Music Directory:     {MUSIC_DIR}")
    print("[*] Concurrency:         Multi-threaded socket pool")
    print("[*] Supported Commands:  LIST, GET <file>, DELETE <file>, EXIT")
    print("[*] Press Ctrl+C to terminate.")
    print("=" * 65)

    try:
        while True:
            client_sock, client_addr = server_socket.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down MCP File Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
