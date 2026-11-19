
import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("Smart Resume Analyzer")

try:
    response = requests.get(f"{API_URL}/", timeout=5)
    response.raise_for_status()
    st.success("Connected to Flask Backend")
except requests.RequestException:
    st.error("Flask backend is not running")

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
    payload = {
        "name": name, "email": email, "skills": skills,
        "experience": experience, "education": education
    }
    try:
        response = requests.post(
            f"{API_URL}/submit-resume", json=payload, timeout=5
        )
        response.raise_for_status()
        result = response.json()
        st.success(result["message"])
        st.info(f"Candidate ID: {result['resume_id']}")
    except requests.RequestException:
        st.error("Unable to submit resume")

st.divider()
st.subheader("Saved Candidates")

if st.button("View Saved Resumes"):
    try:
        response = requests.get(f"{API_URL}/resumes", timeout=5)
        response.raise_for_status()
        resumes = response.json()
        if resumes:
            st.dataframe(resumes, use_container_width=True)
        else:
            st.info("No resumes found")
    except requests.RequestException:
        st.error("Unable to load resumes")

st.divider()
st.subheader("Job Description Analysis")

job_description = st.text_area("Enter Job Description")

if st.button("Analyze Job Description"):
    if job_description.strip():
        st.session_state["job_description"] = job_description
        st.success("Job description added")
    else:
        st.warning("Please enter a job description")

st.divider()
st.subheader("Resume Match Score")

candidate_skills = st.text_input("Candidate Skills for Matching")
required_skills = st.text_input("Required Job Skills")

if st.button("Calculate Match"):
    try:
        response = requests.post(
            f"{API_URL}/compare-skills",
            json={
                "candidate_skills": candidate_skills,
                "required_skills": required_skills
            },
            timeout=5
        )
        response.raise_for_status()
        st.session_state["match_result"] = response.json()
    except requests.RequestException:
        st.error("Unable to calculate matching score")

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
        "Years of Experience", min_value=0, max_value=50,
        key="score_experience"
    )
    score_education = st.selectbox(
        "Education", ["Diploma", "BTech", "MTech", "PhD"]
    )
    calculate = st.form_submit_button("Calculate Overall Score")

if calculate:
    try:
        response = requests.post(
            f"{API_URL}/overall-score",
            json={
                "skill_score": score_skills,
                "experience": score_experience,
                "education": score_education
            },
            timeout=5
        )
        response.raise_for_status()
        st.session_state["overall_score"] = response.json()["overall_score"]
    except requests.RequestException:
        st.error("Unable to calculate overall score")

if "overall_score" in st.session_state:
    overall = st.session_state["overall_score"]
    st.progress(overall / 100)
    st.metric("Overall Score", f"{overall}%")

st.divider()
st.subheader("Candidate Ranking")

ranking_skills = st.text_input("Required Skills for Ranking")

if st.button("Rank Candidates"):
    try:
        response = requests.post(
            f"{API_URL}/rank-candidates",
            json={"required_skills": ranking_skills},
            timeout=5
        )
        response.raise_for_status()
        candidates = response.json()
        if candidates:
            st.dataframe(candidates, use_container_width=True)
        else:
            st.info("No candidates available")
    except requests.RequestException:
        st.error("Unable to rank candidates")

st.divider()
st.subheader("Search Candidates")

search_name = st.text_input("Candidate Name to Search")

if st.button("Search Candidates"):
    try:
        response = requests.get(
            f"{API_URL}/search-candidates",
            params={"name": search_name}, timeout=5
        )
        response.raise_for_status()
        results = response.json()
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No matching candidates found")
    except requests.RequestException:
        st.error("Candidate search failed")

st.divider()
st.subheader("Filter Candidates by Skill")

filter_skill = st.text_input("Skill to Filter")

if st.button("Filter Candidates"):
    try:
        response = requests.get(
            f"{API_URL}/filter-skills",
            params={"skill": filter_skill}, timeout=5
        )
        response.raise_for_status()
        results = response.json()
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No candidates found with this skill")
    except requests.RequestException:
        st.error("Unable to filter candidates")

st.divider()
st.subheader("Delete Candidate")

delete_id = st.number_input(
    "Candidate ID to Delete", min_value=1, step=1
)

if st.button("Delete Candidate"):
    try:
        response = requests.delete(
            f"{API_URL}/resumes/{delete_id}", timeout=5
        )
        response.raise_for_status()
        st.success(response.json()["message"])
    except requests.RequestException:
        st.error("Unable to delete candidate")

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
    payload = {
        "name": update_name, "email": update_email,
        "skills": update_skills,
        "experience": update_experience,
        "education": update_education
    }
    try:
        response = requests.put(
            f"{API_URL}/resumes/{update_id}",
            json=payload, timeout=5
        )
        response.raise_for_status()
        st.success(response.json()["message"])
    except requests.RequestException:
        st.error("Unable to update candidate")

st.divider()
st.subheader("Analysis History")

with st.form("analysis_form"):
    history_id = st.number_input(
        "Candidate ID for Analysis", min_value=1, step=1
    )
    history_skills = st.text_input("Required Skills for Analysis")
    save_history = st.form_submit_button("Save Analysis")

if save_history:
    try:
        response = requests.post(
            f"{API_URL}/save-analysis",
            json={
                "candidate_id": history_id,
                "required_skills": history_skills
            },
            timeout=5
        )
        response.raise_for_status()
        st.success("Analysis saved successfully")
        st.metric("Saved Match Score", f"{response.json()['match_score']}%")
    except requests.RequestException:
        st.error("Unable to save analysis")

if st.button("View Analysis History"):
    try:
        response = requests.get(
            f"{API_URL}/analysis-history", timeout=5
        )
        response.raise_for_status()
        history = response.json()
        if history:
            st.dataframe(history, use_container_width=True)
        else:
            st.info("No analysis history available")
    except requests.RequestException:
        st.error("Unable to load analysis history")
