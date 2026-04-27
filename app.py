from venv import logger

import streamlit as st

from components.ingredient_selector import ingredient_selector
from services.recipe_service import get_recipe


def load_css():
    with open("assets/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

st.set_page_config(page_title="Dish-It", page_icon="🍳")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# -----------------------------
# LOGIN PAGE
# -----------------------------
def show_login():
    st.title("🍳 Dish-It")

    st.subheader("Log In")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username and password:
            # Fake login for MVP
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.rerun()  # reload app to switch page
        else:
            st.warning("Please enter both username and password.")

    st.write("New here? ")
    st.button("Sign Up")

    st.caption("Forgot your password? Click here")


# -----------------------------
# MAIN APP PAGE
# -----------------------------
def show_main_app():
    st.title(f"Welcome, {st.session_state.username}")

    st.write("What do you have today?")

    selected_ingredients = ingredient_selector()

    if st.button("Generate Recipe"):
        if not selected_ingredients:
            st.warning("Please select at least one ingredient.")
        else:
            recipe = get_recipe(selected_ingredients)
            st.markdown(recipe)


# -----------------------------
# ROUTING LOGIC
# -----------------------------
if not st.session_state.logged_in:
    show_login()
else:
    show_main_app()
