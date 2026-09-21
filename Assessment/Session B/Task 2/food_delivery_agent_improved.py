"""
Food Delivery Agent - IMPROVED VERSION
Tool-Calling Agent with Advanced Routing & State Management

Enhanced Features:
- Smarter keyword-based routing with priority matching
- Dual-pass keyword detection for better accuracy
- Robust error handling and fallbacks
- Session history tracking with detailed statistics
"""

import sys
import io

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Callable
import re


# ============================================================================
# TOOL FUNCTIONS - External Tool Definitions
# ============================================================================

def check_restaurant_status(name: str) -> str:
    """Check the operational status of a restaurant."""
    restaurants = {
        "pizza palace": {"status": "open", "hours": "10 AM - 11 PM", "rating": 4.8},
        "burger barn": {"status": "open", "hours": "11 AM - 10 PM", "rating": 4.5},
        "sushi spot": {"status": "closed", "hours": "4 PM - 10 PM", "opens_at": "4 PM"},
        "taco town": {"status": "open", "hours": "12 PM - 11 PM", "rating": 4.7},
        "curry house": {"status": "open", "hours": "5 PM - 11 PM", "rating": 4.9},
    }
    
    name_lower = name.lower().strip()
    if name_lower in restaurants:
        info = restaurants[name_lower]
        status = info["status"].upper()
        hours = info["hours"]
        if info["status"] == "open":
            rating = info.get("rating", "N/A")
            return f"✓ {name} is {status}\n  Hours: {hours}\n  Rating: {rating}⭐"
        else:
            opens = info.get("opens_at", "later")
            return f"✗ {name} is {status}\n  Hours: {hours}\n  Opens: {opens}"
    else:
        return f"✗ Restaurant '{name}' not found in our system.\n  Available: Pizza Palace, Burger Barn, Sushi Spot, Taco Town, Curry House"


def get_estimated_delivery_time(order_id: str) -> str:
    """Get estimated delivery time for an order."""
    orders = {
        "ORD001": {"status": "preparing", "minutes": 18, "distance": 2.5},
        "ORD002": {"status": "out_for_delivery", "minutes": 7, "distance": 1.2},
        "ORD003": {"status": "preparing", "minutes": 25, "distance": 4.0},
        "ORD004": {"status": "out_for_delivery", "minutes": 12, "distance": 3.1},
        "ORD005": {"status": "delivered", "delivered_at": "2:45 PM"},
    }
    
    order_id_upper = order_id.upper().strip()
    if order_id_upper in orders:
        info = orders[order_id_upper]
        if info["status"] == "delivered":
            return f"✓ Order {order_id_upper} was delivered at {info['delivered_at']}"
        else:
            status = info["status"].replace("_", " ").title()
            minutes = info["minutes"]
            distance = info["distance"]
            arrival_time = (datetime.now() + timedelta(minutes=minutes)).strftime("%I:%M %p")
            return f"📍 Order {order_id_upper}\n  Status: {status}\n  ETA: {arrival_time} (~{minutes} min)\n  Distance: {distance} km"
    else:
        return f"✗ Order {order_id_upper} not found. Check your order ID and try again."


def apply_discount(order_id: str, reason: str) -> str:
    """Apply a discount to an order."""
    discount_rules = {
        "late delivery": {"percentage": 15, "message": "Late delivery compensation"},
        "quality issue": {"percentage": 20, "message": "Quality issue refund"},
        "missing item": {"percentage": 25, "message": "Missing item compensation"},
        "wrong order": {"percentage": 30, "message": "Wrong order replacement"},
        "promotional": {"percentage": 10, "message": "Promotional discount"},
    }
    
    order_id_upper = order_id.upper().strip()
    reason_lower = reason.lower().strip()
    
    valid_orders = ["ORD001", "ORD002", "ORD003", "ORD004", "ORD005"]
    if order_id_upper not in valid_orders:
        return f"✗ Cannot apply discount: Order {order_id_upper} not found"
    
    if reason_lower in discount_rules:
        discount_info = discount_rules[reason_lower]
        percentage = discount_info["percentage"]
        message = discount_info["message"]
        
        simulated_amount = 50.00
        discount_amount = simulated_amount * (percentage / 100)
        new_total = simulated_amount - discount_amount
        
        return f"✓ Discount Applied to Order {order_id_upper}\n  Reason: {message}\n  Discount: {percentage}% (${discount_amount:.2f})\n  Original: ${simulated_amount:.2f} → New Total: ${new_total:.2f}"
    else:
        valid_reasons = ", ".join(discount_rules.keys())
        return f"✗ Invalid discount reason '{reason}'. Valid reasons: {valid_reasons}"


