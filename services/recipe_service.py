from utils.prompts import build_recipe_prompt


def generate_mock_recipe(ingredients):
    ingredients_text = ", ".join(ingredients)

    return f"""
### Quick Student Meal
**Cooking time:** 15 minutes

**Ingredients used:**
{ingredients_text}

**Instructions:**
1. Prepare all ingredients.
2. Heat a pan with a little oil or butter.
3. Add the main ingredients and cook for a few minutes.
4. Season with salt, pepper, or any spices you have.
5. Serve warm and enjoy.

**Dish-It tip:** This is a mock recipe for testing.
"""


def get_recipe(ingredients):
    build_recipe_prompt(ingredients)
    return generate_mock_recipe(ingredients)
