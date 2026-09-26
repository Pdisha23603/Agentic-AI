# SESSION 18 – Multi-Client Protocol (MCP) File Server

This repository contains the complete implementation, multi-client socket concurrency, file transfer protocol, error handling, and test suite for **Session 18: Multi-Client Protocol (MCP) Network File Server** built with Python sockets and threading.

---

## Overview of Tasks & Files Created

| Task | Topic | Files Created | Description |
| :--- | :--- | :--- | :--- |
| **Task 1** | Multi-Client TCP Server | [`task1_multi_client_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/task1_multi_client_server.py) | TCP socket server listening on port 6500, printing connection notifications and spawning worker threads. |
| **Task 2** | File Listing (`LIST`) | [`task2_file_listing_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/task2_file_listing_server.py) | Implements `LIST` command returning all tracks/files and byte sizes from the `music/` repository. |
| **Task 3** | File Download (`GET`) | [`task3_file_download_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/task3_file_download_server.py) | Implements `GET <filename>` command streaming binary file contents back to the client. |
| **Task 4** | Robust Error Handling | [`task4_error_handling_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/task4_error_handling_server.py) | Try-except blocks catching `FileNotFoundError` and blocking path traversal attacks without crashing. |
| **Task 5** | File Deletion (`DELETE`) | [`task5_delete_file_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/task5_delete_file_server.py)<br>[`task5_copilot_delete_file.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/task5_copilot_delete_file.md) | Implements hardened `DELETE <filename>` command with path sanitization and 404 verification. |
| **Integrated Server** | Master Server | [`mcp_file_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/mcp_file_server.py) | Complete production-ready multi-client file server combining all tasks on Port 6500. |
| **Interactive Client** | CLI Client | [`mcp_file_client.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/mcp_file_client.py) | Interactive command-line client for sending commands to the server. |
| **Test Suite** | Automated Tests | [`test_mcp_file_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/test_mcp_file_server.py) | Automated test suite verifying all 5 tasks and edge cases. |
| **Sample Data** | Music Library | [`music/`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2018/music/) | Sample MP3 and text payloads (`blinding_lights.mp3`, `espresso.mp3`, `sample.txt`). |

---

## Wire Protocol Specification

The server communicates via line-delimited ASCII commands and binary data streams over TCP port 6500:

| Command | Server Response Format | Description |
| :--- | :--- | :--- |
| **`LIST`** | `OK: <count> files available:\n• <file1>\n• <file2>` | Returns catalog of available files. |
| **`GET <file>`** | `OK: FILE <name> SIZE <bytes>\n<binary_payload>` | Downloads file contents. |
| **`GET <missing>`** | `ERR: FILE_NOT_FOUND: The requested file was not found.` | Handles missing files without crashing. |
| **`DELETE <file>`** | `OK: DELETED: File was successfully removed from server.` | Safely deletes regular file from `music/`. |
| **`EXIT`** | `BYE: Session ended. Goodbye!` | Disconnects the socket session. |

---

## How to Run & Verify All Tasks

### 1. Run the Integrated Multi-Client Server (Port 6500)
```bash
python mcp_file_server.py
```

### 2. Run the Automated Test Suite (in a separate terminal)
```bash
python test_mcp_file_server.py
```

### 3. Or Connect Interactively with the CLI Client
```bash
python mcp_file_client.py
```

### 4. Or Run Individual Task Scripts
```bash
# Task 1:
python task1_multi_client_server.py

# Task 2:
python task2_file_listing_server.py

# Task 3:
python task3_file_download_server.py

# Task 4:
python task4_error_handling_server.py

# Task 5:
python task5_delete_file_server.py
```
