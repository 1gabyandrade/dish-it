import sqlite3

DB_PATH = "database/dish_it.db"


def get_connection():
    conn = sqlite3.connect("database/dish_it.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        with open("database/schema.sql", "r") as file:
            conn.executescript(file.read())
