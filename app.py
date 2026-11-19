
import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("Smart Resume Analyzer")

# Check Flask backend connection
try:
    response = requests.get(
        f"{API_URL}/",
        timeout=5
    )
    response.raise_for_status()

    st.success("Connected to Flask Backend")

except requests.RequestException:
    st.error("Flask backend is not running")


# Candidate form
st.subheader("Candidate Details")

with st.form("resume_form"):
    name = st.text_input("Candidate Name")
    email = st.text_input("Email Address")
    skills = st.text_area("Skills (comma separated)")

    experience = st.number_input(
        "Experience (Years)",
        min_value=0,
        max_value=50
    )

    education = st.text_input("Education")

    submitted = st.form_submit_button("Submit Resume")


# Submit candidate details
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

    except requests.RequestException:
        st.error("Unable to submit resume")


# Display saved candidates
st.divider()
st.subheader("Saved Candidates")

if st.button("View Saved Resumes"):
    try:
        response = requests.get(
            f"{API_URL}/resumes",
            timeout=5
        )

        response.raise_for_status()
        resumes = response.json()

        if resumes:
            st.dataframe(
                resumes,
                use_container_width=True
            )
        else:
            st.info("No resumes found in database")

    except requests.RequestException:
        st.error("Unable to load resumes")
