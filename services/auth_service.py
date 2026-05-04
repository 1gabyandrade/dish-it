import sqlite3

import bcrypt

from database.db import get_connection


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(username, email, password):
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

    except Exception:
        return False, "Username or email is already registered."


def authenticate_user(login_identifier, password):
    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT id, username, email, password_hash
            FROM users
            WHERE username = ? OR email = ?
            """,
            (login_identifier, login_identifier),
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
