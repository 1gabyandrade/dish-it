def build_recipe_prompt(ingredients):
    ingredients_text = ", ".join(ingredients)

    return f"""
You are Dish-It, a helpful cooking assistant for students and young professionals.

Create one quick, simple recipe using these ingredients:
{ingredients_text}

Return the recipe with:
- Title
- Cooking time
- Ingredients used
- Step-by-step instructions

Keep the recipe affordable, realistic, and beginner-friendly.
"""
