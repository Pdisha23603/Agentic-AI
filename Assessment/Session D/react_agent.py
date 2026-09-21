"""
ReAct (Reason + Action) Agent for Food Delivery Customer Support
Implements 2+ reasoning cycles with tool invocations and error handling
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
    # Simulated customer history
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
# ReAct AGENT IMPLEMENTATION
# ============================================================================

class ReActAgent:
    """
    Implements ReAct loop: Reason → Action → Observation → Reason → ...
    """
    
    def __init__(self, max_cycles: int = 5):
        self.max_cycles = max_cycles
        self.cycle_count = 0
        self.thought_history = []
        self.action_history = []
        self.observation_history = []
        
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
        return thought[:500]  # Limit thought size
    
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
        
        # Clean up arguments (remove quotes)
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
            
            # Parse arguments
            args_list = [arg.strip() for arg in arguments.split(',')]
            
            # Call tool with arguments
            result = tool_func(*args_list)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def reason_step(self, query: str, previous_observations: List[str] = None) -> str:
        """
        REASON Step: Generate thoughts based on query and observations
        In a real implementation, this would call an LLM like Claude or GPT
        """
        if previous_observations is None:
            previous_observations = []
        
        # Build context from previous observations
        context = ""
        if previous_observations:
            context = "\n\nPrevious Observations:\n" + "\n".join(previous_observations)
        
        # Simulated LLM response (in production, call Claude/GPT API here)
        reasoning_prompts = {
            1: f"""Customer Issue: {query}

Let me analyze this step by step:
1. I need to understand the customer's problem
2. I should lookup their order to see the current status
3. Based on the status, I'll determine next steps

Thought: The customer seems to have a complaint about their order. Let me first check the order status by looking up the order ID from their complaint.

Action: lookup_order_status(ORD001)""",

            2: f"""Customer Issue: {query}
{context}

Now I have the order status. Let me check if they're eligible for a refund since they're complaining about the order.

Thought: Based on the order status, I should check if the customer is eligible for a refund.

Action: check_refund_eligibility(ORD001)""",

            3: f"""Customer Issue: {query}
{context}

I now have both the order status and refund eligibility. Let me prepare a final response.

Thought: I have all the information needed to help the customer. Let me generate a comprehensive response."""
        }
        
        self.cycle_count += 1
        return reasoning_prompts.get(self.cycle_count, "Generating final response...")
    
    def process_query(self, customer_query: str) -> str:
        """
        Main ReAct loop: Execute multiple reasoning/action/observation cycles
        """
        print("\n" + "="*80)
        print("🤖 REACT AGENT - FOOD DELIVERY CUSTOMER SUPPORT")
        print("="*80)
        print(f"\n📝 Customer Query: {customer_query}\n")
        
        final_response = ""
        
        # CYCLE LOOP (minimum 2 cycles)
        for cycle in range(1, self.max_cycles + 1):
            print(f"\n{'─'*80}")
            print(f"CYCLE {cycle}")
            print(f"{'─'*80}")
            
            # STEP 1: REASON
            thought_response = self.reason_step(customer_query, self.observation_history)
            thought = self.parse_thought(thought_response)
            
            print(f"\n💭 THOUGHT:\n{thought}")
            self.thought_history.append(thought)
            
            # STEP 2: ACTION
            tool_name, arguments = self.parse_action(thought_response)
            
            if tool_name is None:
                print(f"\n✅ FINAL RESPONSE READY (No more actions needed)")
                final_response = thought
                break
            
            print(f"\n⚙️  ACTION: {tool_name}({arguments})")
            self.action_history.append(f"{tool_name}({arguments})")
            
            # STEP 3: OBSERVATION
            observation = self.execute_action(tool_name, arguments)
            
            if observation.get("success"):
                obs_text = json.dumps(observation, indent=2)
                print(f"\n👁️  OBSERVATION:\n{obs_text}")
            else:
                error_msg = observation.get("error", "Unknown error")
                print(f"\n⚠️  OBSERVATION (ERROR):\n{error_msg}")
            
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
        """Generate final customer-facing response"""
        if not self.observation_history:
            return "I'm unable to process your request at this time. Please try again later."
        
        last_obs = json.loads(self.observation_history[-1])
        
        if not last_obs.get("success"):
            return f"I apologize, but I encountered an error: {last_obs.get('error')}. Please contact our support team."
        
        if "order_status" in last_obs:
            status = last_obs["order_status"]
            if status == "delivered":
                return f"Your order {last_obs.get('order_id')} has been delivered. If you have any issues, please let us know within 24 hours for assistance."
            elif status == "pending":
                return f"Your order {last_obs.get('order_id')} is currently being prepared and will be delivered soon."
            elif status == "cancelled":
                if last_obs.get("eligible"):
                    return f"Your order was cancelled. You are eligible for a full refund of ₹{last_obs.get('refund_amount')}. It will be processed within 3-5 business days."
        
        return "Thank you for contacting us. We're looking into your issue and will get back to you shortly."
    
    def get_session_summary(self) -> Dict:
        """Return summary of agent reasoning process"""
        return {
            "total_cycles": self.cycle_count,
            "thoughts": self.thought_history,
            "actions": self.action_history,
            "observations": self.observation_history
        }


# ============================================================================
# TEST SCENARIOS
# ============================================================================

def run_test_scenarios():
    """Run multiple test scenarios"""
    
    test_queries = [
        "My order ORD001 was supposed to have biryani but it never arrived. What can you do?",
        "I ordered ORD002 but it's still pending. Can I get a refund?",
        "Order ORD999 - I don't think this exists, but what happens?"
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
        print(f"   Total Cycles Executed: {summary['total_cycles']}")
        print(f"   Total Actions Taken: {len(summary['actions'])}")
        print(f"   Cycle Trace:")
        for j, thought in enumerate(summary['thoughts'], 1):
            print(f"     Cycle {j}: {thought[:100]}...")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REACT AGENT - FOOD DELIVERY CUSTOMER SUPPORT SYSTEM")
    print("="*80)
    
    # Run all test scenarios
    run_test_scenarios()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)
