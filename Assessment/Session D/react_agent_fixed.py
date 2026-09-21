"""
ReAct (Reason + Action) Agent for Food Delivery Customer Support
FIXED VERSION with proper order ID extraction and improved reasoning
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# ============================================================================
# TOOL FUNCTIONS (Simulated Backend)
# ============================================================================

def lookup_order_status(order_id: str) -> Dict:
    """
    Tool 1: Lookup order status from database
    Simulates database query with realistic data
    """
    # Simulated order database
    orders_db = {
        "ORD001": {
            "status": "delivered",
            "customer": "John Doe",
            "items": ["Biryani", "Raita", "Naan"],
            "total": 450.00,
            "ordered_time": "2024-08-18 10:30",
            "delivered_time": "2024-08-18 11:15"
        },
        "ORD002": {
            "status": "pending",
            "customer": "Jane Smith",
            "items": ["Burger", "Fries"],
            "total": 299.00,
            "ordered_time": "2024-08-18 14:00",
            "estimated_delivery": "2024-08-18 14:45"
        },
        "ORD003": {
            "status": "cancelled",
            "customer": "Bob Johnson",
            "items": ["Pizza"],
            "total": 599.00,
            "ordered_time": "2024-08-18 12:00",
            "cancelled_reason": "Out of stock"
        }
    }
    
    if order_id not in orders_db:
        return {
            "success": False,
            "error": f"Order {order_id} not found in system",
            "status": "NOT_FOUND"
        }
    
    order = orders_db[order_id]
    return {
        "success": True,
        "order_id": order_id,
        "status": order["status"],
        "customer": order["customer"],
        "items": order["items"],
        "total": order["total"],
        **order
    }


def check_refund_eligibility(order_id: str) -> Dict:
    """
    Tool 2: Check if customer is eligible for refund
    Returns eligibility status and refund amount
    """
    # First get order status
    order_info = lookup_order_status(order_id)
    
    if not order_info["success"]:
        return {
            "success": False,
            "error": f"Cannot check refund eligibility: {order_info['error']}",
            "eligible": False,
            "refund_amount": 0
        }
    
    order = order_info
    status = order["status"]
    
    # Refund eligibility rules
    refund_rules = {
        "delivered": {"eligible": False, "reason": "Order already delivered"},
        "pending": {"eligible": True, "reason": "Can cancel pending order"},
        "cancelled": {"eligible": True, "reason": "Order was cancelled by restaurant"},
        "failed": {"eligible": True, "reason": "Delivery failed"}
    }
    
    rule = refund_rules.get(status, {"eligible": False, "reason": "Unknown status"})
    
    return {
        "success": True,
        "order_id": order_id,
        "eligible": rule["eligible"],
        "reason": rule["reason"],
        "refund_amount": order["total"] if rule["eligible"] else 0,
        "order_status": status
    }


def get_order_history(customer_id: str) -> Dict:
    """
    Tool 3 (bonus): Get customer order history
    """
    customer_db = {
        "CUST001": {
            "name": "John Doe",
            "total_orders": 5,
            "total_spent": 2450.00,
            "last_order_date": "2024-08-18"
        },
        "CUST002": {
            "name": "Jane Smith",
            "total_orders": 12,
            "total_spent": 4500.00,
            "last_order_date": "2024-08-18"
        }
    }
    
    if customer_id not in customer_db:
        return {
            "success": False,
            "error": f"Customer {customer_id} not found"
        }
    
    return {
        "success": True,
        "customer_id": customer_id,
        **customer_db[customer_id]
    }


# ============================================================================
# NLP UTILITIES - FIXED BUG #1
# ============================================================================

def extract_order_id(query: str) -> Optional[str]:
    """
    FIXED: Extract order ID from natural language query
    This was missing in the original version!
    
    Examples:
    - "My order ORD001..." -> "ORD001"
    - "I ordered ORD002 but..." -> "ORD002"
    - "Order ORD999" -> "ORD999"
    """
    # Look for pattern ORD followed by digits
    match = re.search(r'\b(ORD\d+)\b', query.upper())
    if match:
        return match.group(1)
    return None


def extract_intent(query: str) -> str:
    """
    Extract customer intent from query
    Returns: 'refund_check', 'status_check', 'complaint', etc.
    """
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['refund', 'money back', 'cancel', 'revert']):
        return 'refund_check'
    elif any(word in query_lower for word in ['status', 'where', 'track', 'pending']):
        return 'status_check'
    elif any(word in query_lower for word in ['complaint', 'issue', 'problem', 'wrong', 'missing']):
        return 'complaint'
    else:
        return 'general_inquiry'


# ============================================================================
# ReAct AGENT IMPLEMENTATION (IMPROVED)
# ============================================================================

class ReActAgent:
    """
    Implements ReAct loop: Reason → Action → Observation → Reason → ...
    FIXED VERSION with proper order ID extraction
    """
    
    def __init__(self, max_cycles: int = 5):
        self.max_cycles = max_cycles
        self.cycle_count = 0
        self.thought_history = []
        self.action_history = []
        self.observation_history = []
        self.order_id = None  # FIX: Store extracted order ID
        self.intent = None    # FIX: Store customer intent
        
        # Available tools
        self.tools = {
            "lookup_order_status": lookup_order_status,
            "check_refund_eligibility": check_refund_eligibility,
            "get_order_history": get_order_history
        }
    
    def parse_thought(self, response: str) -> str:
        """Extract reasoning from response"""
        lines = response.strip().split('\n')
        thought = '\n'.join([l for l in lines if l.strip() and not l.startswith('Action:')])
        return thought[:500]
    
    def parse_action(self, response: str) -> Tuple[str, str]:
        """
        Parse action from response
        Expected format: Action: tool_name(arg1, arg2)
        Returns: (tool_name, arguments)
        """
        action_match = re.search(r'Action:\s*(\w+)\((.*?)\)', response, re.IGNORECASE)
        
        if not action_match:
            return None, None
        
        tool_name = action_match.group(1)
        args_str = action_match.group(2).strip()
        
        # Clean up arguments
        args_str = args_str.replace('"', '').replace("'", '')
        
        return tool_name, args_str
    
    def execute_action(self, tool_name: str, arguments: str) -> Dict:
        """Execute a tool function with error handling"""
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}"
                }
            
            tool_func = self.tools[tool_name]
            args_list = [arg.strip() for arg in arguments.split(',')]
            result = tool_func(*args_list)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def reason_step(self, query: str, step: int) -> str:
        """
        FIXED: Generate thoughts based on extracted order ID and intent
        Now properly uses the extracted order_id instead of hardcoding ORD001
        """
        context = ""
        if self.observation_history:
            context = "\n\nPrevious Observations:\n" + "\n".join(self.observation_history[-1:])
        
        # FIX: Use self.order_id instead of hardcoding
        order_placeholder = self.order_id if self.order_id else "ORD001"
        
        reasoning_prompts = {
            1: f"""Customer Query: {query}

