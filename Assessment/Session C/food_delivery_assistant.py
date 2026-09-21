"""
Agentic Food Delivery Assistant (Capstone)
--------------------------------------------
A console-based multi-tool AI agent for a food delivery platform.

Combines:
  - MCP-style tool schemas (name, description, parameters) printed at startup
  - Four dedicated tool functions: place_order(), track_order(),
    file_complaint(), get_recommendations()
  - A session_log that records every tool call (args + result)
  - A session_memory dict updated after every action
  - decide_response_strategy(action_type, memory) -> 'prompt' | 'rag' | 'fine_tuned'
  - A menu-driven REPL loop, with a full session report on exit

Run with:  python3 food_delivery_assistant.py
No third-party packages required (pure standard library).
"""

import random
import sys
import uuid

random.seed(7)  # deterministic simulated outcomes for demo purposes

# ---------------------------------------------------------------------
# Simulated domain data
# ---------------------------------------------------------------------
MENU_PRICES = {
    "pizza": 9.99, "biryani": 11.50, "sushi": 8.75,
    "burger": 6.99, "pasta": 10.25, "tacos": 7.50,
    "curry": 10.00, "ramen": 9.50,
}

CUISINE_MENU = {
    "italian": ["pizza", "pasta"],
    "indian": ["biryani", "curry"],
    "japanese": ["sushi", "ramen"],
    "mexican": ["tacos"],
    "american": ["burger"],
}

ORDER_STATUSES = ["Preparing", "Out for delivery", "Delivered", "Awaiting pickup"]

# ---------------------------------------------------------------------
# MCP-style tool schemas
# ---------------------------------------------------------------------
TOOL_SCHEMAS = {
    "place_order": {
        "name": "place_order",
        "description": "Places a new food order for the customer and returns an order confirmation.",
        "parameters": {
            "items": "list[str] - menu items to order (e.g. ['pizza', 'pasta'])",
            "cuisine": "str - cuisine type of the order (e.g. 'italian')",
        },
    },
    "track_order": {
        "name": "track_order",
        "description": "Looks up the live status and ETA of an existing order.",
        "parameters": {
            "order_id": "str - the ID of the order to track",
        },
    },
    "file_complaint": {
        "name": "file_complaint",
        "description": "Files a customer complaint about an order and classifies its severity.",
        "parameters": {
            "issue_text": "str - free-text description of the problem",
        },
    },
    "get_recommendations": {
        "name": "get_recommendations",
        "description": "Returns personalised menu recommendations based on the customer's preferred cuisine and history.",
        "parameters": {
            "preferred_cuisine": "str (optional) - cuisine to base recommendations on",
        },
    },
}


def print_tool_schemas():
    print("=" * 70)
    print("AVAILABLE TOOLS (MCP-style schemas)")
    print("=" * 70)
    for schema in TOOL_SCHEMAS.values():
        print(f"\nTool: {schema['name']}")
        print(f"  Description: {schema['description']}")
        print("  Parameters:")
        for pname, pdesc in schema["parameters"].items():
            print(f"    - {pname}: {pdesc}")
    print("\n" + "=" * 70)


# ---------------------------------------------------------------------
# Tool functions (pure business logic, no I/O)
# ---------------------------------------------------------------------
def place_order(items, cuisine):
    order_id = str(uuid.uuid4())[:8]
    total = round(sum(MENU_PRICES.get(i.lower(), 5.00) for i in items), 2)
    return {
        "order_id": order_id,
        "items": items,
        "cuisine": cuisine,
        "total_price": total,
        "status": "placed",
    }


def track_order(order_id):
    status = random.choice(ORDER_STATUSES)
    eta = random.randint(5, 40)
    return {
        "order_id": order_id,
        "status": status,
        "eta_minutes": eta,
    }


