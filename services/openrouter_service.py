import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_recipe_with_openrouter(prompt: str):
    if not OPENROUTER_API_KEY:
        return {"success": False, "error": "missing_api_key"}

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful cooking assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=45,
        )

        data = response.json()

    except requests.RequestException as e:
        logging.error(f"OpenRouter request failed: {e}")
        return {"success": False, "error": "request_failed"}

    if "choices" not in data:
        logging.error(f"Invalid OpenRouter response: {data}")
        return {"success": False, "error": "invalid_response"}

    return {
        "success": True,
        "recipe": data["choices"][0]["message"]["content"],
    }
