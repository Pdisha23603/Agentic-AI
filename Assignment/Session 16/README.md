# SESSION 16 – Business MCP Server

This repository contains the complete implementation, error handling, notification system, and test suite for **Session 16: Business MCP (Multi-Channel Processing) Server** built with Python and Flask.

---

## Overview of Tasks & Files Created

| Task | Topic | Files Created | Description |
| :--- | :--- | :--- | :--- |
| **Task 1** | Basic Flask Server | [`task1_basic_mcp_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/task1_basic_mcp_server.py) | Flask MCP server running on port 5000 responding with `'MCP Server Running'` at `GET /`. |
| **Task 2** | Order Status Endpoint | [`task2_order_status_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/task2_order_status_server.py) | `POST /order-status` endpoint accepting JSON `{ "orderId": "..." }` and returning simulated status. |
| **Task 3** | HTTP 400 Error Handling | [`task3_error_handling_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/task3_error_handling_server.py) | Input validation: returns structured JSON error with status 400 if `orderId` is missing or empty. |
| **Task 4** | Flipkart Notification System | [`task4_notification_system.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/task4_notification_system.py)<br>[`notifications.log`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/notifications.log) | `POST /notify` endpoint accepting `userId` and `message`, logging timestamped events to `notifications.log`. |
| **Task 5** | User Profile Integration | [`task5_user_profile_endpoint.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/task5_user_profile_endpoint.py)<br>[`task5_copilot_generation.md`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/task5_copilot_generation.md) | `GET/POST /user-profile` returning mock user profile (name, email, phone, city, membership tier). |
| **Integrated Server** | Master Server | [`business_mcp_server.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/business_mcp_server.py) | Unified server hosting all 5 tasks together on port 5000. |
| **Test Suite** | Automated Tests | [`test_business_mcp.py`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/test_business_mcp.py) | Automated test suite verifying every endpoint and edge case. |

---

## Detailed Task Documentation & API Specifications

### Task 1: Basic Flask MCP Server
- **Endpoint**: `GET /`
- **Port**: `5000`
- **Response**: `MCP Server Running` (Plain text / HTTP 200)

---

### Task 2 & 3: Order Status with Error Handling
- **Endpoint**: `POST /order-status`
- **Headers**: `Content-Type: application/json`
- **Valid Request**:
  ```json
  {
    "orderId": "OD9847120394"
  }
  ```
- **Valid Response (HTTP 200)**:
  ```json
  {
    "orderId": "OD9847120394",
    "status": "In Transit",
    "carrier": "Ekart Logistics",
    "estimatedDelivery": "Within 2 business days"
  }
  ```
- **Missing `orderId` Request**:
  ```json
  {
    "incorrectField": 123
  }
  ```
- **Error Response (HTTP 400 Bad Request)**:
  ```json
  {
    "error": "Bad Request",
    "message": "Missing required field: 'orderId'",
    "requiredFields": ["orderId"],
    "statusCode": 400
  }
  ```

---

### Task 4: Flipkart-Style Notification System
- **Endpoint**: `POST /notify`
- **Request Body**:
  ```json
  {
    "userId": "USR_101",
    "message": "Your Flipkart package has been out for delivery by Ekart Logistics!"
  }
  ```
- **Log Entry in [`notifications.log`](file:///d:/tops%20data/Agentic%20AI/Assignment/Session%2016/notifications.log)**:
  ```text
  [2026-09-26 14:23:47] [USER: USR_101] NOTIFICATION: Your Flipkart package has been out for delivery by Ekart Logistics!
  ```

---

### Task 5: User Profile Endpoint
- **Endpoints**:
  - `GET /user-profile?userId=USR_101`
  - `POST /user-profile` with `{ "userId": "USR_101" }`
- **Response (HTTP 200)**:
  ```json
  {
    "status": "success",
    "userId": "USR_101",
    "profile": {
      "name": "Nishant Patel",
      "email": "nishant.patel@example.com",
      "phone": "+91-9876543210",
      "city": "Ahmedabad",
      "memberTier": "Flipkart Plus Member",
      "joinedDate": "2021-04-15"
    }
  }
  ```

---

## How to Run & Verify All Tasks

### Step 1: Start the Business MCP Server
```bash
python business_mcp_server.py
```

### Step 2: Run the Automated Test Suite (in another terminal)
```bash
python test_business_mcp.py
```

### Step 3: Or Test Individual Task Scripts
```bash
# Task 1:
python task1_basic_mcp_server.py

# Task 2:
python task2_order_status_server.py

# Task 3:
python task3_error_handling_server.py

# Task 4:
python task4_notification_system.py

# Task 5:
python task5_user_profile_endpoint.py
```
