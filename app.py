
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
        "name": name,
        "email": email,
        "skills": skills,
        "experience": experience,
        "education": education
    }

    try:
        response = requests.post(
            f"{API_URL}/submit-resume",
            json=payload,
            timeout=5
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
        result = response.json()
        st.session_state["match_result"] = result
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