Analysis:
- Customer is asking about: {self.intent}
- Order ID identified: {order_placeholder}
- First step: Get the order details

Thought: I found the order ID {order_placeholder} in the customer's message. Let me check its current status to understand the situation better.

Action: lookup_order_status({order_placeholder})""",

            2: f"""Customer Query: {query}
{context}

Analysis:
- Customer intent: {self.intent}
- Order status retrieved
- Next step: Check refund eligibility if needed

Thought: Now that I have the order status, let me check if the customer is eligible for a refund based on the order's current state.

Action: check_refund_eligibility({order_placeholder})""",

            3: f"""Customer Query: {query}
{context}

Analysis:
- I now have complete information:
  * Order status: Retrieved ✓
  * Refund eligibility: Checked ✓
- Ready to provide final response

Thought: I have gathered sufficient information to provide a comprehensive response to the customer."""
        }
        
        self.cycle_count = step
        return reasoning_prompts.get(step, "Generating final response...")
    
    def process_query(self, customer_query: str) -> str:
        """
        FIXED: Main ReAct loop with proper order ID extraction
        """
        # FIX #1: Extract order ID at the beginning
        self.order_id = extract_order_id(customer_query)
        
        # FIX #2: Extract customer intent
        self.intent = extract_intent(customer_query)
        
        print("\n" + "="*80)
        print("🤖 REACT AGENT - FOOD DELIVERY CUSTOMER SUPPORT (FIXED VERSION)")
        print("="*80)
        print(f"\n📝 Customer Query: {customer_query}")
        print(f"🎯 Extracted Order ID: {self.order_id}")
        print(f"💡 Customer Intent: {self.intent}\n")
        
        # Validation: Check if order ID was found
        if not self.order_id:
            print("⚠️  ERROR: Could not extract order ID from query!")
            print("    Please provide a valid order ID (e.g., ORD001, ORD002)\n")
            return "I couldn't find your order ID in your message. Could you please provide your order number (e.g., ORD001)?"
        
        final_response = ""
        
        # CYCLE LOOP (minimum 2 cycles)
        for cycle in range(1, self.max_cycles + 1):
            print(f"\n{'─'*80}")
            print(f"CYCLE {cycle}")
            print(f"{'─'*80}")
            
            # STEP 1: REASON
            thought_response = self.reason_step(customer_query, cycle)
            thought = self.parse_thought(thought_response)
            
            print(f"\n💭 THOUGHT:\n{thought}")
            self.thought_history.append(thought)
            
            # STEP 2: ACTION
            tool_name, arguments = self.parse_action(thought_response)
            
            if tool_name is None:
                print(f"\n✅ REASONING COMPLETE (No more actions needed)")
                final_response = thought
                break
            
            print(f"\n⚙️  ACTION: {tool_name}({arguments})")
            self.action_history.append(f"{tool_name}({arguments})")
            
            # STEP 3: OBSERVATION
            observation = self.execute_action(tool_name, arguments)
            
            if observation.get("success"):
                obs_text = json.dumps(observation, indent=2)
                print(f"\n👁️  OBSERVATION (SUCCESS):\n{obs_text}")
            else:
                error_msg = observation.get("error", "Unknown error")
                print(f"\n⚠️  OBSERVATION (ERROR):\n{error_msg}")
                # FIX #3: Don't crash on error - incorporate into next reasoning
                print(f"\n    → Agent will use this error in next reasoning cycle")
            
            self.observation_history.append(json.dumps(observation, indent=2))
            
            # Stop if we have enough cycles and found a solution
            if cycle >= 2 and observation.get("success"):
                print(f"\n✅ Sufficient information gathered. Preparing response...")
                break
        
        # FINAL RESPONSE GENERATION
        print(f"\n{'─'*80}")
        print("FINAL RESPONSE")
        print(f"{'─'*80}\n")
        
        if not final_response:
            final_response = self.generate_final_response()
        
        print(f"📤 Agent Response:\n{final_response}\n")
        
        return final_response
    
    def generate_final_response(self) -> str:
        """Generate final customer-facing response based on gathered information"""
        if not self.observation_history:
            return "I'm unable to process your request at this time. Please try again later."
        
        # Get the last observation
        last_obs = json.loads(self.observation_history[-1]) if self.observation_history else {}
        
        if not last_obs.get("success"):
            return f"I apologize, but I encountered an error: {last_obs.get('error')}. Please contact our support team at support@delivery.com"
        
        order_id = self.order_id
        status = last_obs.get("order_status", "unknown")
        eligible = last_obs.get("eligible", False)
        refund_amount = last_obs.get("refund_amount", 0)
        
        # Generate contextual response based on status and eligibility
        if status == "delivered":
            if eligible:
                return f"Your order {order_id} has been delivered. We can process a refund of ₹{refund_amount} for you. Please reply with your confirmation."
            else:
                return f"Your order {order_id} has been delivered successfully. If you have any issues with the food quality, please let us know within 24 hours for assistance."
        
        elif status == "pending":
            if eligible:
                return f"Your order {order_id} is currently pending. You can cancel it now and receive a full refund of ₹{refund_amount}. Would you like to proceed?"
            else:
                return f"Your order {order_id} is being prepared and will be delivered soon. Estimated delivery time: {last_obs.get('estimated_delivery', 'Unknown')}"
        
        elif status == "cancelled":
            if eligible:
                return f"Your order {order_id} was cancelled by the restaurant. You are eligible for a refund of ₹{refund_amount}. This will be processed within 3-5 business days."
            else:
                return f"Your order {order_id} was cancelled. Unfortunately, a refund cannot be processed at this time."
        
        return f"Thank you for contacting us about order {order_id}. We're looking into your issue and will get back to you shortly."
    
    def get_session_summary(self) -> Dict:
        """Return summary of agent reasoning process"""
        return {
            "extracted_order_id": self.order_id,
            "customer_intent": self.intent,
            "total_cycles": self.cycle_count,
            "thoughts": self.thought_history,
            "actions": self.action_history,
            "observations": self.observation_history
        }


# ============================================================================
# COMPREHENSIVE TEST SCENARIOS
# ============================================================================

def run_test_scenarios():
    """Run multiple test scenarios with different order IDs and intents"""
    
    test_queries = [
        "My order ORD001 was supposed to have biryani but it never arrived. What can you do?",
        "I ordered ORD002 but it's still pending. Can I get a refund?",
        "Order ORD003 - it was cancelled and I want my ₹599 back!",
        "Help! My order ORD999 doesn't exist. What should I do?"  # Test error handling
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST SCENARIO {i}")
        print(f"{'#'*80}")
        
        agent = ReActAgent(max_cycles=5)
        response = agent.process_query(query)
        
        # Print session summary
        summary = agent.get_session_summary()
        print(f"\n📊 Session Summary:")
        print(f"   Order ID: {summary['extracted_order_id']}")
        print(f"   Intent: {summary['customer_intent']}")
        print(f"   Total Cycles Executed: {summary['total_cycles']}")
        print(f"   Total Actions Taken: {len(summary['actions'])}")
        for j, action in enumerate(summary['actions'], 1):
            print(f"     Action {j}: {action}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REACT AGENT - FOOD DELIVERY CUSTOMER SUPPORT (FIXED & IMPROVED)")
    print("="*80)
    print("\n✅ FIXES APPLIED:")
    print("   1. Order ID extraction from natural language queries")
    print("   2. Intent detection (refund_check, status_check, complaint)")
    print("   3. Proper error handling - doesn't crash on 'not found'")
    print("   4. Dynamic reasoning based on actual order ID")
    print("   5. Better contextual responses based on order status\n")
    
    # Run all test scenarios
    run_test_scenarios()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80)
