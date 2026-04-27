import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_recipe_with_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text