def file_complaint(order_id: str, issue: str) -> str:
    """File a complaint for an order."""
    valid_orders = ["ORD001", "ORD002", "ORD003", "ORD004", "ORD005"]
    order_id_upper = order_id.upper().strip()
    
    if order_id_upper not in valid_orders:
        return f"✗ Cannot file complaint: Order {order_id_upper} not found"
    
    if not issue or len(issue.strip()) < 5:
        return f"✗ Issue description must be at least 5 characters long"
    
    ticket_id = f"TKT{order_id_upper[3:]}_{datetime.now().strftime('%H%M%S')}"
    
    return f"✓ Complaint Filed Successfully\n  Ticket ID: {ticket_id}\n  Order: {order_id_upper}\n  Issue: {issue}\n  Status: Under Investigation\n  Expected Resolution: 24-48 hours"


# ============================================================================
# MCP-STYLE SCHEMAS - Tool Definitions
# ============================================================================

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "check_restaurant_status",
        "description": "Check if a restaurant is currently open and get its operating hours and rating",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the restaurant to check (e.g., 'Pizza Palace', 'Sushi Spot')"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_estimated_delivery_time",
        "description": "Get the estimated delivery time and current status for an order",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID (e.g., 'ORD001', 'ORD002')"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "apply_discount",
        "description": "Apply a discount to an order for reasons like late delivery, quality issues, or missing items",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to apply discount to"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for discount: 'late delivery', 'quality issue', 'missing item', 'wrong order', or 'promotional'"
                }
            },
            "required": ["order_id", "reason"]
        }
    },
    {
        "name": "file_complaint",
        "description": "File a formal complaint about an order issue and receive a ticket ID for tracking",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID for the complaint"
                },
                "issue": {
                    "type": "string",
                    "description": "Detailed description of the issue experienced"
                }
            },
            "required": ["order_id", "issue"]
        }
    }
]


# ============================================================================
# TOOL REGISTRY
# ============================================================================

TOOL_REGISTRY: Dict[str, Callable] = {
    "check_restaurant_status": check_restaurant_status,
    "get_estimated_delivery_time": get_estimated_delivery_time,
    "apply_discount": apply_discount,
    "file_complaint": file_complaint,
}


# ============================================================================
# FOOD DELIVERY AGENT - Main Agent Class
# ============================================================================

