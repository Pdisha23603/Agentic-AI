# ---------------------------------------------
# TASK 1 : Flipkart Review Summarizer
# ---------------------------------------------

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

review = """
I bought this Samsung Galaxy phone from Flipkart.
The display quality is amazing, battery backup lasts almost two days,
and the camera is excellent in daylight. However, the charger was not included,
and the phone gets slightly warm while gaming.
"""

prompt = f"""
Summarize the following Flipkart review in 3 short bullet points.

Review:
{review}
"""

response = llm.invoke([HumanMessage(content=prompt)])

print("="*60)
print("ORIGINAL REVIEW")
print("="*60)
print(review)

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(response.content)