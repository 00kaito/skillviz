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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Analiza Umiejętności", 
        "🎯 Poziomy Doświadczenia", 
        "🌍 Analiza Lokalizacji", 
        "🏢 Analiza Firm", 
        "📈 Trendy Rynkowe",
        "💰 Analiza Dochodów"
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
    
    with tab6:
        show_salary_analysis(display_df, visualizer, processor)

def show_skills_analysis(display_df, visualizer, processor):
    """Show skills analysis tab content."""
    st.header("Analiza Umiejętności")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Top skills chart
        if visualizer:
            fig_skills = visualizer.create_skills_demand_chart(display_df)
            st.plotly_chart(fig_skills, width='stretch')
    
    with col2:
        # Skills statistics
        skills_stats = processor.get_skills_statistics(display_df)
        st.subheader("Statystyki Umiejętności")
        for skill, count in skills_stats.head(10).items():
            percentage = (count / len(display_df)) * 100 if len(display_df) > 0 else 0
            st.metric(skill, f"{count} ofert", f"{percentage:.1f}%")
    
    # Skill combinations
    st.subheader("Najczęstsze Kombinacje Umiejętności")
    combinations = processor.get_skill_combinations(display_df)
    if not combinations.empty:
        st.dataframe(combinations.head(15), width='stretch')
    
    st.divider()
    
    # NEW: Skill importance weight analysis
    st.header("Analiza Wagi Umiejętności według Poziomów")
    st.markdown("*Analiza uwzględniająca nie tylko częstotliwość umiejętności, ale także wymagany poziom biegłości*")
    
    col1, col2 = st.columns(2)
    with col1:
        # Skill weight chart
        if visualizer:
            fig_weight = visualizer.create_skill_weight_chart(display_df)
            st.plotly_chart(fig_weight, width='stretch')
    
    with col2:
        # Skills by level chart  
        if visualizer:
            fig_levels = visualizer.create_skills_by_level_chart(display_df)
            st.plotly_chart(fig_levels, width='stretch')
    
    # Skill importance matrix
    st.subheader("Macierz Ważności Umiejętności")
    
    # Get available skills for exclusion option
    weight_analysis_for_options = processor.get_skill_weight_analysis(display_df)
    if not weight_analysis_for_options.empty:
        available_skills = weight_analysis_for_options['skill'].tolist()
        # Set default exclusions - Polish is excluded by default
        default_exclusions = [skill for skill in available_skills if skill.lower() in ['polish', 'polski']]
        excluded_skills = st.multiselect(
            "🚫 Wyklucz umiejętności z analizy:",
            options=available_skills,
            default=default_exclusions,
            help="Wybierz umiejętności, które chcesz wykluczyć z macierzy ważności aby lepiej zobaczyć pozostałe"
        )
    else:
        excluded_skills = []
    
    if visualizer:
        fig_matrix = visualizer.create_skill_importance_matrix(display_df, excluded_skills=excluded_skills)
        st.plotly_chart(fig_matrix, width='stretch')
    
    # Skill weight statistics table
    st.subheader("Ranking Umiejętności według Wagi Ważności")
    weight_analysis = processor.get_skill_weight_analysis(display_df)
    if not weight_analysis.empty:
        # Format the data for better display
        display_data = weight_analysis[['skill', 'frequency', 'avg_weight', 'importance_score']].head(20)
        display_data.columns = ['Umiejętność', 'Częstotliwość', 'Średni Poziom', 'Ocena Ważności']
        st.dataframe(display_data, width='stretch', use_container_width=True)

def show_experience_analysis(display_df, visualizer):
    """Show experience level analysis tab content."""
    st.header("Analiza Poziomów Doświadczenia")
    
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
    st.header("Analiza Według Lokalizacji")
    
    # City job distribution
    if visualizer:
        fig_cities = visualizer.create_city_distribution_chart(display_df)
        st.plotly_chart(fig_cities, width='stretch')
    
    # Skills by city
    st.subheader("Najważniejsze Umiejętności w Miastach")
    city_skills = processor.get_skills_by_location(display_df)
    if not city_skills.empty:
        st.dataframe(city_skills, width='stretch')

