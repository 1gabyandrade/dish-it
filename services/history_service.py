import logging
import sqlite3

from database.db import get_connection
from services.recipe_record_utils import encode_ingredients, rows_to_recipe_dicts


def add_recipe_history(user_id, title, recipe_text, ingredients):
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO recipe_history (
                    user_id,
                    title,
                    recipe_text,
                    ingredients
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    title,
                    recipe_text,
                    encode_ingredients(ingredients),
                ),
            )

        return cursor.lastrowid

    except Exception as e:
        logging.error(f"Add history failed: {e}")
        return None


def get_recipe_history(user_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, recipe_text, ingredients, created_at
            FROM recipe_history
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()

    return rows_to_recipe_dicts(rows)
