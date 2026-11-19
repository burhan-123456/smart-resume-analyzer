
import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
    color: #0f172a;
}
h1, h2, h3 {
    color: #1e3a8a;
    font-weight: 700;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
}
div.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
}
div.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}
div[data-testid="stForm"] {
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)


def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=10,
            **kwargs
        )
        if not response.ok:
            try:
                message = response.json().get(
                    "error", "Request failed"
                )
            except ValueError:
                message = response.text or "Request failed"
            st.error(f"API Error ({response.status_code}): {message}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to Flask backend.")
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except requests.RequestException as error:
        st.error(f"Unexpected API error: {error}")
    return None


def show_table(data, empty_message="No records found"):
    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info(empty_message)


st.title("📄 Smart Resume Analyzer")
st.caption("Candidate management, skill matching and recruitment analytics")

try:
    status_response = requests.get(f"{API_URL}/", timeout=5)
    status_response.raise_for_status()
    st.success("Connected to Flask Backend")
except requests.RequestException:
    st.warning("Flask backend is not running")

tabs = st.tabs([
    "Dashboard",
    "Candidates",
    "Resume Analysis",
    "Ranking",
    "Analytics",
    "Management"
])

with tabs[0]:
    st.header("Dashboard Statistics")

    if st.button("Load Dashboard Statistics"):
        stats = api_request("GET", "/statistics")
        if stats is not None:
            st.session_state["dashboard_stats"] = stats

    if "dashboard_stats" in st.session_state:
        stats = st.session_state["dashboard_stats"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Candidates", stats["total_candidates"])
        c2.metric("Total Analyses", stats["total_analyses"])
        c3.metric(
            "Average Experience",
            f"{stats['average_experience']} years"
        )
        c4.metric("Unique Skills", stats["unique_skills"])

    st.subheader("Export Candidate Data")
    try:
        response = requests.get(
            f"{API_URL}/export-candidates",
            timeout=10
        )
        response.raise_for_status()
        st.download_button(
            "Download Candidates CSV",
            data=response.content,
            file_name="candidates.csv",
            mime="text/csv"
        )
    except requests.RequestException:
        st.error("Unable to prepare CSV export")


with tabs[1]:
    st.header("Candidate Registration")

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

    if submitted:
        result = api_request(
            "POST", "/submit-resume",
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

    st.subheader("Saved Candidates")

    if st.button("View Saved Resumes"):
        resumes = api_request("GET", "/resumes")
        if resumes is not None:
            show_table(resumes)

    st.subheader("Search Candidates")
    search_name = st.text_input("Search by Candidate Name")

    if st.button("Search"):
        results = api_request(
            "GET", "/search-candidates",
            params={"name": search_name}
        )
        if results is not None:
            show_table(results)

    st.subheader("Filter Candidates by Skill")
    filter_skill = st.text_input("Enter Skill")

    if st.button("Filter"):
        results = api_request(
            "GET", "/filter-skills",
            params={"skill": filter_skill}
        )
        if results is not None:
            show_table(results)


with tabs[2]:
    st.header("Job Description Analysis")

    job_description = st.text_area("Enter Job Description")

    if st.button("Analyze Job Description"):
        if job_description.strip():
            result = api_request(
                "POST", "/extract-keywords",
                json={"description": job_description}
            )
            if result is not None:
                st.write("Keywords:", result["keywords"])
        else:
            st.warning("Please enter a job description")

    st.divider()
    st.subheader("Resume Skill Match")

    candidate_skills = st.text_input("Candidate Skills")
    required_skills = st.text_input("Required Job Skills")

    if st.button("Calculate Match"):
        result = api_request(
            "POST", "/compare-skills",
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

        st.subheader("Matched Skills")
        if result["matched"]:
            for skill in result["matched"]:
                st.success(skill)
        else:
            st.info("No matched skills")

        st.subheader("Missing Skills")
        if result["missing"]:
            for skill in result["missing"]:
                st.warning(skill)
        else:
            st.success("No missing skills")

        st.subheader("Improvement Suggestions")
        for suggestion in result.get("suggestions", []):
            st.info(suggestion)

    st.divider()
    st.subheader("Overall Resume Score")

    with st.form("overall_score_form"):
        score_skills = st.slider("Skill Score", 0, 100, 50)
        score_experience = st.number_input(
            "Years of Experience",
            min_value=0,
            max_value=50,
            key="score_experience"
        )
        score_education = st.selectbox(
            "Education",
            ["Diploma", "BTech", "MTech", "PhD"]
        )
        calculate = st.form_submit_button("Calculate Overall Score")

    if calculate:
        result = api_request(
            "POST", "/overall-score",
            json={
                "skill_score": score_skills,
                "experience": score_experience,
                "education": score_education
            }
        )
        if result is not None:
            st.session_state["overall_score"] = result["overall_score"]

    if "overall_score" in st.session_state:
        score = st.session_state["overall_score"]
        st.progress(score / 100)
        st.metric("Overall Score", f"{score}%")


with tabs[3]:
    st.header("Candidate Ranking")

    ranking_skills = st.text_input("Required Skills for Ranking")

    if st.button("Rank Candidates"):
        results = api_request(
            "POST", "/rank-candidates",
            json={"required_skills": ranking_skills}
        )
        if results is not None:
            show_table(results)

    st.divider()
    st.subheader("Top 5 Candidates")

    top_required = st.text_input(
        "Required Skills for Top Candidates"
    )

    if st.button("Show Top 5 Candidates"):
        results = api_request(
            "POST", "/top-candidates",
            json={"required_skills": top_required}
        )
        if results is not None:
            show_table(results)

    st.divider()
    st.subheader("Compare Two Candidates")

    with st.form("compare_candidates_form"):
        candidate_id_1 = st.number_input(
            "First Candidate ID", min_value=1, step=1
        )
        candidate_id_2 = st.number_input(
            "Second Candidate ID", min_value=1, step=1
        )
        compare_required = st.text_input(
            "Required Skills for Comparison"
        )
        compare_submit = st.form_submit_button("Compare Candidates")

    if compare_submit:
        result = api_request(
            "POST", "/compare-candidates",
            json={
                "candidate_id_1": candidate_id_1,
                "candidate_id_2": candidate_id_2,
                "required_skills": compare_required
            }
        )
        if result is not None:
            col1, col2 = st.columns(2)

            with col1:
                c = result["candidate_1"]
                st.subheader(c["name"])
                st.write("Skills:", c["skills"])
                st.write("Experience:", c["experience"])
                st.write("Education:", c["education"])
                st.metric("Match Score", f"{c['match_score']}%")

            with col2:
                c = result["candidate_2"]
                st.subheader(c["name"])
                st.write("Skills:", c["skills"])
                st.write("Experience:", c["experience"])
                st.write("Education:", c["education"])
                st.metric("Match Score", f"{c['match_score']}%")

            st.success(
                f"Higher Skill Match: {result['higher_match']}"
            )


with tabs[4]:
    st.header("Skill Frequency Analysis")

    if st.button("Show Skill Frequency"):
        frequency = api_request("GET", "/skill-frequency")
        if frequency is not None:
            if frequency:
                df = pd.DataFrame(
                    list(frequency.items()),
                    columns=["Skill", "Count"]
                ).sort_values("Count", ascending=False)

                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index("Skill")["Count"])
            else:
                st.info("No skill data available")

    st.divider()
    st.subheader("Analysis History")

    with st.form("analysis_form"):
        history_id = st.number_input(
            "Candidate ID for Analysis", min_value=1, step=1
        )
        history_skills = st.text_input(
            "Required Skills for Analysis"
        )
        save_history = st.form_submit_button("Save Analysis")

    if save_history:
        result = api_request(
            "POST", "/save-analysis",
            json={
                "candidate_id": history_id,
                "required_skills": history_skills
            }
        )
        if result is not None:
            st.success(result["message"])
            st.metric(
                "Saved Match Score",
                f"{result['match_score']}%"
            )

    if st.button("View Analysis History"):
        history = api_request("GET", "/analysis-history")
        if history is not None:
            show_table(history)


with tabs[5]:
    st.header("Candidate Management")

    st.subheader("Update Candidate")

    with st.form("update_candidate"):
        update_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1,
            key="update_id"
        )
        update_name = st.text_input("Updated Name")
        update_email = st.text_input("Updated Email")
        update_skills = st.text_input("Updated Skills")
        update_experience = st.number_input(
            "Updated Experience",
            min_value=0,
            max_value=50
        )
        update_education = st.text_input("Updated Education")
        update_submitted = st.form_submit_button("Update Candidate")

    if update_submitted:
        result = api_request(
            "PUT", f"/resumes/{update_id}",
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
    st.subheader("Delete Candidate")

    delete_id = st.number_input(
        "Candidate ID to Delete",
        min_value=1,
        step=1
    )

    if st.button("Delete Candidate"):
        result = api_request(
            "DELETE", f"/resumes/{delete_id}"
        )
        if result is not None:
            st.success(result["message"])
