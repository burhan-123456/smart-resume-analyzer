import streamlit as st
import requests

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("Smart Resume Analyzer")

try:
    response = requests.get(
        "http://127.0.0.1:5000/",
        timeout=5
    )
    response.raise_for_status()

    data = response.json()

    st.success("Connected to Flask Backend")
    st.write(data["message"])

except requests.RequestException:
    st.error("Flask backend is not running")