class FoodDeliveryAgent:
    """
    Advanced tool-calling agent with intelligent routing.
    
    Features:
    - Two-pass keyword matching (exact first, then fuzzy)
    - Priority-based tool selection
    - Comprehensive parameter extraction
    - Session history with statistics
    """
    
    # PRIORITY ROUTING - Higher priority keywords matched first
    PRIORITY_ROUTES = {
        "file_complaint": {
            "priority_keywords": ["complaint", "issue", "problem", "ticket", "report"],
            "secondary_keywords": ["wrong", "broken", "damaged", "bad", "not good"],
        },
        "apply_discount": {
            "priority_keywords": ["discount", "refund", "compensation", "credit", "reduce"],
            "secondary_keywords": ["late", "quality", "missing", "wrong"],
        },
        "check_restaurant_status": {
            "priority_keywords": ["restaurant", "open", "closed", "status", "hours", "operating"],
            "secondary_keywords": ["available", "open"],
        },
        "get_estimated_delivery_time": {
            "priority_keywords": ["when", "arrive", "time", "eta", "where", "track", "status"],
            "secondary_keywords": ["delivery"],
        },
    }
    
    def __init__(self, agent_name: str = "FoodDeliveryBot"):
        self.agent_name = agent_name
        self.session_log: List[Tuple[str, str, str]] = []
        self.query_count = 0
        self.stats = {
            "total_queries": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tools_used": {}
        }
        
    def think(self, query: str) -> str:
        """Process a customer query and route to appropriate tool."""
        self.query_count += 1
        self.stats["total_queries"] += 1
        query_lower = query.lower().strip()
        
        # Two-pass routing for accuracy
        matched_tool = self._find_best_tool(query_lower)
        
        if matched_tool is None:
            result = "❌ I couldn't understand your request. Try:\n  • 'Is [restaurant] open?'\n  • 'Where's my order [ORD###]?'\n  • 'I want a discount for [reason]'\n  • 'I have a complaint about order [ORD###]'"
            self.session_log.append((query, "NO_MATCH", result))
            self.stats["failed_calls"] += 1
            return result
        
        try:
            parameters = self._extract_parameters(query, matched_tool)
            tool_function = TOOL_REGISTRY[matched_tool]
            result = tool_function(**parameters)
            
            self.session_log.append((query, matched_tool, result))
            self.stats["successful_calls"] += 1
            self.stats["tools_used"][matched_tool] = self.stats["tools_used"].get(matched_tool, 0) + 1
            
            return result
            
        except Exception as e:
            error_msg = f"⚠️ Error executing {matched_tool}: {str(e)}"
            self.session_log.append((query, matched_tool, error_msg))
            self.stats["failed_calls"] += 1
            return error_msg
    
    def _find_best_tool(self, query_lower: str) -> str:
        """
        Two-pass tool matching algorithm.
        Pass 1: Check priority keywords
        Pass 2: Check secondary keywords
        """
        # Pass 1: Priority keywords
        for tool_name, keywords in self.PRIORITY_ROUTES.items():
            priority_matches = sum(
                1 for kw in keywords["priority_keywords"] if kw in query_lower
            )
            if priority_matches > 0:
                return tool_name
        
        # Pass 2: Secondary keywords with scoring
        best_tool = None
        best_score = 0
        
        for tool_name, keywords in self.PRIORITY_ROUTES.items():
            score = sum(1 for kw in keywords["secondary_keywords"] if kw in query_lower)
            if score > best_score:
                best_score = score
                best_tool = tool_name
        
        return best_tool
    
    def _extract_parameters(self, query: str, tool_name: str) -> Dict[str, str]:
        """Extract parameters from query using regex and heuristics."""
        parameters = {}
        query_lower = query.lower()
        
        if tool_name == "check_restaurant_status":
            words = query.split()
            restaurant_keywords = ["pizza", "burger", "sushi", "taco", "curry"]
            
            for i, word in enumerate(words):
                if word.lower() in restaurant_keywords:
                    if i + 1 < len(words):
                        name = f"{words[i]} {words[i+1]}".strip()
                    else:
                        name = words[i]
                    parameters["name"] = name
                    break
            
            if "name" not in parameters:
                parameters["name"] = query
        
        elif tool_name == "get_estimated_delivery_time":
            order_match = re.search(r'ORD\d+', query_lower.upper())
            if order_match:
                parameters["order_id"] = order_match.group(0)
            else:
                numbers = re.findall(r'\d+', query)
                parameters["order_id"] = f"ORD{numbers[0].zfill(3)}" if numbers else "ORD001"
        
        elif tool_name == "apply_discount":
            order_match = re.search(r'ORD\d+', query_lower.upper())
            parameters["order_id"] = order_match.group(0) if order_match else "ORD001"
            
            reasons = ["late delivery", "quality issue", "missing item", "wrong order", "promotional"]
            for reason in reasons:
                if reason in query_lower:
                    parameters["reason"] = reason
                    break
            
            if "reason" not in parameters:
                if "late" in query_lower:
                    parameters["reason"] = "late delivery"
                elif "quality" in query_lower or "bad" in query_lower:
                    parameters["reason"] = "quality issue"
                elif "missing" in query_lower:
                    parameters["reason"] = "missing item"
                else:
                    parameters["reason"] = "promotional"
        
        elif tool_name == "file_complaint":
            order_match = re.search(r'ORD\d+', query_lower.upper())
            parameters["order_id"] = order_match.group(0) if order_match else "ORD001"
            
            issue = query
            for keyword in ["complaint", "issue", "problem", "report"]:
                if keyword in query_lower:
                    idx = query_lower.index(keyword)
                    issue = query[idx:].replace(keyword, "").strip()
                    break
            
            parameters["issue"] = issue if issue else "Unspecified issue"
        
        return parameters
    
    def get_session_log(self) -> List[Tuple[str, str, str]]:
        """Get complete session history."""
        return self.session_log
    
    def print_session_summary(self) -> None:
        """Print formatted session summary."""
        print("\n" + "=" * 80)
        print("SESSION SUMMARY")
        print("=" * 80)
        print(f"Agent: {self.agent_name}")
        print(f"Total Queries: {self.stats['total_queries']}")
        print(f"Successful: {self.stats['successful_calls']} | Failed: {self.stats['failed_calls']}")
        print(f"Success Rate: {(self.stats['successful_calls'] / max(1, self.stats['total_queries']) * 100):.1f}%")
        print(f"\nTools Used:")
        for tool, count in self.stats['tools_used'].items():
            print(f"  • {tool}: {count} call(s)")
        
        print("\n" + "-" * 80)
        for i, (query, tool, result) in enumerate(self.session_log, 1):
            print(f"\n[Query #{i}]")
            print(f"Customer: {query}")
            print(f"Tool Called: {tool}")
            print(f"Response:\n{result}")
            print("-" * 80)


