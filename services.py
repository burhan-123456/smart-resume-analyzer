
import re
from collections import Counter

from database import (
    get_connection, init_db, save_resume,
    get_all_resumes, delete_resume, update_resume,
    save_analysis, get_analysis_history
)

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


def get_skill_frequency():
    counter = Counter()
    for candidate in get_all_resumes():
        counter.update(parse_skills(candidate["skills"]))
    return dict(counter.most_common())


def get_statistics():
    candidates = get_all_resumes()
    history = get_analysis_history()
    total = len(candidates)

    average_experience = (
        round(
            sum(c["experience"] for c in candidates) / total,
            2
        )
        if total else 0
    )

    unique_skills = set()
    for candidate in candidates:
        unique_skills.update(parse_skills(candidate["skills"]))

    return {
        "total_candidates": total,
        "total_analyses": len(history),
        "average_experience": average_experience,
        "unique_skills": len(unique_skills)
    }


def get_candidate(candidate_id):
    return next(
        (c for c in get_all_resumes() if c["id"] == candidate_id),
        None
    )


def compare_candidates(candidate1, candidate2, required_skills):
    score1 = calculate_match_score(
        candidate1["skills"], required_skills
    )
    score2 = calculate_match_score(
        candidate2["skills"], required_skills
    )

    return {
        "candidate_1": {
            **candidate1,
            "match_score": score1
        },
        "candidate_2": {
            **candidate2,
            "match_score": score2
        },
        "higher_match": (
            candidate1["name"] if score1 > score2
            else candidate2["name"] if score2 > score1
            else "Tie"
        )
    }
