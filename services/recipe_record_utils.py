import json


def encode_ingredients(ingredients):
    return json.dumps(list(ingredients or []))


def decode_ingredients(ingredients):
    if not ingredients:
        return []

    try:
        decoded = json.loads(ingredients)
    except json.JSONDecodeError:
        return []

    return decoded if isinstance(decoded, list) else []


def rows_to_recipe_dicts(rows):
    recipes = []

    for row in rows:
        recipe = dict(row)
        recipe["ingredients"] = decode_ingredients(recipe["ingredients"])
        recipes.append(recipe)

    return recipes
