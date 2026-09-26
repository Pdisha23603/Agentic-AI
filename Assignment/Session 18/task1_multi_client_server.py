"""
Session 18 - Task 1: Multi-Client Protocol (MCP) Socket Server
=============================================================
This script sets up a multi-client TCP server using Python's 'socket'
and 'threading' modules. It listens on port 6500 and prints a message
whenever a client connects, spawning a worker thread per client.
"""

import sys
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

def handle_client(client_socket: socket.socket, client_address):
    """Handles an individual client connection in a dedicated thread."""
    print(f"[+] Client Handler Started for {client_address}")
    try:
        client_socket.sendall(b"MCP Server v1.0 Ready. Connection Established.\n")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            msg = data.decode("utf-8").strip()
            print(f"[{client_address}] Received: {msg}")
            if msg.upper() == "EXIT":
                client_socket.sendall(b"Goodbye!\n")
                break
            client_socket.sendall(f"ACK: Received '{msg}'\n".encode("utf-8"))
    except ConnectionResetError:
        print(f"[-] Client {client_address} abruptly disconnected.")
    finally:
        client_socket.close()
        print(f"[-] Client disconnected: {client_address}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow instant port reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print("=" * 65)
    print("     SESSION 18 - TASK 1: MULTI-CLIENT PROTOCOL SERVER")
    print("=" * 65)
    print(f"[*] MCP Server listening on {HOST}:{PORT}")
    print("[*] Ready for incoming client socket connections...")
    print("[*] Press Ctrl+C to terminate server.")
    print("=" * 65)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            # Requirement: Print message whenever a client connects
            print(f"\n[+] NEW CLIENT CONNECTED from {client_address[0]}:{client_address[1]}")
            
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            client_thread.start()
            print(f"[*] Active Client Threads: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[*] Shutting down MCP Server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
