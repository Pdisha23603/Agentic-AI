# ---------------------------------------------
# TASK 2 : IPL Captain Chatbot
# ---------------------------------------------

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

ipl_info = {
    "Mumbai Indians": "Hardik Pandya",
    "Chennai Super Kings": "Ruturaj Gaikwad",
    "Royal Challengers Bengaluru": "Rajat Patidar",
    "Kolkata Knight Riders": "Ajinkya Rahane",
    "Gujarat Titans": "Shubman Gill",
    "Rajasthan Royals": "Sanju Samson",
    "Delhi Capitals": "Axar Patel",
    "Punjab Kings": "Shreyas Iyer",
    "Lucknow Super Giants": "Rishabh Pant",
    "Sunrisers Hyderabad": "Pat Cummins"
}

print("="*50)
print("IPL Captain Assistant")
print("="*50)

while True:

    question = input("\nAsk your IPL question (type exit): ")

    if question.lower() == "exit":
        print("Thank You!")
        break

    prompt = f"""
You are an IPL assistant.

Use ONLY the information below.

{ipl_info}

Answer this question:

{question}
"""

    answer = llm.invoke([HumanMessage(content=prompt)])

    print("\nAssistant:", answer.content)