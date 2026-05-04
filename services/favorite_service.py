import hashlib
import sqlite3

from database.db import get_connection
from services.recipe_record_utils import encode_ingredients, rows_to_recipe_dicts


def get_recipe_hash(recipe_text):
    return hashlib.sha256(recipe_text.strip().encode("utf-8")).hexdigest()


def add_favorite_recipe(user_id, title, recipe_text, ingredients):
    recipe_hash = get_recipe_hash(recipe_text)

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO favorite_recipes (
                    user_id,
                    title,
                    recipe_text,
                    ingredients,
                    recipe_hash
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    title,
                    recipe_text,
                    encode_ingredients(ingredients),
                    recipe_hash,
                ),
            )
    except sqlite3.IntegrityError:
        return False

    return True


def get_favorite_recipe_id(user_id, recipe_text):
    recipe_hash = get_recipe_hash(recipe_text)

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM favorite_recipes
            WHERE user_id = ? AND recipe_hash = ?
            """,
            (user_id, recipe_hash),
        ).fetchone()

    return row[0] if row else None


def get_favorite_recipes(user_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, recipe_text, ingredients, created_at
            FROM favorite_recipes
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()

    return rows_to_recipe_dicts(rows)


def remove_favorite_recipe(user_id, favorite_recipe_id):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM favorite_recipes
            WHERE user_id = ? AND id = ?
            """,
            (user_id, favorite_recipe_id),
        )

    return cursor.rowcount > 0