# ============================================================================
# MAIN - Test the Improved Agent
# ============================================================================

def main():
    """Main function to demonstrate the improved agent."""
    
    print("\n" + "=" * 80)
    print("FOOD DELIVERY AGENT - IMPROVED VERSION (WITH BETTER ROUTING)")
    print("=" * 80)
    
    # Print MCP schemas
    print("\n📋 TOOL SCHEMAS (MCP Format)")
    print("=" * 80)
    for schema in TOOL_SCHEMAS:
        print(f"\n{json.dumps(schema, indent=2)}")
    print("\n" + "=" * 80)
    
    # Create agent
    print("\n🤖 Initializing FoodDeliveryAgent (Improved)...")
    agent = FoodDeliveryAgent(agent_name="FoodDeliveryBot v2.0 (Advanced Routing)")
    print(f"✓ Agent '{agent.agent_name}' initialized successfully\n")
    
    # Test queries - IMPROVED to cover all 4 tools properly
    test_queries = [
        # Tool 1: check_restaurant_status
        "Is Pizza Palace open right now?",
        
        # Tool 2: get_estimated_delivery_time
        "When will my order ORD002 arrive?",
        
        # Tool 3: apply_discount
        "I'd like a discount for order ORD001 because it arrived late",
        
        # Tool 4: file_complaint
        "I need to file a complaint about order ORD003 - the food arrived cold",
        
        # Bonus: Mixed query
        "Check if Sushi Spot is open and tell me about my order ORD004",
    ]
    
    print("🚀 PROCESSING CUSTOMER QUERIES")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query #{i}]")
        print(f"👤 Customer: {query}")
        print(f"🔄 Agent Processing...")
        
        result = agent.think(query)
        
        print(f"📤 Response:\n{result}")
        print("-" * 80)
    
    # Print session summary
    agent.print_session_summary()
    
    print("\n" + "=" * 80)
    print("✓ IMPROVED AGENT DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
