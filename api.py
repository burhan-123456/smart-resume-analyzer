
import re
from flask import Flask, jsonify, request
from database import get_connection, init_db, save_resume, get_all_resumes

app = Flask(__name__)

STOP_WORDS = {
    "a", "an", "the", "and", "or", "for", "with",
    "in", "on", "to", "of", "is", "are", "we",
    "looking", "required", "experience", "developer"
}


def parse_skills(skills):
    cleaned = [
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    ]
    return list(dict.fromkeys(cleaned))


def extract_keywords(text):
    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.]*",
        text.lower()
    )

    return sorted({
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    })


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
        return jsonify({"error": "Invalid candidate name"}), 400

    email = data.get("email", "")

    if not isinstance(email, str) or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()
    ):
        return jsonify({"error": "Invalid email address"}), 400

    skills = data.get("skills", "")

    if not isinstance(skills, str) or not parse_skills(skills):
        return jsonify({"error": "At least one skill is required"}), 400

    data["name"] = name.strip()
    data["email"] = email.strip().lower()
    data["skills"] = ", ".join(parse_skills(skills))

    resume_id = save_resume(data)

    return jsonify({
        "message": "Resume saved successfully",
        "resume_id": resume_id,
        "status": "created"
    }), 201


@app.route("/resumes", methods=["GET"])
def list_resumes():
    return jsonify(get_all_resumes())


@app.route("/extract-keywords", methods=["POST"])
def keywords_api():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    description = data.get("description", "")

    if not isinstance(description, str):
        return jsonify({"error": "Invalid description"}), 400

    return jsonify({
        "keywords": extract_keywords(description)
    })


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
