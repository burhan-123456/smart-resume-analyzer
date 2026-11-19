
import sqlite3

DATABASE = "resumes.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience INTEGER DEFAULT 0,
            education TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_resume(data):
    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO resumes
            (name, email, skills, experience, education)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["email"],
            data["skills"],
            data["experience"],
            data["education"]
        ))

        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()
