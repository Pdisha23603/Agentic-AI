"""
Session 19 - Task 4: Autonomous Food Delivery Agent Simulation
==============================================================
This script simulates the 6-step end-to-end agentic workflow for an
autonomous food delivery concierge ('NutriCraver Agent' for Zomato/Swiggy):
1. Contextual Perception (Fitness + Schedule + Location)
2. Reasoning & Macro Matching (Nutritional Scoring)
3. Cart Assembly & Discount Optimization
4. Human-in-the-Loop 1-Tap Notification
5. Order Execution & Payment Dispatch
6. Real-time Telemetry & Reflection
"""

import sys
import time

# Ensure safe UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_agentic_delivery_simulation():
    print("=" * 70)
    print("   SESSION 19 - TASK 4: NUTRICRAVER FOOD DELIVERY AGENT WORKFLOW")
    print("=" * 70)

    # STEP 1: Contextual Perception
    print("\n[STEP 1: CONTEXTUAL PERCEPTION]")
    context = {
        "user_name": "Nishant",
        "workout": "45-min Morning HIIT (Burned 480 kcal)",
        "daily_target": "High Protein (30g+), Pure Vegetarian",
        "calendar_slot": "Free at 1:15 PM (Zoom meeting ends at 1:10 PM)",
        "location": "Lower Parel, Mumbai"
    }
    for k, v in context.items():
        print(f"  • {k.replace('_', ' ').title()}: {v}")

    # STEP 2: Reasoning & Macro Matching
    print("\n[STEP 2: REASONING & RESTAURANT FILTERING]")
    candidates = [
        {"dish": "Grilled Paneer Protein Bowl", "restaurant": "Green Theory", "calories": 420, "protein": "32g", "price": 450, "eta": "22 min", "match": "96%"},
        {"dish": "Veggie Deluxe Burger & Fries", "restaurant": "Burger Central", "calories": 850, "protein": "14g", "price": 380, "eta": "35 min", "match": "REJECTED (High Calorie)"},
        {"dish": "Quinoa & Edamame Salad", "restaurant": "Salad Days", "calories": 390, "protein": "28g", "price": 490, "eta": "28 min", "match": "89%"}
    ]
    for c in candidates:
        print(f"  • {c['dish']} ({c['restaurant']}) ➔ {c['calories']} kcal | {c['protein']} protein | Match: {c['match']}")
    selected = candidates[0]
    print(f"  >>> Winner Selected: '{selected['dish']}' from {selected['restaurant']}")

    # STEP 3: Cart Assembly & Customization
    print("\n[STEP 3: CART ASSEMBLY & DISCOUNT OPTIMIZATION]")
    original_price = selected["price"]
    discount = 90  # HEALTHY20 coupon
    final_price = original_price - discount
    print(f"  • Assembled Cart:  1x {selected['dish']}")
    print(f"  • Customization:   Extra grilled cottage cheese, herb dressing on side")
    print(f"  • Coupon Applied:  'HEALTHY20' (Saved Rs. {discount})")
    print(f"  • Final Bill:      Rs. {final_price} (was Rs. {original_price})")

    # STEP 4: Human-in-the-Loop Confirmation
    print("\n[STEP 4: PROACTIVE HUMAN-IN-THE-LOOP NOTIFICATION]")
    push_message = (
        f"📱 PUSH NOTIFICATION SENT TO {context['user_name'].upper()}:\n"
        f"   \"Great workout! You burned 480 kcal. To hit your protein goal, we staged\n"
        f"   a {selected['dish']} from {selected['restaurant']} for Rs. {final_price}\n"
        f"   (420 kcal, 32g Protein). Arrives at 1:15 PM when your meeting ends.\n"
        f"   [APPROVE (1-Tap)]  [SWAP MEAL]  [SKIP]\""
    )
    print(push_message)
    print("  * Simulating user action: User tapped [APPROVE (1-Tap)] *")

    # STEP 5: Order Execution & Payment Dispatch
    print("\n[STEP 5: AUTONOMOUS ORDER DISPATCH & PAYMENT]")
    print(f"  • Payment Token:   UPI AutoPay Token verified (Rs. {final_price})")
    print(f"  • Order ID:        ZOM-SWIGGY-892147")
    print(f"  • Kitchen Status:  Order transmitted to {selected['restaurant']}; prep scheduled for 12:45 PM")
    print(f"  • Target Delivery: 1:15 PM sharp at {context['location']}")

    # STEP 6: Active Telemetry & Reflection
    print("\n[STEP 6: LIVE TELEMETRY & POST-ORDER REFLECTION]")
    print("  • Rider Telemetry: Rider Ramesh K. assigned (Electric Bike, 1.2 km away)")
    print("  • Weather Check:   Clear skies, no rain delays detected")
    print("  • Status Update:   Delivered on-time at 1:14 PM!")
    print("  • Reflection Log:  User rated 5 stars; reinforced preference for grilled paneer bowls.")

    print("\n" + "=" * 70)
    print("[SUCCESS] Complete 6-Step Agentic Food Delivery Workflow verified!")
    print("=" * 70)

if __name__ == "__main__":
    run_agentic_delivery_simulation()
