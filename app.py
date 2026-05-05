import base64
import logging
import secrets
import sqlite3
import time
from html import escape

import streamlit as st

from components.ingredient_selector import ingredient_selector
from database.db import get_connection, init_db
from services.auth_service import (
    authenticate_user,
    create_user,
    delete_user_account,
    update_user_account,
)
from services.favorite_service import (
    add_favorite_recipe,
    get_favorite_recipe_id,
    get_favorite_recipes,
    remove_favorite_recipe,
)
from services.history_service import add_recipe_history, get_recipe_history
from services.recipe_service import get_recipe

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

st.set_page_config(page_title="Dish-It", page_icon="🍳", layout="wide")

NAV_ITEMS = (
    ("home", "Home"),
    ("my_recipes", "My Recipes"),
    ("my_pantry", "My Pantry"),
    ("history", "History"),
)

SESSION_DEFAULTS = {
    "logged_in": False,
    "auth_mode": "login",
    "has_generated": False,
    "generated_recipe": "",
    "generated_recipe_ingredients": [],
    "favorite_notice": "",
    "confirm_delete_account": False,
    "current_page": "home",
    "last_recipe_request_time": 0,
}

INVALID_RECIPE_PHRASES = (
    "add more ingredients",
    "couldn't find a good recipe",
    "couldn’t find a good recipe",
)


@st.cache_resource
def get_auth_sessions():
    return {}


def get_auth_token_from_url():
    try:
        return st.query_params.get("auth")
    except AttributeError:
        value = st.experimental_get_query_params().get("auth")
        return value[0] if isinstance(value, list) and value else value


def set_auth_token_in_url(token):
    try:
        st.query_params["auth"] = token
    except AttributeError:
        st.experimental_set_query_params(auth=token)


def clear_auth_token_from_url():
    try:
        if "auth" in st.query_params:
            del st.query_params["auth"]
    except AttributeError:
        params = st.experimental_get_query_params()
        params.pop("auth", None)
        st.experimental_set_query_params(**params)


def get_current_page():
    return st.session_state.get("current_page", "home")


def set_current_page(page_name):
    st.session_state.current_page = page_name
    st.session_state.confirm_delete_account = False


def set_authenticated_user(user_data, auth_token=None):
    st.session_state.logged_in = True
    st.session_state.user_id = user_data["id"]
    st.session_state.username = user_data["username"]
    st.session_state.email = user_data["email"]

    if auth_token:
        st.session_state.auth_token = auth_token


def start_auth_session(user_data):
    old_token = st.session_state.get("auth_token") or get_auth_token_from_url()

    if old_token:
        get_auth_sessions().pop(old_token, None)

    auth_token = secrets.token_urlsafe(32)
    get_auth_sessions()[auth_token] = user_data.copy()

    set_authenticated_user(user_data, auth_token)
    set_auth_token_in_url(auth_token)
    st.session_state.current_page = "home"


def restore_auth_session():
    if st.session_state.logged_in:
        return

    auth_token = st.session_state.get("auth_token") or get_auth_token_from_url()

    if not auth_token:
        return

    user_data = get_auth_sessions().get(auth_token)

    if not user_data:
        st.session_state.pop("auth_token", None)
        clear_auth_token_from_url()
        return

    set_authenticated_user(user_data, auth_token)


def update_stored_auth_session(user_data):
    auth_token = st.session_state.get("auth_token") or get_auth_token_from_url()

    if auth_token:
        get_auth_sessions()[auth_token] = user_data.copy()


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
            background:
                url("data:image/png;base64,{encoded}")
                top center / 100% auto no-repeat;
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
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            if isinstance(value, list):
                st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value
    restore_auth_session()


def reset_recipe_state():
    st.session_state.has_generated = False
    st.session_state.generated_recipe = ""
    st.session_state.generated_recipe_ingredients = []
    st.session_state.favorite_notice = ""


