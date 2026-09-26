# ============================================
# Task 2: Sentiment Analysis using Transformers
# ============================================

from transformers import pipeline

# Load sentiment analysis model
sentiment = pipeline("sentiment-analysis")

# Sample Zomato Reviews
reviews = [
    "The pizza was delicious and arrived hot.",
    "Food quality was terrible and delivery was very late.",
    "The restaurant was okay. Nothing special.",
    "Amazing burger! I loved the taste and service.",
    "I am disappointed because my order was cold."
]

print("Zomato Review Sentiment Analysis")
print("-" * 45)

for i, review in enumerate(reviews, start=1):
    result = sentiment(review)[0]

    label = result["label"]

    # Convert model labels into Positive / Negative / Neutral
    if label == "POSITIVE":
        sentiment_result = "Positive"
    elif label == "NEGATIVE":
        sentiment_result = "Negative"
    else:
        sentiment_result = "Neutral"

    print(f"\nReview {i}")
    print("Text      :", review)
    print("Sentiment :", sentiment_result)