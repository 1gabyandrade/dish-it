import streamlit as st

from data.ingredients import INGREDIENTS


def ingredient_selector():
    if "selected_ingredients" not in st.session_state:
        st.session_state.selected_ingredients = []

    selected_ingredients = st.multiselect(
        "What do you have today?",
        options=INGREDIENTS,
        default=st.session_state.selected_ingredients,
        placeholder="Type at least 2 letters, e.g. ch",
        key="ingredient_multiselect",
    )

    st.session_state.selected_ingredients = selected_ingredients

    return selected_ingredients
