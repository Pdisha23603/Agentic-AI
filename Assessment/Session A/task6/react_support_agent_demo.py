"""
ReAct (Reason -> Action -> Observation) loop simulation for a customer
support agent handling a refund/discount request.

Zero dependencies -- pure standard library.

Run:
    python3 react_support_agent_demo.py
"""

from dataclasses import dataclass, field


# ---------- Mock backend "tools" ----------

ORDER_DB = {
    "FD4521": {
        "promised_time": "19:00",
        "actual_time": "19:41",
        "delay_minutes": 41,
        "order_value": 450,
        "prior_refunds_on_order": 0,
    }
}


def get_order_details(order_id: str) -> dict:
    order = ORDER_DB.get(order_id)
    if not order:
        return {"found": False}
    return {"found": True, **order}


def check_refund_policy(delay_minutes: int, order_value: int) -> dict:
    if delay_minutes > 30:
        auto_approvable = order_value <= 1000  # manual review above this
        return {
            "eligible": True,
            "options": ["full_refund", "discount_50pct_next_order"],
            "auto_approvable": auto_approvable,
        }
    return {"eligible": False, "options": [], "auto_approvable": False}


def issue_refund(order_id: str, amount: int) -> dict:
    return {"status": "issued", "order_id": order_id, "amount": amount,
             "transaction_id": f"TXN-{order_id}-REFUND"}


def issue_discount_code(order_id: str) -> dict:
    return {"status": "issued", "order_id": order_id, "code": f"SAVE50-{order_id}"}


# ---------- ReAct loop scaffolding ----------

@dataclass
class ReActTrace:
    steps: list = field(default_factory=list)
    verified_facts: dict = field(default_factory=dict)  # only set via Observations

    def log(self, kind: str, content: str):
        self.steps.append(f"{kind}: {content}")

    def print_trace(self):
        for step in self.steps:
            print(step)


def run_support_agent(order_id: str, user_message: str) -> ReActTrace:
    trace = ReActTrace()

    # ----- Cycle 1: verify the claim against system data -----
    trace.log("REASON", "User claims a 40-min delay and cold food, wants a "
                         "refund or discount. Must verify against order "
                         "records before taking any financial action -- "
                         "user self-report alone is not a valid basis to act.")
    trace.log("ACTION", f"get_order_details(order_id='{order_id}')")
    order = get_order_details(order_id)
    trace.log("OBSERVATION", str(order))

    if not order["found"]:
        trace.log("REASON", "Order not found -- cannot proceed. Ask user to "
                             "confirm the order ID rather than guessing.")
        return trace

    trace.verified_facts["delay_minutes"] = order["delay_minutes"]
    trace.verified_facts["order_value"] = order["order_value"]

    # ----- Cycle 2: check what policy actually permits -----
    trace.log("REASON", f"System confirms {order['delay_minutes']} min delay, "
                         "corroborating the user. Now check policy -- the "
                         "remedy and amount are a business rule, not something "
                         "to infer from the conversation.")
    trace.log("ACTION", f"check_refund_policy(delay_minutes="
                         f"{order['delay_minutes']}, order_value={order['order_value']})")
    policy = check_refund_policy(order["delay_minutes"], order["order_value"])
    trace.log("OBSERVATION", str(policy))

    # ----- Guardrail: action gated on verified observation, not on the reasoning alone -----
    if not policy["eligible"]:
        trace.log("REASON", "Policy does not support a refund/discount for "
                             "this delay length. Explain this to the user "
                             "instead of taking a financial action.")
        return trace

    if not policy["auto_approvable"]:
        trace.log("REASON", "Order value exceeds auto-approval threshold -- "
                             "route to human review instead of calling a "
                             "payout tool directly.")
        trace.log("ACTION", "escalate_to_human_review(order_id, reason='high_value_refund')")
        return trace

    # ----- Cycle 3: present verified, policy-approved options; execute user's choice -----
    trace.log("REASON", "Both facts and policy are verified and within "
                         "auto-approval bounds. User asked for 'refund OR "
                         "discount' -- present both, let the user choose, "
                         "rather than deciding on their behalf.")
    trace.log("ACTION", f"present_options_to_user(options={policy['options']})")
    user_choice = "full_refund"  # simulated user selection
    trace.log("OBSERVATION", f"user selected: '{user_choice}'")

    trace.log("REASON", "User chose full refund. Proceed to execute -- this "
                         "is now grounded in a verified delay, a verified "
                         "policy match, and an explicit user choice.")
    if user_choice == "full_refund":
        trace.log("ACTION", f"issue_refund(order_id='{order_id}', amount={order['order_value']})")
        result = issue_refund(order_id, order["order_value"])
    else:
        trace.log("ACTION", f"issue_discount_code(order_id='{order_id}')")
        result = issue_discount_code(order_id)
    trace.log("OBSERVATION", str(result))

    return trace


def main():
    user_message = ("My order #FD4521 was 40 minutes late and the food "
                     "arrived cold. I want either a full refund or a "
                     "significant discount on my next order.")
    print("User:", user_message)
    print()
    trace = run_support_agent("FD4521", user_message)
    trace.print_trace()


if __name__ == "__main__":
    main()
