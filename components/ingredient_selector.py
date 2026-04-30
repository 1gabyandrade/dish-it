import streamlit as st

from data.ingredients import INGREDIENTS


def ingredient_selector():
    if "selected_ingredients" not in st.session_state:
        st.session_state.selected_ingredients = []

    selected_ingredients = st.multiselect(
        "Ingredients",
        options=INGREDIENTS,
        default=st.session_state.selected_ingredients,
        placeholder="What do you have today?",
        key="ingredient_multiselect",
        label_visibility="collapsed",
    )

    st.session_state.selected_ingredients = selected_ingredients

    return selected_ingredients
