
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
    return list(dict.fromkeys(
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    ))


def extract_keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text.lower())
    return sorted({
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    })


def compare_skills(candidate_skills, required_skills):
    candidate = set(parse_skills(candidate_skills))
    required = set(parse_skills(required_skills))
    return {
        "matched": sorted(candidate & required),
        "missing": sorted(required - candidate)
    }


def calculate_match_score(candidate_skills, required_skills):
    required = set(parse_skills(required_skills))
    if not required:
        return 0.0
    matched = set(parse_skills(candidate_skills)) & required
    return round(len(matched) / len(required) * 100, 2)


def generate_suggestions(missing_skills):
    return [
        f"Consider learning {skill} through projects and practice"
        for skill in missing_skills
    ]


def calculate_experience_score(years):
    if years >= 5:
        return 100
    if years >= 3:
        return 80
    if years >= 1:
        return 60
    if years > 0:
        return 40
    return 20


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

    fields = ["name", "email", "skills", "experience", "education"]
    if any(field not in data for field in fields):
        return jsonify({"error": "Missing required fields"}), 400

    name = data["name"]
    email = data["email"]
    skills = data["skills"]
    experience = data["experience"]

    if not isinstance(name, str) or len(name.strip()) < 2:
        return jsonify({"error": "Invalid candidate name"}), 400

    if not isinstance(email, str) or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()
    ):
        return jsonify({"error": "Invalid email address"}), 400

    if not isinstance(skills, str) or not parse_skills(skills):
        return jsonify({"error": "At least one skill is required"}), 400

    if (
        isinstance(experience, bool)
        or not isinstance(experience, (int, float))
        or not 0 <= experience <= 50
    ):
        return jsonify({"error": "Invalid experience"}), 400

    if not isinstance(data["education"], str):
        return jsonify({"error": "Invalid education"}), 400

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

    return jsonify({"keywords": extract_keywords(description)})


@app.route("/compare-skills", methods=["POST"])
def compare_skills_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    candidate = data.get("candidate_skills", "")
    required = data.get("required_skills", "")

    if not isinstance(candidate, str) or not isinstance(required, str):
        return jsonify({"error": "Skills must be text"}), 400

    result = compare_skills(candidate, required)
    result["score"] = calculate_match_score(candidate, required)
    result["suggestions"] = generate_suggestions(result["missing"])

    return jsonify(result)


@app.route("/experience-score", methods=["POST"])
def experience_score_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    years = data.get("experience", 0)

    if (
        isinstance(years, bool)
        or not isinstance(years, (int, float))
        or not 0 <= years <= 50
    ):
        return jsonify({"error": "Invalid experience"}), 400

    return jsonify({
        "experience_score": calculate_experience_score(years)
    })


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
