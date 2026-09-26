"""
Session 18: Automated Test Suite for Multi-Client File Server
=============================================================
This script tests all 5 tasks against the MCP File Server on Port 6500:
1. Task 1: Connect to server and verify connection banner
2. Task 2: Send 'LIST' command and parse file listing
3. Task 3: Send 'GET sample.txt' and download file contents
4. Task 4: Send 'GET unknown.mp3' and verify custom FileNotFoundError handling
5. Task 5: Send 'DELETE <filename>' and verify file deletion and 404 handling
"""

import sys
import os
import socket
import time

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

def send_command(sock: socket.socket, cmd: str) -> str:
    """Helper to send a command and receive the server response."""
    sock.sendall((cmd + "\n").encode("utf-8"))
    time.sleep(0.1)
    response = sock.recv(4096).decode("utf-8")
    return response

def run_tests():
    print("=" * 70)
    print("     SESSION 18: MULTI-CLIENT FILE SERVER AUTOMATED TEST SUITE")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # Test 1: Task 1 - Socket Connection & Welcome Banner
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Task 1 - Connecting to MCP Server on Port 6500 ---")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        banner = s.recv(2048).decode("utf-8")
        print("[*] Connected! Server Welcome Banner:")
        print(banner.strip())
        assert "Welcome to the MCP Music & File Server" in banner
        print("[PASS] Task 1 Connection verified successfully!")
    except Exception as e:
        print(f"[-] FAILED Test 1: {e}")
        print("    Ensure 'mcp_file_server.py' is running on port 6500.")
        return

    # --------------------------------------------------------------------------
    # Test 2: Task 2 - File Listing ('LIST')
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 2: Task 2 - Listing Files with 'LIST' Command ---")
    list_res = send_command(s, "LIST")
    print("[*] Sent: 'LIST'")
    print("[*] Server Response:\n" + list_res.strip())
    assert "OK:" in list_res
    assert "blinding_lights.mp3" in list_res
    assert "espresso.mp3" in list_res
    print("[PASS] Task 2 File listing verified successfully!")

    # --------------------------------------------------------------------------
    # Test 3: Task 3 - File Download ('GET sample.txt')
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 3: Task 3 - Downloading File with 'GET sample.txt' ---")
    get_res = send_command(s, "GET sample.txt")
    print("[*] Sent: 'GET sample.txt'")
    print("[*] Server Response Header & Data:\n" + get_res.strip())
    assert "OK: FILE sample.txt" in get_res
    assert "Hello from the MCP Music Server!" in get_res
    print("[PASS] Task 3 File download verified successfully!")

    # --------------------------------------------------------------------------
    # Test 4: Task 4 - Error Handling for Missing File ('GET non_existent.mp3')
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 4: Task 4 - Error Handling for Non-Existent File ---")
    err_res = send_command(s, "GET non_existent_song_404.mp3")
    print("[*] Sent: 'GET non_existent_song_404.mp3'")
    print("[*] Server Response:\n" + err_res.strip())
    assert "ERR: FILE_NOT_FOUND" in err_res
    print("[PASS] Task 4 Error handling (FileNotFoundError) verified successfully!")

    # --------------------------------------------------------------------------
    # Test 5: Task 5 - File Deletion ('DELETE') & Verification
    # --------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("--- TEST 5: Task 5 - Deleting File with 'DELETE' Command ---")
    # 1. Create a dummy file to delete
    dummy_path = os.path.join(MUSIC_DIR, "temp_track_to_delete.mp3")
    with open(dummy_path, "w", encoding="utf-8") as f:
        f.write("Temporary track payload.")
    print(f"[*] Prepared temporary file on server: {os.path.basename(dummy_path)}")

    # 2. Issue DELETE command
    del_res = send_command(s, "DELETE temp_track_to_delete.mp3")
    print("[*] Sent: 'DELETE temp_track_to_delete.mp3'")
    print("[*] Server Response:\n" + del_res.strip())
    assert "OK: DELETED" in del_res
    assert not os.path.exists(dummy_path)

    # 3. Attempt deleting again (Expect FILE_NOT_FOUND)
    del_again = send_command(s, "DELETE temp_track_to_delete.mp3")
    print("\n[*] Deleting again -> Response:\n" + del_again.strip())
    assert "ERR: FILE_NOT_FOUND" in del_again
    print("[PASS] Task 5 File deletion & error handling verified successfully!")

    # Clean close
    s.sendall(b"EXIT\n")
    s.close()

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL 5 TASKS TESTED AND VERIFIED FLAWLESSLY ON PORT 6500!")

if __name__ == "__main__":
    run_tests()
