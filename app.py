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
        st.success(response.json()["message"])
    except requests.RequestException:
        st.error("Unable to submit resume")