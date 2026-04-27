import json


def load_ingredients():
    with open("data/ingredients.json", "r") as file:
        return json.load(file)


INGREDIENTS = load_ingredients()