def file_complaint(issue_text):
    complaint_id = str(uuid.uuid4())[:8]
    f = issue_text.lower()
    if any(k in f for k in ["refund", "again", "unacceptable", "never"]):
        severity = "high"
    elif any(k in f for k in ["late", "cold", "wrong", "missing"]):
        severity = "medium"
    else:
        severity = "low"
    return {
        "complaint_id": complaint_id,
        "issue": issue_text,
        "severity": severity,
    }


def get_recommendations(preferred_cuisine):
    if preferred_cuisine:
        pool = CUISINE_MENU.get(preferred_cuisine.lower(), list(MENU_PRICES.keys()))
    else:
        pool = list(MENU_PRICES.keys())
    recs = random.sample(pool, min(3, len(pool)))
    return {
        "preferred_cuisine": preferred_cuisine,
        "recommendations": recs,
    }


TOOL_FUNCTIONS = {
    "place_order": place_order,
    "track_order": track_order,
    "file_complaint": file_complaint,
    "get_recommendations": get_recommendations,
}


# ---------------------------------------------------------------------
# Strategy selection
# ---------------------------------------------------------------------
def decide_response_strategy(action_type, memory):
    """
    Chooses a response strategy ('prompt' | 'rag' | 'fine_tuned') based on
    the action being performed and the current session memory state.
    """
    if action_type == "place_order":
        # Simple, templated confirmation is enough for a new order
        return "prompt"

    elif action_type == "track_order":
        # Tracking needs a live retrieval-style lookup
        return "rag"

    elif action_type == "file_complaint":
        # A repeat complainer gets escalated to the fine-tuned specialist model
        if memory["complaints_filed"] >= 1:
            return "fine_tuned"
        return "rag"

    elif action_type == "get_recommendations":
        # With a known cuisine preference we can do a targeted (RAG) lookup;
        # otherwise fall back to a generic templated suggestion
        if memory["preferred_cuisine"]:
            return "rag"
        return "prompt"

    return "prompt"


# ---------------------------------------------------------------------
# Input handling (supports interactive use AND scripted/demo input)
# ---------------------------------------------------------------------
class InputSource:
    """
    Wraps input() so the same menu loop can run interactively (reading
    from the real console) or from a pre-scripted list of answers
    (used by --demo mode, useful for testing / non-interactive runs).
    """

    def __init__(self, scripted_inputs=None):
        self.scripted_inputs = list(scripted_inputs) if scripted_inputs else None

    def get(self, prompt):
        if self.scripted_inputs is not None:
            if not self.scripted_inputs:
                raise EOFError("Demo input queue exhausted")
            value = self.scripted_inputs.pop(0)
            print(f"{prompt}{value}")
            return value
        return input(prompt)


