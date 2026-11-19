
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("Smart Resume Analyzer")


def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=5,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        st.error(f"API Error: {error}")
        return None


if api_request("GET", "/"):
    st.success("Connected to Flask Backend")

st.subheader("Dashboard Statistics")

if st.button("Load Dashboard Statistics"):
    stats = api_request("GET", "/statistics")

    if stats is not None:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Candidates",
            stats["total_candidates"]
        )
        col2.metric(
            "Total Analyses",
            stats["total_analyses"]
        )
        col3.metric(
            "Average Experience",
            f"{stats['average_experience']} years"
        )
        col4.metric(
            "Unique Skills",
            stats["unique_skills"]
        )

st.divider()
st.subheader("Candidate Details")

with st.form("resume_form"):
    name = st.text_input("Candidate Name")
    email = st.text_input("Email Address")
    skills = st.text_area("Skills (comma separated)")
    experience = st.number_input(
        "Experience (Years)", min_value=0, max_value=50
    )
    education = st.text_input("Education")
    submitted = st.form_submit_button("Submit Resume")

if submitted:
    result = api_request(
        "POST",
        "/submit-resume",
        json={
            "name": name,
            "email": email,
            "skills": skills,
            "experience": experience,
            "education": education
        }
    )
    if result is not None:
        st.success(result["message"])
        st.info(f"Candidate ID: {result['resume_id']}")

st.divider()
st.subheader("Saved Candidates")

if st.button("View Saved Resumes"):
    resumes = api_request("GET", "/resumes")
    if resumes is not None:
        if resumes:
            st.dataframe(resumes, use_container_width=True)
        else:
            st.info("No resumes found")

st.divider()
st.subheader("Job Description Analysis")

job_description = st.text_area("Enter Job Description")

if st.button("Analyze Job Description"):
    if job_description.strip():
        result = api_request(
            "POST",
            "/extract-keywords",
            json={"description": job_description}
        )
        if result is not None:
            st.write("Extracted Keywords:", result["keywords"])
    else:
        st.warning("Please enter a job description")

st.divider()
st.subheader("Resume Match Score")

candidate_skills = st.text_input("Candidate Skills for Matching")
required_skills = st.text_input("Required Job Skills")

if st.button("Calculate Match"):
    result = api_request(
        "POST",
        "/compare-skills",
        json={
            "candidate_skills": candidate_skills,
            "required_skills": required_skills
        }
    )
    if result is not None:
        st.session_state["match_result"] = result

if "match_result" in st.session_state:
    result = st.session_state["match_result"]
    st.metric("Skill Match", f"{result['score']}%")

    st.subheader("Missing Skills")
    if result["missing"]:
        for skill in result["missing"]:
            st.warning(f"Missing: {skill}")
    else:
        st.success("No missing skills")

    st.subheader("Matched Skills")
    if result["matched"]:
        for skill in result["matched"]:
            st.success(f"Matched: {skill}")
    else:
        st.info("No matching skills found")

    st.subheader("Improvement Suggestions")
    for suggestion in result.get("suggestions", []):
        st.info(suggestion)

st.divider()
st.subheader("Overall Resume Score")

with st.form("overall_score_form"):
    score_skills = st.slider("Skill Match Score", 0, 100, 50)
    score_experience = st.number_input(
        "Years of Experience",
        min_value=0,
        max_value=50,
        key="score_experience"
    )
    score_education = st.selectbox(
        "Education", ["Diploma", "BTech", "MTech", "PhD"]
    )
    calculate = st.form_submit_button("Calculate Overall Score")

if calculate:
    result = api_request(
        "POST",
        "/overall-score",
        json={
            "skill_score": score_skills,
            "experience": score_experience,
            "education": score_education
        }
    )
    if result is not None:
        st.session_state["overall_score"] = result["overall_score"]

if "overall_score" in st.session_state:
    overall = st.session_state["overall_score"]
    st.progress(overall / 100)
    st.metric("Overall Score", f"{overall}%")

st.divider()
st.subheader("Candidate Ranking")

ranking_skills = st.text_input("Required Skills for Ranking")

if st.button("Rank Candidates"):
    candidates = api_request(
        "POST",
        "/rank-candidates",
        json={"required_skills": ranking_skills}
    )
    if candidates is not None:
        if candidates:
            st.dataframe(candidates, use_container_width=True)
        else:
            st.info("No candidates available")

st.divider()
st.subheader("Search Candidates")

search_name = st.text_input("Candidate Name to Search")

if st.button("Search Candidates"):
    results = api_request(
        "GET",
        "/search-candidates",
        params={"name": search_name}
    )
    if results is not None:
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No matching candidates found")

st.divider()
st.subheader("Filter Candidates by Skill")

filter_skill = st.text_input("Skill to Filter")

if st.button("Filter Candidates"):
    results = api_request(
        "GET",
        "/filter-skills",
        params={"skill": filter_skill}
    )
    if results is not None:
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No candidates found with this skill")

st.divider()
st.subheader("Delete Candidate")

delete_id = st.number_input(
    "Candidate ID to Delete", min_value=1, step=1
)

if st.button("Delete Candidate"):
    result = api_request(
        "DELETE", f"/resumes/{delete_id}"
    )
    if result is not None:
        st.success(result["message"])

st.divider()
st.subheader("Update Candidate")

with st.form("update_candidate"):
    update_id = st.number_input(
        "Candidate ID", min_value=1, step=1, key="update_id"
    )
    update_name = st.text_input("Updated Name")
    update_email = st.text_input("Updated Email")
    update_skills = st.text_input("Updated Skills")
    update_experience = st.number_input(
        "Updated Experience", min_value=0, max_value=50
    )
    update_education = st.text_input("Updated Education")
    update_submitted = st.form_submit_button("Update Candidate")

if update_submitted:
    result = api_request(
        "PUT",
        f"/resumes/{update_id}",
        json={
            "name": update_name,
            "email": update_email,
            "skills": update_skills,
            "experience": update_experience,
            "education": update_education
        }
    )
    if result is not None:
        st.success(result["message"])

st.divider()
st.subheader("Analysis History")

with st.form("analysis_form"):
    history_id = st.number_input(
        "Candidate ID for Analysis", min_value=1, step=1
    )
    history_skills = st.text_input("Required Skills for Analysis")
    save_history = st.form_submit_button("Save Analysis")

if save_history:
    result = api_request(
        "POST",
        "/save-analysis",
        json={
            "candidate_id": history_id,
            "required_skills": history_skills
        }
    )
    if result is not None:
        st.success(result["message"])
        st.metric("Saved Match Score", f"{result['match_score']}%")

if st.button("View Analysis History"):
    history = api_request("GET", "/analysis-history")
    if history is not None:
        if history:
            st.dataframe(history, use_container_width=True)
        else:
            st.info("No analysis history available")

st.divider()
st.subheader("Skill Frequency Analysis")

if st.button("Show Skill Frequency"):
    frequency = api_request("GET", "/skill-frequency")

    if frequency is not None:
        if frequency:
            df = pd.DataFrame(
                list(frequency.items()),
                columns=["Skill", "Count"]
            )
            df = df.sort_values(
                by="Count", ascending=False
            )
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Skill")["Count"])
        else:
            st.info("No skill data available")
