# ============================================
# Task 1: Gemini API - Latest IPL Match Summary
# ============================================

import requests
import json

API_KEY = "AIzaSyCanC3VX5lkthjqA8xj2m0m8WqqcQYvkWQ"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Give me a short summary of the latest IPL cricket match in 5-6 simple lines."
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()

    summary = result["candidates"][0]["content"]["parts"][0]["text"]

    print("Latest IPL Match Summary")
    print("-" * 40)
    print(summary)

else:
    print("Error:", response.status_code)
    print(response.text)