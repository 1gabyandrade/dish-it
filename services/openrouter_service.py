import os

import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_recipe_with_openrouter(prompt: str):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt},
            ],
        },
    )

    data = response.json()

    # 🔥 DEBUG (very important)
    if "choices" not in data:
        print("OpenRouter error:", data)
        return None

    return data["choices"][0]["message"]["content"]
