"""
Multi-Agent Order Lifecycle System
------------------------------------
Three collaborating agents handle a food-delivery order end-to-end,
orchestrated by a Coordinator:

    OrderAgent    -> builds an order summary from raw customer input
    DispatchAgent -> assigns a delivery partner + ETA
    SupportAgent  -> classifies post-delivery feedback and picks a
                     response technique (prompt / RAG / fine-tuned)

Run with:  python3 order_lifecycle_system.py
No third-party packages required (pure standard library).
"""

import random
import time
import uuid

random.seed(42)  # deterministic demo output

# ---------------------------------------------------------------------
# Simulated data
# ---------------------------------------------------------------------
DELIVERY_PARTNERS = [
    {"name": "Raj K.", "vehicle": "bike", "rating": 4.8},
    {"name": "Maria S.", "vehicle": "scooter", "rating": 4.6},
    {"name": "Tom L.", "vehicle": "bike", "rating": 4.9},
    {"name": "Aisha B.", "vehicle": "car", "rating": 4.5},
]

MENU_PRICES = {
    "pizza": 9.99,
    "biryani": 11.50,
    "sushi": 8.75,
    "burger": 6.99,
    "pasta": 10.25,
    "tacos": 7.50,
}

COMPLAINT_KEYWORDS = ["late", "cold", "wrong", "missing", "bad", "terrible"]
ESCALATE_KEYWORDS = ["refund", "again", "second time", "never", "worst", "unacceptable"]
POSITIVE_KEYWORDS = ["great", "delicious", "fast", "amazing", "thanks", "loved", "excellent"]


# ---------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------
class OrderAgent:
    """Builds a structured order summary from raw customer input."""

    def process(self, data):
        items = data.get("items", [])
        total = round(sum(MENU_PRICES.get(item.lower(), 5.00) for item in items), 2)

        order_summary = {
            "order_id": str(uuid.uuid4())[:8],
            "customer_id": data.get("customer_id"),
            "items": items,
            "total_price": total,
            "delivery_address": data.get("address"),
            "cuisine": data.get("cuisine"),
        }
        return order_summary


class DispatchAgent:
    """Assigns a delivery partner and an ETA based on the order."""

    def process(self, order_summary):
        partner = random.choice(DELIVERY_PARTNERS)
        eta_minutes = random.randint(20, 45)

        dispatch_details = {
            "order_id": order_summary["order_id"],
            "assigned_partner": partner["name"],
            "vehicle": partner["vehicle"],
            "partner_rating": partner["rating"],
            "eta_minutes": eta_minutes,
        }
        return dispatch_details


class SupportAgent:
    """Classifies post-delivery feedback and selects a response technique."""

    def _classify(self, feedback):
        f = feedback.lower()
        if any(kw in f for kw in ESCALATE_KEYWORDS):
            return "escalate"
        if any(kw in f for kw in COMPLAINT_KEYWORDS):
            return "complaint"
        if any(kw in f for kw in POSITIVE_KEYWORDS):
            return "positive"
        return "positive"  # default to positive/neutral if nothing matches

    def _select_technique(self, classification):
        mapping = {
            "positive": "prompt",
            "complaint": "rag",
            "escalate": "fine_tuned",
        }
        return mapping[classification]

    def _generate_response(self, classification, technique, feedback):
        if technique == "prompt":
            return (f"[Prompt] Thanks so much for the feedback: \"{feedback}\" "
                     f"We're glad you enjoyed your order!")
        if technique == "rag":
            return (f"[RAG-Lookup] Looking up our service-recovery policy for "
                     f"\"{feedback}\"... Here's a 15% discount code for your next "
                     f"order, and we've flagged this with the restaurant partner.")
        return (f"[Fine-Tuned-Model] We sincerely apologize for \"{feedback}\". "
                f"This has been escalated to a senior support specialist and a "
                f"full refund has been issued to your account.")

    def process(self, feedback):
        classification = self._classify(feedback)
        technique = self._select_technique(classification)
        response = self._generate_response(classification, technique, feedback)

        return {
            "feedback": feedback,
            "classification": classification,
            "technique_selected": technique,
            "response": response,
        }


