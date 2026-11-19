
import re
from collections import Counter
from flask import Flask, jsonify, request
from database import (
    get_connection, init_db, save_resume,
    get_all_resumes, delete_resume, update_resume,
    save_analysis, get_analysis_history
)

app = Flask(__name__)

STOP_WORDS = {
    "a", "an", "the", "and", "or", "for", "with",
    "in", "on", "to", "of", "is", "are", "we",
    "looking", "required", "experience", "developer"
}


def parse_skills(skills):
    return list(dict.fromkeys(
        skill.strip().lower()
        for skill in skills.split(",") if skill.strip()
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


def normalize_education(education):
    return " ".join(education.strip().lower().split())


def calculate_education_score(education):
    education = normalize_education(education)
    if "phd" in education or "doctorate" in education:
        return 100
    if any(x in education for x in ["mtech", "m.tech", "master", "mba"]):
        return 90
    if any(x in education for x in ["btech", "b.tech", "bachelor", "bsc"]):
        return 75
    if "diploma" in education:
        return 60
    return 40


def calculate_overall_score(skill_score, experience, education):
    return round(
        skill_score * 0.60
        + calculate_experience_score(experience) * 0.25
        + calculate_education_score(education) * 0.15,
        2
    )


def validate_resume(data):
    if not isinstance(data, dict):
        return None, "Invalid JSON data"

    fields = ["name", "email", "skills", "experience", "education"]
    if any(field not in data for field in fields):
        return None, "Missing required fields"

    name = data["name"]
    email = data["email"]
    skills = data["skills"]
    experience = data["experience"]
    education = data["education"]

    if not isinstance(name, str) or len(name.strip()) < 2:
        return None, "Invalid candidate name"

    if not isinstance(email, str) or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()
    ):
        return None, "Invalid email address"

    if not isinstance(skills, str) or not parse_skills(skills):
        return None, "At least one skill is required"

    if (
        isinstance(experience, bool)
        or not isinstance(experience, (int, float))
        or not 0 <= experience <= 50
    ):
        return None, "Invalid experience"

    if not isinstance(education, str):
        return None, "Invalid education"

    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "skills": ", ".join(parse_skills(skills)),
        "experience": experience,
        "education": normalize_education(education)
    }, None


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
    data, error = validate_resume(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

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


@app.route("/education-score", methods=["POST"])
def education_score_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    education = data.get("education", "")
    if not isinstance(education, str):
        return jsonify({"error": "Invalid education"}), 400

    return jsonify({
        "education_score": calculate_education_score(education)
    })


@app.route("/overall-score", methods=["POST"])
def overall_score_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    skill_score = data.get("skill_score")
    experience = data.get("experience")
    education = data.get("education")

    if (
        isinstance(skill_score, bool)
        or not isinstance(skill_score, (int, float))
        or not 0 <= skill_score <= 100
        or isinstance(experience, bool)
        or not isinstance(experience, (int, float))
        or not 0 <= experience <= 50
        or not isinstance(education, str)
    ):
        return jsonify({"error": "Invalid score inputs"}), 400

    return jsonify({
        "overall_score": calculate_overall_score(
            skill_score, experience, education
        )
    })


@app.route("/rank-candidates", methods=["POST"])
def rank_candidates():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    required = data.get("required_skills", "")
    if not isinstance(required, str) or not parse_skills(required):
        return jsonify({"error": "Required skills are missing"}), 400

    candidates = get_all_resumes()
    for candidate in candidates:
        candidate["match_score"] = calculate_match_score(
            candidate["skills"], required
        )

    candidates.sort(key=lambda item: item["match_score"], reverse=True)
    return jsonify(candidates)


@app.route("/search-candidates", methods=["GET"])
def search_candidates():
    keyword = request.args.get("name", "").strip().lower()
    return jsonify([
        candidate for candidate in get_all_resumes()
        if keyword in candidate["name"].lower()
    ])


@app.route("/filter-skills", methods=["GET"])
def filter_skills():
    skill = request.args.get("skill", "").strip().lower()
    if not skill:
        return jsonify([])
    return jsonify([
        candidate for candidate in get_all_resumes()
        if skill in parse_skills(candidate["skills"])
    ])


@app.route("/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume_api(resume_id):
    if not delete_resume(resume_id):
        return jsonify({"error": "Candidate not found"}), 404
    return jsonify({"message": "Candidate deleted successfully"})


@app.route("/resumes/<int:resume_id>", methods=["PUT"])
def update_resume_api(resume_id):
    data, error = validate_resume(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    if not update_resume(resume_id, data):
        return jsonify({"error": "Candidate not found"}), 404

    return jsonify({"message": "Candidate updated successfully"})


@app.route("/save-analysis", methods=["POST"])
def save_analysis_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    candidate_id = data.get("candidate_id")
    required_skills = data.get("required_skills")

    if (
        isinstance(candidate_id, bool)
        or not isinstance(candidate_id, int)
        or candidate_id < 1
        or not isinstance(required_skills, str)
        or not parse_skills(required_skills)
    ):
        return jsonify({"error": "Invalid analysis inputs"}), 400

    candidate = next(
        (item for item in get_all_resumes()
         if item["id"] == candidate_id),
        None
    )
    if candidate is None:
        return jsonify({"error": "Candidate not found"}), 404

    score = calculate_match_score(
        candidate["skills"], required_skills
    )
    analysis_id = save_analysis(candidate_id, required_skills, score)

    return jsonify({
        "analysis_id": analysis_id,
        "match_score": score,
        "message": "Analysis saved successfully"
    }), 201


@app.route("/analysis-history", methods=["GET"])
def analysis_history_api():
    return jsonify(get_analysis_history())


@app.route("/skill-frequency", methods=["GET"])
def skill_frequency_api():
    counter = Counter()

    for candidate in get_all_resumes():
        counter.update(parse_skills(candidate["skills"]))

    return jsonify(dict(counter.most_common()))


@app.route("/statistics", methods=["GET"])
def statistics_api():
    candidates = get_all_resumes()
    history = get_analysis_history()

    total_candidates = len(candidates)
    total_analyses = len(history)

    average_experience = (
        round(
            sum(c["experience"] for c in candidates)
            / total_candidates,
            2
        )
        if total_candidates else 0
    )

    unique_skills = set()
    for candidate in candidates:
        unique_skills.update(parse_skills(candidate["skills"]))

    return jsonify({
        "total_candidates": total_candidates,
        "total_analyses": total_analyses,
        "average_experience": average_experience,
        "unique_skills": len(unique_skills)
    })


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
