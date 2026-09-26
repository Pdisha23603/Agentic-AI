# ============================================
# Task 3: WhatsApp Urgent Message Agent
# ============================================

messages = [
    "Hi, how are you?",
    "Meeting starts at 10 AM.",
    "Please call me urgently.",
    "URGENT: Your order has been delayed.",
    "See you tomorrow."
]

urgent_found = False

for message in messages:
    if "urgent" in message.lower():
        urgent_found = True
        break

if urgent_found:
    print("Alert: Urgent message received!")
else:
    print("No urgent messages.")