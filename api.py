
from flask import Flask, jsonify, request

from services import (
    get_connection, init_db, save_resume,
    get_all_resumes, delete_resume, update_resume,
    save_analysis, get_analysis_history,
    parse_skills, extract_keywords, compare_skills,
    calculate_match_score, generate_suggestions,
    calculate_experience_score, calculate_education_score,
    calculate_overall_score, validate_resume,
    get_skill_frequency, get_statistics,
    get_candidate, compare_candidates
)

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
    return jsonify({
        "database": "SQLite",
        "status": "connected"
    })


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

    return jsonify({
        "keywords": extract_keywords(description)
    })


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

    candidates.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

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

    return jsonify({
        "message": "Candidate deleted successfully"
    })


@app.route("/resumes/<int:resume_id>", methods=["PUT"])
def update_resume_api(resume_id):
    data, error = validate_resume(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    if not update_resume(resume_id, data):
        return jsonify({"error": "Candidate not found"}), 404

    return jsonify({
        "message": "Candidate updated successfully"
    })


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

    candidate = get_candidate(candidate_id)

    if candidate is None:
        return jsonify({"error": "Candidate not found"}), 404

    score = calculate_match_score(
        candidate["skills"], required_skills
    )

    analysis_id = save_analysis(
        candidate_id, required_skills, score
    )

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
    return jsonify(get_skill_frequency())


@app.route("/statistics", methods=["GET"])
def statistics_api():
    return jsonify(get_statistics())


@app.route("/compare-candidates", methods=["POST"])
def compare_candidates_api():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    id1 = data.get("candidate_id_1")
    id2 = data.get("candidate_id_2")
    required = data.get("required_skills", "")

    if (
        type(id1) is not int
        or type(id2) is not int
        or id1 < 1 or id2 < 1
        or id1 == id2
        or not isinstance(required, str)
        or not parse_skills(required)
    ):
        return jsonify({"error": "Invalid comparison inputs"}), 400

    candidate1 = get_candidate(id1)
    candidate2 = get_candidate(id2)

    if candidate1 is None or candidate2 is None:
        return jsonify({"error": "Candidate not found"}), 404

    result = compare_candidates(
        candidate1, candidate2, required
    )

    return jsonify(result)


if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
