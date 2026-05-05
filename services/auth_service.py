import re
import sqlite3

import bcrypt

from database.db import get_connection

MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_username(username):
    return username.strip()


def normalize_email(email):
    return email.strip().lower()


def validate_username(username):
    if not username:
        return False, "Username is required."

    if len(username) < MIN_USERNAME_LENGTH:
        return False, "Username must be at least 3 characters."

    return True, ""


def validate_email(email):
    if not email:
        return False, "Email is required."

    if not EMAIL_PATTERN.match(email):
        return False, "Please enter a valid email address."

    return True, ""


def validate_password(password):
    if not password:
        return False, "Password is required."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, "Password must be at least 6 characters."

    return True, ""


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(username, email, password):
    username = normalize_username(username)
    email = normalize_email(email)

    username_is_valid, username_message = validate_username(username)
    if not username_is_valid:
        return False, username_message

    email_is_valid, email_message = validate_email(email)
    if not email_is_valid:
        return False, email_message

    password_is_valid, password_message = validate_password(password)
    if not password_is_valid:
        return False, password_message

    password_hash = hash_password(password)

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash),
            )

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "Username or email is already registered."

    except Exception:
        return False, "Something went wrong. Please try again."


def authenticate_user(login_identifier, password):
    login_identifier = login_identifier.strip()

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT id, username, email, password_hash
            FROM users
            WHERE username = ? OR email = ?
            """,
            (login_identifier, login_identifier.lower()),
        ).fetchone()

    if not user:
        return False, None, "User not found."

    user_id, username, email, password_hash = user

    if not check_password(password, password_hash):
        return False, None, "Incorrect password."

    user_data = {
        "id": user_id,
        "username": username,
        "email": email,
    }

    return True, user_data, "Login successful."


def update_user_account(user_id, username, email, old_password, new_password=None):
    username = normalize_username(username)
    email = normalize_email(email)

    username_is_valid, username_message = validate_username(username)
    if not username_is_valid:
        return False, username_message

    email_is_valid, email_message = validate_email(email)
    if not email_is_valid:
        return False, email_message

    if not old_password:
        return False, "Current password is required."

    if new_password:
        password_is_valid, password_message = validate_password(new_password)
        if not password_is_valid:
            return False, password_message

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT password_hash
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if not user:
            return False, "User not found."

        password_hash = user[0]

        if not check_password(old_password, password_hash):
            return False, "Current password is incorrect."

        if new_password and check_password(new_password, password_hash):
            return False, "New password must be different from the current password."

        try:
            if new_password:
                new_password_hash = hash_password(new_password)

                conn.execute(
                    """
                    UPDATE users
                    SET username = ?, email = ?, password_hash = ?
                    WHERE id = ?
                    """,
                    (username, email, new_password_hash, user_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE users
                    SET username = ?, email = ?
                    WHERE id = ?
                    """,
                    (username, email, user_id),
                )

        except sqlite3.IntegrityError:
            return False, "Username or email is already used."

        except Exception:
            return False, "Something went wrong. Please try again."

    return True, "Account updated successfully."


def delete_user_account(user_id):
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """,
            (user_id,),
        )

    return True
