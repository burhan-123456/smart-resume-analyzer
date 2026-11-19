
import sqlite3

DATABASE = "resumes.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                skills TEXT NOT NULL,
                experience REAL DEFAULT 0,
                education TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                required_skills TEXT NOT NULL,
                match_score REAL NOT NULL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES resumes(id)
            )
        """)
        connection.commit()
    finally:
        connection.close()


def save_resume(data):
    connection = get_connection()
    try:
        cursor = connection.execute("""
            INSERT INTO resumes
            (name, email, skills, experience, education)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["name"], data["email"], data["skills"],
            data["experience"], data["education"]
        ))
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_all_resumes():
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT * FROM resumes ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def delete_resume(resume_id):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "DELETE FROM resumes WHERE id = ?", (resume_id,)
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def update_resume(resume_id, data):
    connection = get_connection()
    try:
        cursor = connection.execute("""
            UPDATE resumes
            SET name = ?, email = ?, skills = ?,
                experience = ?, education = ?
            WHERE id = ?
        """, (
            data["name"], data["email"], data["skills"],
            data["experience"], data["education"], resume_id
        ))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def save_analysis(candidate_id, required_skills, match_score):
    connection = get_connection()
    try:
        cursor = connection.execute("""
            INSERT INTO analysis_history
            (candidate_id, required_skills, match_score)
            VALUES (?, ?, ?)
        """, (candidate_id, required_skills, match_score))
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()
