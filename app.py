import streamlit as st
import json
import pandas as pd
from data_processor import JobDataProcessor
from visualizations import JobMarketVisualizer
import io

def main():
    st.set_page_config(
        page_title="Job Market Analytics for Engineers",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Job Market Analytics for Engineers")
    st.markdown("### Analyze skill requirements, experience levels, and location-based hiring trends")
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.df = None
        st.session_state.processor = None
        st.session_state.visualizer = None
    
    # Sidebar for data input and filters
    with st.sidebar:
        st.header("📂 Data Input")
        
        # Data input options
        input_method = st.radio("Choose input method:", ["Upload JSON file", "Paste JSON data"])
        
        if input_method == "Upload JSON file":
            uploaded_file = st.file_uploader("Upload job data JSON file", type=['json'])
            if uploaded_file is not None:
                try:
                    json_data = json.load(uploaded_file)
                    if process_data(json_data):
                        st.success("✅ Data loaded successfully!")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file. Please check the format.")
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
        
        else:
            json_text = st.text_area("Paste JSON data here:", height=200)
            if st.button("Load Data"):
                if json_text.strip():
                    try:
                        json_data = json.loads(json_text)
                        if process_data(json_data):
                            st.success("✅ Data loaded successfully!")
                    except json.JSONDecodeError:
                        st.error("❌ Invalid JSON format. Please check your data.")
                    except Exception as e:
                        st.error(f"❌ Error processing data: {str(e)}")
                else:
                    st.warning("⚠️ Please paste JSON data first.")
    
    # Main content area
    if st.session_state.data_loaded and st.session_state.df is not None:
        display_analytics()
    else:
        display_welcome_screen()

def process_data(json_data):
    """Process the loaded JSON data and initialize analytics objects."""
    try:
        processor = JobDataProcessor()
        df = processor.process_json_data(json_data)
        
        if df.empty:
            st.error("❌ No valid job data found in the provided JSON.")
            return False
        
        st.session_state.df = df
        st.session_state.processor = processor
        st.session_state.visualizer = JobMarketVisualizer(df)
        st.session_state.data_loaded = True
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        return False

def display_welcome_screen():
    """Display welcome screen with instructions."""
    st.info("👈 Please upload a JSON file or paste JSON data in the sidebar to begin analysis.")
    
    with st.expander("📋 Expected JSON Format"):
        st.markdown("Your JSON data should contain an array of job objects with the following structure:")
        sample_json = {
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
        st.json([sample_json])

def display_analytics():
    """Display the main analytics dashboard."""
    df = st.session_state.df
    processor = st.session_state.processor
    visualizer = st.session_state.visualizer
    
    # Data overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(df))
    with col2:
        st.metric("Unique Skills", len(processor.get_all_skills()))
    with col3:
        st.metric("Cities", df['city'].nunique())
    with col4:
        st.metric("Companies", df['companyName'].nunique())
    
    st.divider()
    
    # Filters in sidebar
    with st.sidebar:
        if st.session_state.data_loaded:
            st.header("🔍 Filters")
            
            # City filter
            cities = ['All'] + sorted(df['city'].unique().tolist())
            selected_city = st.selectbox("City:", cities)
            
            # Experience level filter
            exp_levels = ['All'] + sorted(df['experienceLevel'].unique().tolist())
            selected_exp = st.selectbox("Experience Level:", exp_levels)
            
            # Company filter
            companies = ['All'] + sorted(df['companyName'].unique().tolist())
            selected_company = st.selectbox("Company:", companies)
            
            # Apply filters
            filtered_df = df.copy()
            if selected_city != 'All':
                filtered_df = filtered_df[filtered_df['city'] == selected_city]
            if selected_exp != 'All':
                filtered_df = filtered_df[filtered_df['experienceLevel'] == selected_exp]
            if selected_company != 'All':
                filtered_df = filtered_df[filtered_df['companyName'] == selected_company]
            
            st.info(f"Showing {len(filtered_df)} of {len(df)} jobs")
    
    # Main analytics tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Skills Analysis", "🎯 Experience Levels", "🌍 Location Analysis", "🏢 Company Insights", "📈 Trends"])
    
    with tab1:
        st.header("Skills Analysis")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # Top skills chart
            fig_skills = visualizer.create_skills_demand_chart(filtered_df)
            st.plotly_chart(fig_skills, use_container_width=True)
        
        with col2:
            # Skills statistics
            skills_stats = processor.get_skills_statistics(filtered_df)
            st.subheader("Skills Statistics")
            for skill, count in skills_stats.head(10).items():
                percentage = (count / len(filtered_df)) * 100
                st.metric(skill, f"{count} jobs", f"{percentage:.1f}%")
        
        # Skill combinations
        st.subheader("Most Common Skill Combinations")
        combinations = processor.get_skill_combinations(filtered_df)
        if not combinations.empty:
            st.dataframe(combinations.head(15), use_container_width=True)
    
    with tab2:
        st.header("Experience Level Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_exp = visualizer.create_experience_distribution_chart(filtered_df)
            st.plotly_chart(fig_exp, use_container_width=True)
        
        with col2:
            fig_exp_skills = visualizer.create_experience_skills_heatmap(filtered_df)
            st.plotly_chart(fig_exp_skills, use_container_width=True)
    
    with tab3:
        st.header("Location-Based Analysis")
        
        # City job distribution
        fig_cities = visualizer.create_city_distribution_chart(filtered_df)
        st.plotly_chart(fig_cities, use_container_width=True)
        
        # Skills by city
        st.subheader("Top Skills by City")
        city_skills = processor.get_skills_by_location(filtered_df)
        if not city_skills.empty:
            st.dataframe(city_skills, use_container_width=True)
    
    with tab4:
        st.header("Company Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            # Top hiring companies
            fig_companies = visualizer.create_top_companies_chart(filtered_df)
            st.plotly_chart(fig_companies, use_container_width=True)
        
        with col2:
            # Remote work analysis
            fig_remote = visualizer.create_workplace_type_chart(filtered_df)
            st.plotly_chart(fig_remote, use_container_width=True)
    
    with tab5:
        st.header("Market Trends")
        
        # Publishing trends over time
        if 'publishedAt' in filtered_df.columns:
            fig_trends = visualizer.create_publishing_trends_chart(filtered_df)
            st.plotly_chart(fig_trends, use_container_width=True)
        
        # Salary insights (if available)
        st.subheader("Market Summary")
        summary_stats = processor.get_market_summary(filtered_df)
        
        for key, value in summary_stats.items():
            st.write(f"**{key}:** {value}")
    
    # Export functionality
    st.divider()
    st.subheader("📥 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Filtered Data as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="job_market_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download Skills Analysis"):
            skills_stats = processor.get_skills_statistics(filtered_df)
            skills_csv = skills_stats.to_csv()
            st.download_button(
                label="Download Skills CSV",
                data=skills_csv,
                file_name="skills_analysis.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
