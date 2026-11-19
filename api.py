
import re
from flask import Flask, jsonify, request
from database import get_connection, init_db, save_resume, get_all_resumes

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Smart Resume Analyzer API",
        "status": "running"
    })


@app.route("/database-status")
def database_status():
    connection = get_connection()
    connection.close()
    return jsonify({"database": "SQLite", "status": "connected"})


@app.route("/submit-resume", methods=["POST"])
def submit_resume():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    required_fields = [
        "name", "email", "skills", "experience", "education"
    ]

    if any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    name = data.get("name", "")

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({
            "error": "Candidate name must contain at least 2 characters"
        }), 400

    email = data.get("email", "")

    if not isinstance(email, str) or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()
    ):
        return jsonify({"error": "Invalid email address"}), 400

    data["name"] = name.strip()
    data["email"] = email.strip().lower()

    resume_id = save_resume(data)

    return jsonify({
        "message": "Resume saved successfully",
        "resume_id": resume_id,
        "status": "created"
    }), 201


@app.route("/resumes", methods=["GET"])
def list_resumes():
    return jsonify(get_all_resumes())


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
