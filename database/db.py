import sqlite3


DB_PATH = "database/dish_it.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        with open("database/schema.sql", "r") as file:
            conn.executescript(file.read())