def logout():
    auth_token = st.session_state.get("auth_token") or get_auth_token_from_url()

    if auth_token:
        get_auth_sessions().pop(auth_token, None)

    for key in ("user_id", "username", "email", "auth_token"):
        st.session_state.pop(key, None)

    clear_auth_token_from_url()

    st.session_state.logged_in = False
    st.session_state.auth_mode = "login"
    st.session_state.confirm_delete_account = False
    st.session_state.current_page = "home"

    reset_recipe_state()
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
                        start_auth_session(user_data)
                        reset_recipe_state()
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
            st.markdown('<p class="new-here">New here?</p>', unsafe_allow_html=True)

            _, signup_center, _ = st.columns([1, 1, 1])

            with signup_center:
                sign_up_clicked = st.button("SIGN UP", key="signup_btn")

            if sign_up_clicked:
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


def show_nav_bar(active_page=None):
    with st.container(key="nav_bar"):
        with st.container(key="nav_logo"):
            st.markdown('<div class="logo">DISH-IT</div>', unsafe_allow_html=True)

        with st.container(
            key="nav_menu_actions",
            horizontal=True,
            vertical_alignment="center",
            gap="small",
        ):
            for index, (page_name, label) in enumerate(NAV_ITEMS):
                st.button(
                    label,
                    key=f"nav_{page_name}_btn",
                    on_click=set_current_page,
                    args=(page_name,),
                )

                if index < len(NAV_ITEMS) - 1:
                    st.markdown(
                        '<span class="nav-separator">|</span>',
                        unsafe_allow_html=True,
                    )

        with st.container(
            key="nav_right_actions",
            horizontal=True,
            vertical_alignment="center",
            gap="small",
        ):
            st.button(
                "My Account",
                key="nav_my_account_btn",
                on_click=set_current_page,
                args=("my_account",),
            )

            st.markdown(
                '<span class="nav-separator small">|</span>',
                unsafe_allow_html=True,
            )

            if st.button("Log Out", key="logout_btn"):
                logout()

        active_button_key = (
            "nav_my_account_btn"
            if active_page == "my_account"
            else f"nav_{active_page}_btn"
        )

        st.markdown(
            f"""
            <style>
            .st-key-{active_button_key} button p {{
                text-decoration: underline !important;
                text-underline-offset: 4px !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


def get_recipe_title(recipe_text):
    title, _ = split_recipe_title_and_body(recipe_text)
    return title or "Saved Recipe"


def split_recipe_title_and_body(recipe_text):
    lines = recipe_text.splitlines()

    for index, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line.startswith("#"):
            title = stripped_line.lstrip("#").strip()

            if title:
                body = "\n".join(lines[index + 1 :]).strip()
                return title[:120], body

    return "", recipe_text


def show_favorite_notice():
    if not st.session_state.favorite_notice:
        return

    st.success(st.session_state.favorite_notice)
    st.session_state.favorite_notice = ""


def is_favoriteable_recipe(recipe_text):
    lower_recipe = recipe_text.lower()
    return not any(phrase in lower_recipe for phrase in INVALID_RECIPE_PHRASES)


def show_generated_recipe_favorite_action():
    recipe_text = st.session_state.generated_recipe
    user_id = st.session_state.user_id
    favorite_recipe_id = get_favorite_recipe_id(user_id, recipe_text)
    is_favorited = favorite_recipe_id is not None

    with st.container(key="favorite_recipe_action"):
        favorite_clicked = st.button(
            "Add to My Recipes",
            key="favorite_recipe_btn",
            disabled=is_favorited,
        )

    if not favorite_clicked:
        return

    was_added = add_favorite_recipe(
        user_id,
        get_recipe_title(recipe_text),
        recipe_text,
        st.session_state.generated_recipe_ingredients,
    )
    st.session_state.favorite_notice = (
        "Recipe saved to My Recipes."
        if was_added
        else "This recipe is already in My Recipes."
    )

    st.rerun()


def show_generated_recipe():
    recipe_text = st.session_state.generated_recipe
    title, body = split_recipe_title_and_body(recipe_text)

    if not is_favoriteable_recipe(recipe_text):
        st.markdown(recipe_text)
        return

    if not title:
        show_generated_recipe_favorite_action()
        st.markdown(recipe_text)
        return

    title_col, favorite_col = st.columns(
        [0.76, 0.24],
        gap="small",
        vertical_alignment="center",
    )

    with title_col:
        st.markdown(
            f"<h2 class='generated-recipe-title'>{escape(title)}</h2>",
            unsafe_allow_html=True,
        )

    with favorite_col:
        show_generated_recipe_favorite_action()

    if body:
        st.markdown(body)


def format_ingredients(ingredients):
    return ", ".join(str(ingredient) for ingredient in ingredients)


def show_recipe_body_without_title(recipe_text):
    _, body = split_recipe_title_and_body(recipe_text)
    st.markdown(body or recipe_text)


def show_page_title(title):
    st.markdown(
        f"<h1 class='main-title'>{escape(title)}</h1>",
        unsafe_allow_html=True,
    )


def show_empty_state(message):
    st.markdown(
        f"<p class='empty-state'>{escape(message)}</p>",
        unsafe_allow_html=True,
    )


def show_recipe_heading(title):
    st.markdown(
        f"<h2 class='favorite-card-title'>{escape(title)}</h2>",
        unsafe_allow_html=True,
    )


def show_recipe_meta(meta_items):
    if not meta_items:
        return

    st.markdown(
        f"<p class='favorite-meta'>{escape(' | '.join(meta_items))}</p>",
        unsafe_allow_html=True,
    )


def show_main_app():
    show_nav_bar(active_page="home")

    with st.container(key="main_card"):
        if st.session_state.has_generated:
            title_text = f"Here are your recipes, @{st.session_state.username}!"
        else:
            title_text = f"Welcome back, @{st.session_state.username}"

        show_page_title(title_text)

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
            selected_ingredients = selected_ingredients or []

            current_time = time.time()
            seconds_since_last_request = (
                current_time - st.session_state.last_recipe_request_time
            )

            if seconds_since_last_request < 5:
                st.warning(
                    "Please wait a few seconds before generating another recipe."
                )
            elif len(selected_ingredients) < 2:
                st.warning("Please select at least two ingredients.")
            else:
                st.session_state.last_recipe_request_time = current_time

                recipe = get_recipe(selected_ingredients)
                st.session_state.generated_recipe = recipe
                st.session_state.generated_recipe_ingredients = list(
                    selected_ingredients
                )

                if is_favoriteable_recipe(recipe):
                    add_recipe_history(
                        st.session_state.user_id,
                        get_recipe_title(recipe),
                        recipe,
                        selected_ingredients,
                    )

                st.session_state.has_generated = True
                st.rerun()

        if st.session_state.has_generated and st.session_state.generated_recipe:
            with st.container(key="recipe_output"):
                show_favorite_notice()
                show_generated_recipe()


def show_my_recipes_page():
    show_nav_bar(active_page="my_recipes")

    with st.container(key="main_card"):
        show_page_title("My Recipes")
        show_favorite_notice()

        favorite_recipes = get_favorite_recipes(st.session_state.user_id)

        if not favorite_recipes:
            show_empty_state(
                "No favorite recipes yet. "
                "Use Add to My Recipes after generating a recipe."
            )
            return

        for favorite_recipe in favorite_recipes:
            with st.container(key=f"saved_recipe_{favorite_recipe['id']}"):
                title_col, action_col = st.columns(
                    [1, 0.12],
                    vertical_alignment="top",
                )

                with title_col:
                    show_recipe_heading(favorite_recipe["title"])

                    if favorite_recipe["ingredients"]:
                        show_recipe_meta(
                            [
                                "Ingredients: "
                                + format_ingredients(favorite_recipe["ingredients"])
                            ]
                        )

                with action_col:
                    with st.container(key=f"favorite_remove_{favorite_recipe['id']}"):
                        remove_clicked = st.button(
                            "♥",
                            key=f"remove_favorite_{favorite_recipe['id']}",
                            help="Remove from My Recipes",
                        )

                if remove_clicked:
                    remove_favorite_recipe(
                        st.session_state.user_id,
                        favorite_recipe["id"],
                    )
                    st.session_state.favorite_notice = "Recipe removed from My Recipes."
                    st.rerun()

                show_recipe_body_without_title(favorite_recipe["recipe_text"])


def show_my_pantry_page():
    show_nav_bar(active_page="my_pantry")

    with st.container(key="main_card"):
        show_page_title("My Pantry")
        show_empty_state("Sorry, we are working on implementing a new feature here.")


def show_history_page():
    show_nav_bar(active_page="history")

    with st.container(key="main_card"):
        show_page_title("History")

        history_recipes = get_recipe_history(st.session_state.user_id)

        if not history_recipes:
            show_empty_state("No recipes generated yet.")
            return

        for history_recipe in history_recipes:
            with st.container(key=f"saved_recipe_history_{history_recipe['id']}"):
                show_recipe_heading(history_recipe["title"])

                meta_items = []

                if history_recipe["ingredients"]:
                    meta_items.append(
                        "Ingredients: "
                        + format_ingredients(history_recipe["ingredients"])
                    )

                if history_recipe["created_at"]:
                    meta_items.append(f"Generated: {history_recipe['created_at']}")

                show_recipe_meta(meta_items)

                show_recipe_body_without_title(history_recipe["recipe_text"])


def show_my_account_page():
    show_nav_bar(active_page="my_account")

    with st.container(key="main_card"):
        show_page_title(f"@{st.session_state.username}")

        st.markdown(
            "<p class='section-label'>Edit your account details</p>",
            unsafe_allow_html=True,
        )

        username = st.text_input(
            "Username",
            value=st.session_state.username,
            key="account_username",
        )

        email = st.text_input(
            "Email",
            value=st.session_state.email,
            key="account_email",
        )

        current_password = st.text_input(
            "Current Password",
            type="password",
            key="account_current_password",
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            key="account_new_password",
        )

        confirm_new_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="account_confirm_new_password",
        )

        with st.container(key="save_account_action"):
            save_clicked = st.button("Save Changes", key="save_account_btn")

        if save_clicked:
            if not username or not email or not current_password:
                st.warning("Please fill in username, email, and current password.")
            elif new_password and new_password != confirm_new_password:
                st.error("New passwords do not match.")
            elif confirm_new_password and not new_password:
                st.error("Please enter the new password first.")
            else:
                success, message = update_user_account(
                    st.session_state.user_id,
                    username,
                    email,
                    current_password,
                    new_password if new_password else None,
                )

                if success:
                    user_data = {
                        "id": st.session_state.user_id,
                        "username": username,
                        "email": email,
                    }

                    st.session_state.username = username
                    st.session_state.email = email
                    update_stored_auth_session(user_data)

                    st.success(message)
                else:
                    st.error(message)

        st.markdown("<hr class='account-divider'>", unsafe_allow_html=True)

        with st.container(key="delete_account_action"):
            delete_clicked = st.button("Delete Account", key="delete_account_btn")

        if delete_clicked:
            st.session_state.confirm_delete_account = True

        if st.session_state.confirm_delete_account:
            with st.container(key="delete_account_confirm_box"):
                st.warning(
                    "Are you sure you want to delete your account? "
                    "This action cannot be undone."
                )

                yes_col, no_col = st.columns(2)

                with yes_col:
                    confirm_yes = st.button(
                        "Yes, delete my account",
                        key="confirm_delete_yes",
                    )

                with no_col:
                    confirm_no = st.button(
                        "No, keep editing",
                        key="confirm_delete_no",
                    )

                if confirm_yes:
                    user_id = st.session_state.user_id

                    st.session_state.current_page = "home"
                    st.session_state.logged_in = False
                    st.session_state.confirm_delete_account = False

                    delete_user_account(user_id)
                    logout()

                if confirm_no:
                    st.session_state.confirm_delete_account = False
                    st.rerun()


load_css()
init_db()
init_session_state()

if not st.session_state.logged_in:
    set_login_background()
    show_login()
else:
    set_main_background()
    current_page = get_current_page()
    page_renderers = {
        "home": show_main_app,
        "my_recipes": show_my_recipes_page,
        "my_pantry": show_my_pantry_page,
        "history": show_history_page,
        "my_account": show_my_account_page,
    }
    page_renderers.get(current_page, show_main_app)()
