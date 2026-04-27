# Dish-It

Dish-It is a Streamlit MVP for turning available ingredients into a quick recipe.

The project goal is simple: help students and young professionals waste less food,
spend less money, and decide what to cook faster.

## MVP Plan

1. Let the user enter/select ingredients.
2. Suggest ingredients from a predefined autocomplete list.
3. Generate a structured recipe.
4. Use Gemini when an API key is available.
5. Use a mock recipe when no API key is available.
6. Optionally save generated recipes with SQLite.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```