# ---------------------------------------------------------------------
# Agent: ties memory, logging, tools and strategy together
# ---------------------------------------------------------------------
class FoodDeliveryAgent:
    def __init__(self, input_source):
        self.io = input_source
        self.session_memory = {
            "orders_placed": 0,
            "complaints_filed": 0,
            "preferred_cuisine": None,
            "interaction_count": 0,
        }
        self.session_log = []  # each entry: {step, action, tool, args, strategy, result}

    def _log_and_report(self, action_type, tool_name, args, result):
        strategy = decide_response_strategy(action_type, self.session_memory)

        entry = {
            "step": len(self.session_log) + 1,
            "action": action_type,
            "tool": tool_name,
            "args": args,
            "strategy": strategy,
            "result": result,
        }
        self.session_log.append(entry)

        print(f"\n  [Tool called]  {tool_name}({args})")
        print(f"  [Strategy]     {strategy}")
        print(f"  [Result]       {result}")

        self.session_memory["interaction_count"] += 1
        return strategy

    # ---- Menu action handlers -------------------------------------
    def action_place_order(self):
        raw_items = self.io.get("Enter items to order (comma-separated, e.g. pizza,pasta): ")
        items = [i.strip() for i in raw_items.split(",") if i.strip()]
        cuisine = self.io.get("Enter cuisine type (e.g. italian): ").strip()

        args = {"items": items, "cuisine": cuisine}
        result = place_order(**args)
        self._log_and_report("place_order", "place_order", args, result)

        self.session_memory["orders_placed"] += 1
        self.session_memory["preferred_cuisine"] = cuisine or self.session_memory["preferred_cuisine"]

    def action_track_order(self):
        order_id = self.io.get("Enter order ID to track: ").strip()

        args = {"order_id": order_id}
        result = track_order(**args)
        self._log_and_report("track_order", "track_order", args, result)

    def action_file_complaint(self):
        issue_text = self.io.get("Describe your issue: ").strip()

        args = {"issue_text": issue_text}
        result = file_complaint(**args)
        self._log_and_report("file_complaint", "file_complaint", args, result)

        self.session_memory["complaints_filed"] += 1

    def action_get_recommendations(self):
        cuisine = self.session_memory["preferred_cuisine"]
        prompt_text = f"Preferred cuisine [{cuisine or 'none on file'}] (press Enter to keep, or type new): "
        typed = self.io.get(prompt_text).strip()
        preferred_cuisine = typed if typed else cuisine

        args = {"preferred_cuisine": preferred_cuisine}
        result = get_recommendations(**args)
        self._log_and_report("get_recommendations", "get_recommendations", args, result)

        if typed:
            self.session_memory["preferred_cuisine"] = typed

    # ---- Session report ---------------------------------------------
    def print_session_report(self):
        print("\n" + "#" * 70)
        print("FULL SESSION REPORT")
        print("#" * 70)

        print("\nActions taken (in order):")
        for entry in self.session_log:
            print(f"  Step {entry['step']}: action='{entry['action']}' "
                  f"tool='{entry['tool']}' strategy='{entry['strategy']}'")
            print(f"           args={entry['args']}")
            print(f"           result={entry['result']}")

        print("\nFinal session_memory state:")
        for k, v in self.session_memory.items():
            print(f"  {k:20s}: {v}")

        print("\n" + "#" * 70)


# ---------------------------------------------------------------------
# Menu loop
# ---------------------------------------------------------------------
MENU_TEXT = """
============================================
  FOOD DELIVERY ASSISTANT
============================================
1. Place Order
2. Track Order
3. File Complaint
4. Get Personalised Recommendations
5. Exit
============================================
"""


def run_menu(input_source):
    agent = FoodDeliveryAgent(input_source)

    print_tool_schemas()

    while True:
        print(MENU_TEXT)
        choice = input_source.get("Choose an option (1-5): ").strip()

        if choice == "1":
            agent.action_place_order()
        elif choice == "2":
            agent.action_track_order()
        elif choice == "3":
            agent.action_file_complaint()
        elif choice == "4":
            agent.action_get_recommendations()
        elif choice == "5":
            agent.print_session_report()
            print("\nSession ended. Thanks for using the Food Delivery Assistant!")
            break
        else:
            print("Invalid option, please choose a number from 1 to 5.")


def build_demo_input_source():
    """Pre-scripted walkthrough exercising every menu option at least once,
    including a second complaint to demonstrate the strategy shifting to
    'fine_tuned' on repeat complaints."""
    scripted = [
        # Place an order
        "1", "pizza,pasta", "italian",
        # Track that order (use a fake ID for the demo)
        "2", "abc12345",
        # Get recommendations (cuisine already known from the order)
        "4", "",
        # File a first complaint -> expect 'rag'
        "3", "My order arrived a bit late and cold",
        # File a second complaint -> expect 'fine_tuned' (repeat complainer)
        "3", "This is unacceptable, it happened again, I want a refund",
        # Exit
        "5",
    ]
    return InputSource(scripted_inputs=scripted)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        source = build_demo_input_source()
    else:
        source = InputSource()  # real interactive console input

    run_menu(source)
