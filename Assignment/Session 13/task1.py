# ============================================
# Task 1: Multi-Modal Agent
# ============================================

import os


def multimodal_agent(text_prompt, image_path):
    """
    Receives a text prompt and an image file path.
    """

    print("========== Multi-Modal AI Agent ==========")

    print("Text Prompt Received:")
    print(text_prompt)

    print()

    if os.path.exists(image_path):
        image_name = os.path.basename(image_path)
        print("Image Received Successfully!")
        print("Image Filename:", image_name)
    else:
        print("Image file not found.")


# Example
multimodal_agent(
    "Show me restaurants near Ahmedabad.",
    "restaurant.jpg"
)