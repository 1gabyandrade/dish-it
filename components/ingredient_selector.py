import time

import streamlit as st
from streamlit_searchbox import st_searchbox

from data.ingredients import INGREDIENTS

SEARCHBOX_KEY = "ingredient_searchbox"
SUGGESTION_LIMIT = 8


def keep_empty_searchbox_closed():
    searchbox_state = st.session_state.get(SEARCHBOX_KEY)

    if searchbox_state is None:
        st.session_state[SEARCHBOX_KEY] = {
            "result": None,
            "search": "",
            "options_js": None,
            "key_react": f"{SEARCHBOX_KEY}_react_{time.time()}",
        }
        return

    if not searchbox_state.get("search"):
        searchbox_state["options_js"] = None
        searchbox_state.pop("options_py", None)


def search_ingredients(searchterm):
    query = searchterm.strip().lower()

    if not query:
        return []

    selected = set(st.session_state.get("selected_ingredients", []))

    matches = [
        ingredient
        for ingredient in INGREDIENTS
        if ingredient not in selected and query in ingredient.lower()
    ]

    exact_matches = [
        ingredient for ingredient in matches if ingredient.lower() == query
    ]

    starts_with_matches = [
        ingredient for ingredient in matches if ingredient.lower().startswith(query)
    ]

    contains_matches = [
        ingredient for ingredient in matches if not ingredient.lower().startswith(query)
    ]

    ordered_matches = (
        exact_matches
        + [
            ingredient
            for ingredient in starts_with_matches
            if ingredient not in exact_matches
        ]
        + contains_matches
    )

    return ordered_matches[:SUGGESTION_LIMIT]


def add_ingredient(ingredient):
    if ingredient not in INGREDIENTS:
        return

    selected = st.session_state.setdefault("selected_ingredients", [])

    if ingredient not in selected:
        selected.append(ingredient)

    if SEARCHBOX_KEY in st.session_state:
        st.session_state[SEARCHBOX_KEY]["result"] = None
        st.session_state[SEARCHBOX_KEY]["search"] = ""
        st.session_state[SEARCHBOX_KEY]["options_js"] = None
        st.session_state[SEARCHBOX_KEY].pop("options_py", None)


def remove_ingredient(ingredient):
    st.session_state.selected_ingredients = [
        selected
        for selected in st.session_state.selected_ingredients
        if selected != ingredient
    ]


def ingredient_selector():
    if "selected_ingredients" not in st.session_state:
        st.session_state.selected_ingredients = []

    keep_empty_searchbox_closed()

    st_searchbox(
        search_ingredients,
        placeholder="What do you have today?",
        label=None,
        clear_on_submit=True,
        edit_after_submit="disabled",
        submit_function=add_ingredient,
        style_overrides={
            "wrapper": {
                "backgroundColor": "#3f7f4f",
                "margin": "0",
                "padding": "0",
                "border": "0",
            },
            "clear": {"clearable": "never"},
            "dropdown": {
                "rotate": False,
                "fill": "#82301a",
            },
            "searchbox": {
                "optionEmpty": "hidden",
                "control": {
                    "backgroundColor": "#fff5ec",
                    "border": "2px solid #ffc933",
                    "borderRadius": "999px",
                    "boxShadow": "none",
                    "minHeight": "44px",
                },
                "root": {
                    "backgroundColor": "#3f7f4f",
                },
                "input": {
                    "color": "#82301a",
                },
                "placeholder": {
                    "color": "#82301a",
                },
                "singleValue": {
                    "display": "none",
                },
                "menu": {
                    "backgroundColor": "transparent",
                    "boxShadow": "none",
                    "marginTop": "0px",
                    "padding": "0",
                    "border": "0",
                },
                "menuList": {
                    "backgroundColor": "#fff5ec",
                    "border": "2px solid #ffc933",
                    "borderRadius": "18px",
                    "maxHeight": "220px",
                    "marginTop": "-14px",
                    "padding": "26px 8px 8px",
                },
                "menuPortal": {
                    "backgroundColor": "#3f7f4f",
                },
                "container": {
                    "backgroundColor": "#3f7f4f",
                },
                "option": {
                    "color": "#82301a",
                    "backgroundColor": "#fff5ec",
                    "highlightColor": "#ffc933",
                    "padding": "6px 10px",
                },
            },
        },
        key=SEARCHBOX_KEY,
    )

    selected_ingredients = st.session_state.selected_ingredients

    if selected_ingredients:
        with st.container(key="ingredient_tags", horizontal=True, gap="small"):
            for ingredient in selected_ingredients:
                st.button(
                    ingredient,
                    key=f"remove_ingredient_{ingredient}",
                    help=f"Remove {ingredient}",
                    on_click=remove_ingredient,
                    args=(ingredient,),
                    width="content",
                )

    return selected_ingredients
