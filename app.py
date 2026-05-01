import base64

import streamlit as st

from components.ingredient_selector import ingredient_selector
from database.db import init_db
from services.auth_service import authenticate_user, create_user
from services.recipe_service import get_recipe

st.set_page_config(page_title="Dish-It", page_icon="🍳", layout="wide")


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


def set_login_background():
    with open("assets/header.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            --login-header-height: clamp(190px, 18.4vw, 470px);
            background: #fff5ec;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--login-header-height);
            background: url("data:image/png;base64,{encoded}") top center / 100% auto no-repeat;
            pointer-events: none;
            z-index: 0;
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


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    if "has_generated" not in st.session_state:
        st.session_state.has_generated = False

    if "generated_recipe" not in st.session_state:
        st.session_state.generated_recipe = ""


def logout():
    for key in ("user_id", "username", "email"):
        st.session_state.pop(key, None)

    st.session_state.logged_in = False
    st.session_state.auth_mode = "login"
    st.session_state.has_generated = False
    st.session_state.generated_recipe = ""
    st.rerun()


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

        if st.session_state.auth_mode == "login":
            login_identifier = st.text_input("Username")
            password = st.text_input("Password", type="password")

            _, btn_center, _ = st.columns([1, 1, 1])

            with btn_center:
                login_clicked = st.button("LOG IN", key="login_btn")

            if login_clicked:
                if not login_identifier or not password:
                    st.warning("Please enter your username/email and password.")
                else:
                    success, user_data, message = authenticate_user(
                        login_identifier,
                        password,
                    )

                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_data["id"]
                        st.session_state.username = user_data["username"]
                        st.session_state.email = user_data["email"]
                        st.session_state.has_generated = False
                        st.session_state.generated_recipe = ""
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown(
                '<p class="forgot">Forgot your password? <u>Click here</u></p>',
                unsafe_allow_html=True,
            )

            st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
            st.markdown('<p class="new-here">New here?</p>', unsafe_allow_html=True)

            _, signup_center, _ = st.columns([1, 1, 1])

            with signup_center:
                sign_in_clicked = st.button("SIGN IN", key="signup_btn")

            if sign_in_clicked:
                st.session_state.auth_mode = "signup"
                st.rerun()

        else:
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            _, btn_center, _ = st.columns([1, 1, 1])

            with btn_center:
                create_clicked = st.button("CREATE", key="create_btn")

            if create_clicked:
                if not username or not email or not password or not confirm_password:
                    st.warning("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = create_user(username, email, password)

                    if success:
                        st.success("Account created. Please log in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
            st.markdown(
                '<p class="new-here">Already have an account?</p>',
                unsafe_allow_html=True,
            )

            _, back_center, _ = st.columns([1, 1, 1])

            with back_center:
                back_clicked = st.button("BACK", key="back_btn")

            if back_clicked:
                st.session_state.auth_mode = "login"
                st.rerun()


def show_main_app():
    with st.container(key="nav_bar"):
        st.markdown(
            """
            <div class="navbar">
                <div class="logo">DISH-IT</div>
                <div class="menu" aria-label="Primary navigation">
                    <span>Home</span>
                    <span class="nav-separator">|</span>
                    <span>My Recipes</span>
                    <span class="nav-separator">|</span>
                    <span>My Pantry</span>
                    <span class="nav-separator">|</span>
                    <span>History</span>
                </div>
                <div class="account">
                    My Account <span class="nav-separator">|</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Log Out", key="logout_btn"):
            logout()

    with st.container(key="main_card"):
        if st.session_state.has_generated:
            title_text = f"Here are your recipes, @{st.session_state.username}!"
        else:
            title_text = f"Welcome back, @{st.session_state.username}"

        st.markdown(
            f"<h1 class='main-title'>{title_text}</h1>",
            unsafe_allow_html=True,
        )

        input_col, button_col = st.columns(
            [5, 1.4], gap="small", vertical_alignment="top"
        )
        with input_col:
            selected_ingredients = ingredient_selector()

        with button_col:
            with st.container(key="generate_action"):
                generate_clicked = st.button(
                    "Generate Recipe",
                    key="generate_recipe_btn",
                )

        if generate_clicked:
            if not selected_ingredients:
                st.warning("Please select at least one ingredient.")
            else:
                recipe = get_recipe(selected_ingredients)
                st.session_state.generated_recipe = recipe
                st.session_state.has_generated = True
                st.rerun()

        if st.session_state.has_generated and st.session_state.generated_recipe:
            with st.container(key="recipe_output"):
                st.markdown(st.session_state.generated_recipe)


load_css()
init_db()
init_session_state()

if not st.session_state.logged_in:
    set_login_background()
    show_login()
else:
    set_main_background()
    show_main_app()
