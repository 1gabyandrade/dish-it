from services.openrouter_service import generate_recipe_with_openrouter
from utils.prompts import build_recipe_prompt

NO_RECIPE_FOUND = "NO_RECIPE_FOUND"


def get_recipe(ingredients):
    if len(ingredients) < 2:
        return """
### Add more ingredients 👀

Please add at least **2 ingredients** so I can create a better recipe for you.
"""

    prompt = build_recipe_prompt(ingredients)
    result = generate_recipe_with_openrouter(prompt)

    # API error
    if not result["success"]:
        return generate_api_error_message()

    recipe = result["recipe"]

    # Valid recipe
    if recipe and NO_RECIPE_FOUND not in recipe:
        return recipe

    # No recipe found
    return generate_no_recipe_message(ingredients)


def generate_api_error_message():
    return """
### Recipe service is unavailable 🚧

Something went wrong while generating your recipe.

Please try again in a moment.
"""


def generate_no_recipe_message(ingredients):
    ingredients_text = ", ".join(ingredients)

    return f"""
### Hmm… I couldn’t find a good recipe 😅

I couldn’t create a realistic recipe using only:

**{ingredients_text}**

Try adding one or two more ingredients, or swapping one of them.
"""
