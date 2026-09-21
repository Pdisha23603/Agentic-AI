"""
Demo: few-shot prompting as a remedy for a fine-tuned classifier's
blind spot on rare complaint categories.

Usage:
    python complaint_classifier_demo.py

Optional:
    Set ANTHROPIC_API_KEY in environment or .env file to use live Claude API.
    If no key is provided, the script runs in standalone Simulation Mode.
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

MODEL = "claude-sonnet-4-6"

# The known, well-covered categories from the original 6,000-ticket training set
COMMON_CATEGORIES = [
    "wrong_item_delivered",
    "cold_food",
    "late_delivery",
    "missing_item",
    "damaged_packaging",
]

# A handful of exemplars for rare categories the fine-tuned model never saw.
# This is the "few-shot" fix: instead of retraining, we show the live model
# a couple of labeled examples for the underrepresented classes.
FEW_SHOT_EXAMPLES = """
Example 1:
Ticket: "The delivery partner made dismissive comments about my religious attire while I was fasting for a festival."
Category: conduct_cultural_insensitivity

Example 2:
Ticket: "Rider refused to wait 2 extra minutes even though I explained I was mid-prayer."
Category: conduct_cultural_insensitivity

Example 3:
Ticket: "Driver was polite but the delivery arrived 40 minutes late during dinner."
Category: late_delivery
"""

TICKET_TO_CLASSIFY = (
    "Delivery partner was rude and impatient during a religious event I was "
    "observing at home, made a sarcastic remark about the delay it caused him."
)


def classify_simulated(ticket: str, use_few_shot: bool) -> str:
    """Deterministic simulation mimicking LLM behavior with and without few-shot examples."""
    if use_few_shot:
        # In few-shot mode, the model identifies cultural/religious insensitivity from exemplars
        return "conduct_cultural_insensitivity"
    else:
        # In baseline mode, the model is constrained to the 5 known categories.
        # It latches onto the mention of "delay" and erroneously classifies as late_delivery.
        return "late_delivery (Misclassified: forced into common categories)"


def classify(ticket: str, use_few_shot: bool) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    is_real_key = api_key and not api_key.startswith("sk-ant-...") and len(api_key) > 20

    if not HAS_ANTHROPIC or not is_real_key:
        return classify_simulated(ticket, use_few_shot)

    client = anthropic.Anthropic(api_key=api_key)

    if use_few_shot:
        system_prompt = (
            "You are a complaint classifier for a food delivery company. "
            "Classify the ticket into the single best category. Known common "
            f"categories: {', '.join(COMMON_CATEGORIES)}. There are also rarer "
            "categories not in that list -- infer a sensible category name if "
            "none of the common ones fit, using the examples below as a guide.\n"
            f"{FEW_SHOT_EXAMPLES}\n"
            "Respond with only the category name, nothing else."
        )
    else:
        system_prompt = (
            "You are a complaint classifier for a food delivery company. "
            "Classify the ticket into the single best category from this list "
            f"only: {', '.join(COMMON_CATEGORIES)}. Respond with only the "
            "category name, nothing else."
        )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=20,
            system=system_prompt,
            messages=[{"role": "user", "content": ticket}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[Notice: API call failed ({e}). Falling back to simulation.]")
        return classify_simulated(ticket, use_few_shot)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    is_real_key = bool(api_key and not api_key.startswith("sk-ant-...") and len(api_key) > 20)

    print("=" * 70)
    print("COMPLAINT CLASSIFIER DEMO: FEW-SHOT REMEDY FOR RARE CATEGORIES")
    print("=" * 70)
    print(f"Mode: {'Live API (Claude)' if is_real_key else 'Simulation Mode (Offline / No API Key required)'}")
    print("=" * 70)
    print("\n[Input Ticket]:")
    print(f'"{TICKET_TO_CLASSIFY}"\n')

    print("-" * 70)
    print("1. Baseline (mimics fine-tuned model with fixed 5-class vocabulary):")
    print("   ->", classify(TICKET_TO_CLASSIFY, use_few_shot=False))
    print("   [Why: Model forces rare issue into existing bucket 'late_delivery' due to mention of delay]")

    print("\n2. Few-shot Prompted (remedy for rare-category blind spot):")
    print("   ->", classify(TICKET_TO_CLASSIFY, use_few_shot=True))
    print("   [Why: Exemplars guide model to identify the novel 'conduct_cultural_insensitivity' class]")
    print("=" * 70)


if __name__ == "__main__":
    main()