# ---------------------------------------------------------------------
# Coordinator: orchestrates the full order lifecycle
# ---------------------------------------------------------------------
class Coordinator:
    def __init__(self):
        self.order_agent = OrderAgent()
        self.dispatch_agent = DispatchAgent()
        self.support_agent = SupportAgent()

    def run_lifecycle(self, customer_input, feedback):
        start_time = time.perf_counter()

        # --- Step 1: OrderAgent ---
        order_summary = self.order_agent.process(customer_input)
        # simulate processing latency
        time.sleep(random.uniform(0.02, 0.05))

        # --- Step 2: DispatchAgent ---
        dispatch_details = self.dispatch_agent.process(order_summary)
        time.sleep(random.uniform(0.02, 0.05))

        # --- Step 3: SupportAgent ---
        support_result = self.support_agent.process(feedback)
        time.sleep(random.uniform(0.02, 0.05))

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        self._print_report(order_summary, dispatch_details, support_result, elapsed_ms)

        return {
            "order_summary": order_summary,
            "dispatch_details": dispatch_details,
            "support_result": support_result,
            "processing_time_ms": elapsed_ms,
        }

    def _print_report(self, order_summary, dispatch_details, support_result, elapsed_ms):
        print("\n" + "=" * 70)
        print(f"LIFECYCLE REPORT — Order {order_summary['order_id']}")
        print("=" * 70)

        print("\n[1] ORDER SUMMARY")
        for k, v in order_summary.items():
            print(f"    {k:18s}: {v}")

        print("\n[2] DISPATCH DETAILS")
        for k, v in dispatch_details.items():
            print(f"    {k:18s}: {v}")

        print("\n[3] SUPPORT / FEEDBACK HANDLING")
        print(f"    {'feedback':18s}: {support_result['feedback']}")
        print(f"    {'classification':18s}: {support_result['classification']}")
        print(f"    {'technique_selected':18s}: {support_result['technique_selected']}")
        print(f"    {'response':18s}: {support_result['response']}")

        print(f"\nTotal simulated processing time: {elapsed_ms} ms")
        print("=" * 70)


# ---------------------------------------------------------------------
# Demo: run the lifecycle for two different customer scenarios
# ---------------------------------------------------------------------
def run_demo():
    coordinator = Coordinator()

    # Scenario 1: Smooth delivery, happy customer
    customer_input_1 = {
        "customer_id": "cust_501",
        "items": ["Pizza", "Pasta"],
        "cuisine": "Italian",
        "address": "12 Riverside Ave",
    }
    feedback_1 = "The food arrived fast and was delicious, thanks!"

    # Scenario 2: Delivery problem, escalating complaint
    customer_input_2 = {
        "customer_id": "cust_502",
        "items": ["Sushi", "Tacos"],
        "cuisine": "Fusion",
        "address": "88 Oak Street",
    }
    feedback_2 = "This is unacceptable, my order arrived cold again and I want a refund!"

    print("SCENARIO 1: Smooth delivery")
    result_1 = coordinator.run_lifecycle(customer_input_1, feedback_1)

    print("\n\nSCENARIO 2: Delivery complaint / escalation")
    result_2 = coordinator.run_lifecycle(customer_input_2, feedback_2)

    print("\n\n" + "#" * 70)
    print("TECHNIQUE COMPARISON ACROSS SCENARIOS")
    print("#" * 70)
    print(f"Scenario 1 -> classification: {result_1['support_result']['classification']:10s} "
          f"| technique: {result_1['support_result']['technique_selected']}")
    print(f"Scenario 2 -> classification: {result_2['support_result']['classification']:10s} "
          f"| technique: {result_2['support_result']['technique_selected']}")


if __name__ == "__main__":
    run_demo()
