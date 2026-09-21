"""
Perceive -> Think -> Act loop simulation for a food-delivery ordering agent.

No external dependencies -- pure standard library, so it just runs as-is.

Install: nothing required.
Run:
    python agent_loop_demo.py
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta


# ---------- Mock "tools" the agent can call ----------

MOCK_DB = {
    "Saravana Bhavan": {
        "branches": ["Saravana Bhavan - MG Road", "Saravana Bhavan - Indiranagar"],
        # hard-code unavailability at 19:00 to demonstrate the fallback branch
        "closed_slots": {"19:00"},
        "menu": {"Masala Dosa": True},
        "next_open_slot": "19:30",
    }
}


def check_restaurant_availability(restaurant: str, time_str: str) -> dict:
    info = MOCK_DB.get(restaurant)
    if not info:
        return {"available": False, "reason": "restaurant_not_found"}
    if time_str in info["closed_slots"]:
        return {
            "available": False,
            "reason": "slot_unavailable",
            "next_open_slot": info["next_open_slot"],
        }
    return {"available": True, "branch": info["branches"][0]}


def check_item_availability(restaurant: str, item: str) -> dict:
    info = MOCK_DB.get(restaurant, {})
    return {"available": info.get("menu", {}).get(item, False)}


def estimate_delivery_time(restaurant: str, target_time: str) -> dict:
    return {"eta": target_time, "feasible": True}


def place_order(restaurant: str, items: dict, time_str: str) -> dict:
    return {
        "status": "confirmed",
        "restaurant": restaurant,
        "items": items,
        "time": time_str,
    }


# ---------- Agent state ----------

@dataclass
class OrderRequest:
    restaurant: str
    item: str
    quantity: int
    requested_time: str
    resolved_time: str = None
    awaiting_user: bool = False
    log: list = field(default_factory=list)


# ---------- Perceive ----------

def perceive(user_message: str) -> OrderRequest:
    # In a real agent this would be an LLM extraction call.
    # Hard-coded here to keep the demo dependency-free and deterministic.
    req = OrderRequest(
        restaurant="Saravana Bhavan",
        item="Masala Dosa",
        quantity=2,
        requested_time="19:00",
    )
    req.log.append(f"PERCEIVE: parsed order -> {req.quantity}x {req.item} "
                    f"from {req.restaurant} at {req.requested_time}")
    return req


# ---------- Think + Act loop ----------

def think_and_act(req: OrderRequest) -> OrderRequest:
    # Step 1: availability check
    avail = check_restaurant_availability(req.restaurant, req.requested_time)
    req.log.append(f"ACT: check_restaurant_availability -> {avail}")

    if not avail["available"]:
        # THINK: precondition failed -- don't place the order, re-plan
        next_slot = avail.get("next_open_slot")
        req.log.append(
            "THINK: restaurant unavailable at requested time. "
            f"Nearest open slot is {next_slot}. This changes what the user "
            "asked for, so surface it instead of silently substituting."
        )
        req.awaiting_user = True
        req.log.append(
            f"ACT: ask_user(\"Saravana Bhavan isn't taking orders for 7 PM. "
            f"The next available slot is {next_slot} -- shall I book that "
            f"instead, or would you like a different restaurant?\")"
        )
        return req  # loop pauses here, waiting on user response

    # Step 2: item availability
    item_check = check_item_availability(req.restaurant, req.item)
    req.log.append(f"ACT: check_item_availability -> {item_check}")
    if not item_check["available"]:
        req.awaiting_user = True
        req.log.append("ACT: ask_user(\"Masala Dosa isn't available right now.\")")
        return req

    # Step 3: delivery time feasibility
    eta = estimate_delivery_time(req.restaurant, req.requested_time)
    req.log.append(f"ACT: estimate_delivery_time -> {eta}")

    # Step 4: place order (only if everything upstream cleared)
    order = place_order(req.restaurant, {req.item: req.quantity}, req.requested_time)
    req.log.append(f"ACT: place_order -> {order}")
    req.resolved_time = req.requested_time
    return req


def resume_after_user_response(req: OrderRequest, user_accepts_new_slot: bool,
                                new_slot: str) -> OrderRequest:
    """Loop re-enters Perceive/Think once the user answers the clarifying question."""
    req.log.append(f"PERCEIVE: user response -> accepts_new_slot={user_accepts_new_slot}")
    if not user_accepts_new_slot:
        req.log.append("THINK: user declined -- stop, no order placed.")
        req.awaiting_user = False
        return req

    req.requested_time = new_slot
    req.awaiting_user = False
    req.log.append(f"THINK: retry with updated time {new_slot}")
    return think_and_act(req)


# ---------- Run the demo ----------

def main():
    user_message = "Order 2 portions of Masala Dosa from Saravana Bhavan for delivery at 7 PM tonight."
    print("User message:", user_message)
    print()

    req = perceive(user_message)
    req = think_and_act(req)

    for line in req.log:
        print(line)

    if req.awaiting_user:
        print()
        print("--- Simulating the user accepting the fallback slot ---")
        req = resume_after_user_response(req, user_accepts_new_slot=True, new_slot="19:30")
        print()
        for line in req.log[-4:]:
            print(line)


if __name__ == "__main__":
    main()
