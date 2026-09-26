# ============================================
# Task 5: LangChain Calculator Agent
# File: calculator_agent.py
# ============================================

from langchain.tools import Tool

# Calculator function
def calculator(expression: str):
    try:
        return str(eval(expression))
    except Exception:
        return "Invalid calculation."


# Create calculator tool
calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Performs basic mathematical calculations."
)

print("====== Calculator Agent ======")

question = input("Enter a math question: ")

# Extract expression from sentence
expression = (
    question.lower()
    .replace("what is", "")
    .replace("?", "")
    .replace("times", "*")
    .replace("plus", "+")
    .replace("minus", "-")
    .replace("divided by", "/")
    .strip()
)

answer = calculator_tool.run(expression)

print("Agent Answer:", answer)