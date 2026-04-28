import base64

import streamlit as st

from components.ingredient_selector import ingredient_selector
from services.recipe_service import get_recipe

st.set_page_config(page_title="Dish-It", page_icon="🍳")


def load_css():
    with open("assets/styles.css") as f:
        css = f.read()

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Passion+One:wght@700&display=swap');
        {css}
        </style>
        """,
        unsafe_allow_html=True,
    )


load_css()


def set_login_background():
    with open("assets/header.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
              url("data:image/png;base64,{encoded}") top center / 100% auto no-repeat,
              #fff5ec;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_main_background():
    with open("assets/background.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "has_generated" not in st.session_state:
    st.session_state.has_generated = False

if "generated_recipe" not in st.session_state:
    st.session_state.generated_recipe = ""


# -----------------------------
# LOGIN PAGE
# -----------------------------
def show_login():
    with st.container(key="login_card"):
        st.markdown(
            """
            <div class="title-wrapper">
                <h1 class="dish-title">DISH-IT</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        btn_left, btn_center, btn_right = st.columns([1, 1, 1])

        with btn_center:
            login_clicked = st.button("LOG IN")

        if login_clicked:
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.has_generated = False
                st.session_state.generated_recipe = ""
                st.rerun()
            else:
                st.warning("Please enter username and password.")

        st.markdown(
            '<p class="forgot">Forgot your password? <u>Click here</u></p>',
            unsafe_allow_html=True,
        )

        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        st.markdown('<p class="new-here">New here?</p>', unsafe_allow_html=True)

        signup_left, signup_center, signup_right = st.columns([1, 1, 1])

        with signup_center:
            sign_in_clicked = st.button("SIGN IN")

        if sign_in_clicked:
            st.info("Sign up page coming soon.")


# -----------------------------
# MAIN APP PAGE
# -----------------------------
def show_main_app():
    st.markdown(
        """
        <div class="navbar">
            <span class="logo">DISH-IT</span>
            <span class="menu">Home | My Recipes | My Pantry | History</span>
            <span class="account">My Account | Log Out</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="main_card"):
        if st.session_state.has_generated:
            title_text = f"Here are your recipes, @{st.session_state.username}!"
        else:
            title_text = f"Welcome back, @{st.session_state.username}"

        st.markdown(
            f"<h1 class='main-title'>{title_text}</h1>",
            unsafe_allow_html=True,
        )

        selected_ingredients = ingredient_selector()

        if st.button("Generate Recipe"):
            if not selected_ingredients:
                st.warning("Please select at least one ingredient.")
            else:
                recipe = get_recipe(selected_ingredients)
                st.session_state.generated_recipe = recipe
                st.session_state.has_generated = True
                st.rerun()

        if st.session_state.has_generated and st.session_state.generated_recipe:
            st.markdown(st.session_state.generated_recipe)


# -----------------------------
# ROUTING LOGIC
# -----------------------------
if not st.session_state.logged_in:
    set_login_background()
    show_login()
else:
    set_main_background()
    show_main_app()
