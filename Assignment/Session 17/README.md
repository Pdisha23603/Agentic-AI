# SESSION 17 – Database MCP Server

This repository contains the complete implementation, database schemas, command handlers, and test suite for **Session 17: Database Multi-Channel Processing (MCP) Server** built with Python and SQLite.

---

## Overview of Tasks & Files Created

| Task | Topic | Files Created | Description |
| :--- | :--- | :--- | :--- |
| **Task 1** | SQLite MCP Server & User Management | [`task1_sqlite_mcp_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task1_sqlite_mcp_server.py) | SQLite MCP server handling basic user commands (`POST /user` to add, `GET /user/<user_id>` to retrieve). |
| **Task 2** | Parameterized `store_order` | [`task2_store_order.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task2_store_order.py) | Function inserting orders into `orders` table using parameterized queries (`?`) to prevent SQL injection. |
| **Task 3** | `GET_USER_ORDERS` Handler | [`task3_get_user_orders.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task3_get_user_orders.py) | Handler accepting `user_id` and returning all associated `order_id`s and `amount`s from the database. |
| **Task 4** | Zomato-Style Recent History (`GET_LAST_N_ORDERS`) | [`task4_zomato_order_history.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task4_zomato_order_history.py) | Returns the N most recent orders for a user, sorted descending by the `order_time` timestamp column. |
| **Task 5** | Refined `delete_order` | [`task5_delete_order.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task5_delete_order.py)<br>[`task5_copilot_delete_order.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task5_copilot_delete_order.md) | Deletes orders with `cursor.rowcount` verification and parameterized queries (includes Copilot evolution documentation). |
| **Integrated Server** | Master Server (Port 5001) | [`database_mcp_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/database_mcp_server.py) | Unified server hosting all 5 tasks and universal command dispatcher on port 5001. |
| **Test Suite** | Automated Tests | [`test_database_mcp.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/test_database_mcp.py) | Automated test suite verifying all tasks end-to-end. |

---

## Database Schema (`mcp_database.db`)

### `users` Table
```sql
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `orders` Table (with Timestamp Constraint)
```sql
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount REAL NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Detailed Task Documentation & API Specifications

### Task 1: SQLite Server & User Data
- **Endpoints**:
  - `POST /user` with body `{"user_id": "USR_01", "name": "Nishant", "email": "n@ex.com", "phone": "+91-9876543210"}`
  - `GET /user/<user_id>` -> returns user record.

### Task 2: Parameterized `store_order`
- **Function**: `store_order(order_id, user_id, amount, order_time=None)`
- **SQL Protection**:
  ```python
  cursor.execute(
      "INSERT INTO orders (order_id, user_id, amount, order_time) VALUES (?, ?, ?, ?)",
      (order_id, user_id, amount, order_time)
  )
  ```
- Protects against malicious SQL injection strings (e.g. `' OR '1'='1`).

### Task 3: `GET_USER_ORDERS` Command Handler
- **Command**: `GET_USER_ORDERS`
- **Payload**: `{"user_id": "USR_101"}`
- **Response**:
  ```json
  {
    "status": "success",
    "command": "GET_USER_ORDERS",
    "user_id": "USR_101",
    "count": 4,
    "orders": [
      {"order_id": "ORD_7001", "amount": 450.0},
      {"order_id": "ORD_7002", "amount": 1250.5}
    ]
  }
  ```

### Task 4: Zomato-Style `GET_LAST_N_ORDERS`
- **Command**: `GET_LAST_N_ORDERS`
- **Constraint**: Orders table includes `order_time TIMESTAMP`, and queries use `ORDER BY order_time DESC LIMIT ?`.
- **Payload**: `{"user_id": "USR_ZOMATO", "n": 3}`
- **Response**: Returns the 3 latest orders sorted with latest timestamp first.

### Task 5: AI Code Generation & Refinement (`delete_order`)
- **Documentation**: See [`task5_copilot_delete_order.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2017/task5_copilot_delete_order.md).
- **Function**: `delete_order(order_id)`
- **Key Enhancements**:
  - Checks `cursor.rowcount` to distinguish between successful deletion (200) and non-existent IDs (404).
  - Parameterized execution.

---

## How to Run & Verify All Tasks

### 1. Run the Integrated Master Server (Port 5001)
```bash
python database_mcp_server.py
```

### 2. Run the Automated Test Suite (in a separate terminal)
```bash
python test_database_mcp.py
```

### 3. Or Run Individual Task Scripts Directly
```bash
# Task 1:
python task1_sqlite_mcp_server.py

# Task 2:
python task2_store_order.py

# Task 3:
python task3_get_user_orders.py

# Task 4:
python task4_zomato_order_history.py

# Task 5:
python task5_delete_order.py
```
