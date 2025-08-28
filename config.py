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
    st.title("📊 SkillViz Analytics for Engineers")
    st.markdown("### Analyze skill requirements, experience levels, and location-based hiring trends")

# Application constants
GUEST_DATA_LIMIT = 50
SAMPLE_JSON_DATA = {
    "companyLogoThumbUrl": "https://example.com/logo.jpg",
    "title": "Senior Data Engineer",
    "companyName": "Example Company",
    "city": "Warsaw",
    "experienceLevel": "senior",
    "workingTime": "full_time",
    "workplaceType": "remote",
    "remoteInterview": True,
    "openToHireUkrainians": False,
    "publishedAt": "2025-08-18T13:00:28.333Z",
    "requiredSkills": ["ETL", "Java", "SQL", "Python"],
    "link": "https://example.com/job-offer"
}