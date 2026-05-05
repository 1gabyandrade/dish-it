import json


def normalize_ingredient(ingredient):
    return str(ingredient).strip().lower()


def normalize_ingredients(ingredients):
    normalized_ingredients = []
    seen_ingredients = set()

    for ingredient in ingredients or []:
        normalized = normalize_ingredient(ingredient)

        if not normalized or normalized in seen_ingredients:
            continue

        normalized_ingredients.append(normalized)
        seen_ingredients.add(normalized)

    return normalized_ingredients


def encode_ingredients(ingredients):
    return json.dumps(normalize_ingredients(ingredients))


def decode_ingredients(ingredients):
    if not ingredients:
        return []

    try:
        decoded = json.loads(ingredients)
    except json.JSONDecodeError:
        return []

    if not isinstance(decoded, list):
        return []

    return normalize_ingredients(decoded)


def rows_to_recipe_dicts(rows):
    recipes = []

    for row in rows:
        recipe = dict(row)
        recipe["ingredients"] = decode_ingredients(recipe["ingredients"])
        recipes.append(recipe)

    return recipes