def show_company_analysis(display_df, visualizer):
    """Show company insights tab content."""
    st.header("Analiza Firm")
    
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
    st.header("Trendy Rynkowe")
    
    # Publishing trends over time
    if visualizer and 'published_date' in display_df.columns:
        fig_trends = visualizer.create_publishing_trends_chart(display_df)
        st.plotly_chart(fig_trends, width='stretch')
    
    # Skills trends over time
    st.subheader("Zapotrzebowanie na Umiejętności w Czasie")
    if visualizer and 'published_date' in display_df.columns:
        fig_skills_trends = visualizer.create_skills_trends_chart(display_df)
        st.plotly_chart(fig_skills_trends, width='stretch')
    
    # Market summary
    st.subheader("Podsumowanie Rynku")
    summary_stats = processor.get_market_summary(display_df)
    
    for key, value in summary_stats.items():
        st.write(f"**{key}:** {value}")

def show_salary_analysis(display_df, visualizer, processor):
    """Show salary analysis tab content."""
    st.header("Analiza Dochodów")
    
    # Check if salary data is available
    if 'salary_avg' not in display_df.columns or display_df['salary_avg'].isna().all():
        st.warning("⚠️ Brak danych o wynagrodzeniach do analizy. Upewnij się, że przesłane dane zawierają pole 'salary' z informacjami o wynagrodzeniach.")
        return
    
    # Filter out rows without salary data for counts
    salary_df = display_df.dropna(subset=['salary_avg'])
    
    if salary_df.empty:
        st.warning("⚠️ Nie znaleziono poprawnych danych o wynagrodzeniach do analizy.")
        return
    
    # Basic salary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_salary = salary_df['salary_avg'].mean()
        st.metric("Średnie Wynagrodzenie", f"{avg_salary:,.0f} PLN")
    
    with col2:
        median_salary = salary_df['salary_avg'].median()
        st.metric("Mediana Wynagrodzeń", f"{median_salary:,.0f} PLN")
    
    with col3:
        min_salary = salary_df['salary_min'].min()
        max_salary = salary_df['salary_max'].max()
        st.metric("Zakres", f"{min_salary:,.0f} - {max_salary:,.0f} PLN")
    
    with col4:
        st.metric("Ofert z danymi o wynagrodzeniach", f"{len(salary_df)} z {len(display_df)}")
    
    st.divider()
    
    # Correlation analysis section
    st.subheader("🔍 Analiza Korelacji z Wynagrodzeniami")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Współczynniki Korelacji dla Umiejętności**")
        if visualizer:
            fig_correlation_bar = visualizer.create_correlation_bar_chart(processor, salary_df)
            st.plotly_chart(fig_correlation_bar, width='stretch')
    
    with col2:
        st.write("**Macierz Korelacji (Heatmap)**")
        if visualizer:
            fig_correlation_heatmap = visualizer.create_correlation_heatmap(processor, salary_df)
            st.plotly_chart(fig_correlation_heatmap, width='stretch')
    
    st.divider()
    
    # Regression analysis section
    st.subheader("📈 Analiza Regresji Liniowej")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Regresja: Poziom Doświadczenia vs Wynagrodzenie**")
        if visualizer:
            fig_seniority_regression = visualizer.create_seniority_regression_chart(processor, salary_df)
            st.plotly_chart(fig_seniority_regression, width='stretch')
    
    with col2:
        st.write("**Regresja: Liczba Umiejętności vs Wynagrodzenie**")
        if visualizer:
            fig_skills_count_regression = visualizer.create_skills_count_regression_chart(processor, salary_df)
            st.plotly_chart(fig_skills_count_regression, width='stretch')
    
    st.divider()
    
    # Statistical summary
    st.subheader("📊 Podsumowanie Analiz Statystycznych")
    
    # Get regression results
    regression_results = processor.get_regression_analysis(salary_df)
    correlations = processor.get_correlation_analysis(salary_df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Regresja Doświadczenia**")
        if 'seniority' in regression_results:
            seniority_r2 = regression_results['seniority']['r_squared']
            st.metric("Współczynnik Determinacji R²", f"{seniority_r2:.3f}")
            st.write(f"Równanie: {regression_results['seniority']['equation']}")
        else:
            st.write("Brak wystarczających danych")
    
    with col2:
        st.write("**Regresja Liczby Umiejętności**")
        if 'skills_count' in regression_results:
            skills_r2 = regression_results['skills_count']['r_squared']
            st.metric("Współczynnik Determinacji R²", f"{skills_r2:.3f}")
            st.write(f"Równanie: {regression_results['skills_count']['equation']}")
        else:
            st.write("Brak wystarczających danych")
    
    with col3:
        st.write("**Najsilniejsze Korelacje**")
        if correlations:
            # Get top 3 correlations by absolute value
            skill_correlations = {k: v for k, v in correlations.items() 
                                if k not in ['seniority_level', 'skills_count']}
            
            if skill_correlations:
                top_correlations = sorted(skill_correlations.items(), 
                                        key=lambda x: abs(x[1]), reverse=True)[:3]
                
                for skill, corr in top_correlations:
                    st.write(f"**{skill}:** {corr:.3f}")
            else:
                st.write("Brak danych o korelacjach")
        else:
            st.write("Brak danych o korelacjach")
    
    st.divider()
    
    # Traditional charts section
    st.subheader("💼 Tradycyjne Analizy Wynagrodzeń")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Najlepiej Płacące Umiejętności**")
        if visualizer:
            fig_skills_salary = visualizer.create_skills_salary_correlation_chart(processor, salary_df)
            st.plotly_chart(fig_skills_salary, width='stretch')
    
    with col2:
        st.write("**Wynagrodzenia według Doświadczenia**")
        if visualizer:
            fig_seniority_salary = visualizer.create_seniority_salary_chart(processor, salary_df)
            st.plotly_chart(fig_seniority_salary, width='stretch')
    
    st.divider()
    
    # Additional salary analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Wynagrodzenia według Poziomu Biegłości")
        if visualizer:
            fig_skill_level_salary = visualizer.create_skill_level_salary_chart(processor, salary_df)
            st.plotly_chart(fig_skill_level_salary, width='stretch')
    
    with col2:
        st.subheader("📈 Rozkład Wynagrodzeń")
        if visualizer:
            fig_salary_dist = visualizer.create_salary_distribution_chart(salary_df)
            st.plotly_chart(fig_salary_dist, width='stretch')
    
    st.divider()
    
    # Salary ranges chart
    st.subheader("📍 Zakresy Wynagrodzeń dla Najlepiej Płacących Umiejętności")
    if visualizer:
        fig_salary_ranges = visualizer.create_salary_range_chart(processor, salary_df)
        st.plotly_chart(fig_salary_ranges, width='stretch')
    
    st.divider()
    
    # Detailed salary statistics table
    st.subheader("📋 Szczegółowe Statystyki Wynagrodzeń według Umiejętności")
    
    # Get detailed salary correlation data
    detailed_salary_data = processor.get_skills_salary_correlation(salary_df, min_occurrences=2)
    
    if not detailed_salary_data.empty:
        # Display top 20 results
        st.dataframe(
            detailed_salary_data.head(20),
            width='stretch',
            column_config={
                "skill": st.column_config.TextColumn("Umiejętność"),
                "avg_salary": st.column_config.NumberColumn("Średnie Wynagrodzenie", format="%.0f PLN"),
                "median_salary": st.column_config.NumberColumn("Mediana", format="%.0f PLN"),
                "min_salary": st.column_config.NumberColumn("Minimum", format="%.0f PLN"),
                "max_salary": st.column_config.NumberColumn("Maksimum", format="%.0f PLN"),
                "count": st.column_config.NumberColumn("Liczba Ofert"),
                "salary_range": st.column_config.NumberColumn("Zakres", format="%.0f PLN")
            }
        )
        
        if len(detailed_salary_data) > 20:
            st.info(f"Wyświetlono top 20 umiejętności z {len(detailed_salary_data)} dostępnych.")
    else:
        st.warning("Brak szczegółowych danych o wynagrodzeniach do wyświetlenia.")