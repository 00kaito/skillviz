"""Analytics dashboard module for SkillViz Analytics."""

import streamlit as st
import pandas as pd
from visualizations import JobMarketVisualizer
from auth import AuthManager
from ui_components import (
    display_data_overview, 
    show_category_info,
    show_user_role_footer
)

def display_analytics():
    """Display the main analytics dashboard."""
    auth_manager = AuthManager()
    df = st.session_state.df
    processor = st.session_state.processor
    
    # Get appropriate data based on authentication status
    is_guest = not auth_manager.is_authenticated()
    
    # Get filtered data based on selected category
    if st.session_state.selected_category == 'all':
        display_df = processor.get_data(is_guest=is_guest)
    else:
        display_df = processor.get_data_by_category(st.session_state.selected_category, is_guest=is_guest)
    
    # Create visualizer with filtered data
    if not display_df.empty:
        visualizer = JobMarketVisualizer(display_df)
    else:
        visualizer = None
    
    # Data overview
    display_data_overview(display_df)
    st.divider()
    
    # Show current category info
    show_category_info(auth_manager)
    
    if display_df.empty:
        if auth_manager.is_authenticated():
            st.warning("⚠️ Brak danych dla wybranej specjalizacji. Administrator musi najpierw przesłać dane.")
        else:
            st.warning("⚠️ Brak danych do wyświetlenia. Skontaktuj się z administratorem lub zaloguj się.")
        return
    
    # Apply additional filters from sidebar if they exist
    if 'filtered_df' in st.session_state and st.session_state.filtered_df is not None:
        display_df = st.session_state.filtered_df.copy()
    
    # Main analytics tabs
    show_analytics_tabs(display_df, visualizer, processor)
    
    # Show user role info
    show_user_role_footer(auth_manager)

def show_analytics_tabs(display_df, visualizer, processor):
    """Show the main analytics tabs."""
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Skills Analysis", 
        "🎯 Experience Levels", 
        "🌍 Location Analysis", 
        "🏢 Company Insights", 
        "📈 Trends"
    ])
    
    with tab1:
        show_skills_analysis(display_df, visualizer, processor)
    
    with tab2:
        show_experience_analysis(display_df, visualizer)
    
    with tab3:
        show_location_analysis(display_df, visualizer, processor)
    
    with tab4:
        show_company_analysis(display_df, visualizer)
    
    with tab5:
        show_trends_analysis(display_df, visualizer, processor)

def show_skills_analysis(display_df, visualizer, processor):
    """Show skills analysis tab content."""
    st.header("Skills Analysis")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Top skills chart
        if visualizer:
            fig_skills = visualizer.create_skills_demand_chart(display_df)
            st.plotly_chart(fig_skills, width='stretch')
    
    with col2:
        # Skills statistics
        skills_stats = processor.get_skills_statistics(display_df)
        st.subheader("Skills Statistics")
        for skill, count in skills_stats.head(10).items():
            percentage = (count / len(display_df)) * 100 if len(display_df) > 0 else 0
            st.metric(skill, f"{count} jobs", f"{percentage:.1f}%")
    
    # Skill combinations
    st.subheader("Most Common Skill Combinations")
    combinations = processor.get_skill_combinations(display_df)
    if not combinations.empty:
        st.dataframe(combinations.head(15), width='stretch')

def show_experience_analysis(display_df, visualizer):
    """Show experience level analysis tab content."""
    st.header("Experience Level Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        if visualizer:
            fig_exp = visualizer.create_experience_distribution_chart(display_df)
            st.plotly_chart(fig_exp, width='stretch')
    
    with col2:
        if visualizer:
            fig_exp_skills = visualizer.create_experience_skills_heatmap(display_df)
            st.plotly_chart(fig_exp_skills, width='stretch')

def show_location_analysis(display_df, visualizer, processor):
    """Show location analysis tab content."""
    st.header("Location-Based Analysis")
    
    # City job distribution
    if visualizer:
        fig_cities = visualizer.create_city_distribution_chart(display_df)
        st.plotly_chart(fig_cities, width='stretch')
    
    # Skills by city
    st.subheader("Top Skills by City")
    city_skills = processor.get_skills_by_location(display_df)
    if not city_skills.empty:
        st.dataframe(city_skills, width='stretch')

def show_company_analysis(display_df, visualizer):
    """Show company insights tab content."""
    st.header("Company Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        # Top hiring companies
        if visualizer:
            fig_companies = visualizer.create_top_companies_chart(display_df)
            st.plotly_chart(fig_companies, width='stretch')
    
    with col2:
        # Remote work analysis
        if visualizer:
            fig_remote = visualizer.create_workplace_type_chart(display_df)
            st.plotly_chart(fig_remote, width='stretch')

def show_trends_analysis(display_df, visualizer, processor):
    """Show market trends tab content."""
    st.header("Market Trends")
    
    # Publishing trends over time
    if visualizer and 'publishedAt' in display_df.columns:
        fig_trends = visualizer.create_publishing_trends_chart(display_df)
        st.plotly_chart(fig_trends, width='stretch')
    
    # Skills trends over time
    st.subheader("Skills Demand Over Time")
    if visualizer and 'publishedAt' in display_df.columns:
        fig_skills_trends = visualizer.create_skills_trends_chart(display_df)
        st.plotly_chart(fig_skills_trends, width='stretch')
    
    # Market summary
    st.subheader("Market Summary")
    summary_stats = processor.get_market_summary(display_df)
    
    for key, value in summary_stats.items():
        st.write(f"**{key}:** {value}")