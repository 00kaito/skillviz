"""Configuration module for SkillViz Analytics application."""

import streamlit as st

def setup_page_config():
    """Set up Streamlit page configuration."""
    st.set_page_config(
        page_title="Job Market Analytics for Engineers",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def setup_app_title():
    """Set up main application title and description."""
    st.title("📊 SkillViz Analytics dla Inżynierów")
    st.markdown("### Analizuj wymagania umiejętności, poziomy doświadczenia i trendy zatrudnienia według lokalizacji")

# Application constants
GUEST_DATA_LIMIT = 50
SAMPLE_JSON_DATA = {
    "role": "Senior Data Engineer",
    "company": "Example Company",
    "city": "Warsaw",
    "employment_type": "B2B",
    "job_time_type": "Full-time",
    "remote": False,
    "seniority": "Senior",
    "salary": "15 000 - 20 000 PLN",
    "published_date": "18.08.2025",
    "skills": {
        "Python": "Senior",
        "SQL": "Regular", 
        "Java": "Regular",
        "ETL": "Senior",
        "English": "B2"
    },
    "url": "https://example.com/job-offer"
}