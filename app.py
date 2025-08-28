import streamlit as st
import json
import pandas as pd
from data_processor import JobDataProcessor
from visualizations import JobMarketVisualizer
from auth import AuthManager, show_login_form, show_auth_header
import io

def main():
    st.set_page_config(
        page_title="Job Market Analytics for Engineers",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    st.title("📊 SkillViz Analytics for Engineers")
    st.markdown("### Analyze skill requirements, experience levels, and location-based hiring trends")
    
    # Show authentication header if logged in, or allow guest access
    if auth_manager.is_authenticated():
        show_auth_header()
    else:
        # Guest access header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("🔍 **Tryb Gościa** - Ograniczony dostęp (50 wyników). Zaloguj się dla pełnego dostępu.")
        with col2:
            if st.button("🔐 Zaloguj się"):
                st.session_state.show_login = True
        
        # Show login form if requested
        if st.session_state.get('show_login', False):
            with st.expander("🔐 Logowanie", expanded=True):
                show_login_form()
                if st.button("❌ Anuluj"):
                    st.session_state.show_login = False
                    st.rerun()
        st.divider()
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.processor = JobDataProcessor()
        
        # Get appropriate data based on authentication status
        is_guest = not auth_manager.is_authenticated()
        current_data = st.session_state.processor.get_data(is_guest=is_guest)
        
        if not current_data.empty:
            st.session_state.data_loaded = True
            st.session_state.df = current_data
            st.session_state.categories = st.session_state.processor.get_categories(is_guest=is_guest)
            st.session_state.visualizer = JobMarketVisualizer(st.session_state.df)
        else:
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.session_state.categories = []
            st.session_state.visualizer = None
        st.session_state.selected_category = 'all'
        st.session_state.append_mode = True
    
    # Sidebar for data input and filters
    with st.sidebar:
        # Admin-only data input section
        if auth_manager.is_admin():
            st.header("📂 Data Input (Admin Only)")
            
            # Category input
            st.subheader("🏷️ Category Management")
            category = st.text_input("Enter category for upload:", placeholder="e.g., Java, Python, Data Science")
            
            # Upload mode selection
            append_mode = st.checkbox("Append to existing data (avoid duplicates)", value=st.session_state.append_mode)
            st.session_state.append_mode = append_mode
            
            # Data input options
            input_method = st.radio("Choose input method:", ["Upload JSON file", "Paste JSON data"])
            
            if input_method == "Upload JSON file":
                uploaded_file = st.file_uploader("Upload job data JSON file", type=['json'])
                if uploaded_file is not None:
                    try:
                        json_data = json.load(uploaded_file)
                        if process_data(json_data, category=category, append_to_existing=append_mode):
                            added_count = len(json_data)
                            category_text = f" to category '{category}'" if category else ""
                            st.success(f"✅ {added_count} jobs loaded successfully{category_text}!")
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
                            if process_data(json_data, category=category, append_to_existing=append_mode):
                                added_count = len(json_data)
                                category_text = f" to category '{category}'" if category else ""
                                st.success(f"✅ {added_count} jobs loaded successfully{category_text}!")
                        except json.JSONDecodeError:
                            st.error("❌ Invalid JSON format. Please check your data.")
                        except Exception as e:
                            st.error(f"❌ Error processing data: {str(e)}")
                    else:
                        st.warning("⚠️ Please paste JSON data first.")
            
            # Data management controls
            if st.session_state.data_loaded:
                st.divider()
                st.subheader("🛠️ Data Management (Admin Only)")
                
                # Show current categories
                if st.session_state.categories:
                    st.write("**Available categories:**")
                    for cat in st.session_state.categories:
                        cat_data = st.session_state.processor.get_data_by_category(cat)
                        st.write(f"- {cat.title()}: {len(cat_data)} jobs")
                
                # Clear data options
                if st.button("🗑️ Clear All Data", type="secondary"):
                    st.session_state.processor.clear_category_data()
                    st.session_state.data_loaded = False
                    st.session_state.df = None
                    st.session_state.categories = []
                    st.session_state.visualizer = None
                    st.rerun()
        
        elif auth_manager.is_authenticated():
            # User info for non-admin users
            st.info("👁️ **Viewing Mode**\n\nYou can browse all available job market data and analytics. Data upload is restricted to administrators.")
        else:
            # Guest user info
            st.info("🔍 **Tryb Gościa**\n\nMożesz przeglądać ograniczone dane (50 wyników). Zaloguj się dla pełnego dostępu i wszystkich funkcji.")
            
    
    # Main content area - allow guest access
    if (st.session_state.get('data_loaded', False) and st.session_state.df is not None) or not auth_manager.is_authenticated():
        display_analytics()
    else:
        display_welcome_screen()

def process_data(json_data, category=None, append_to_existing=True):
    """Process the loaded JSON data with category support."""
    try:
        processor = st.session_state.processor
        df = processor.process_json_data(json_data, category=category, append_to_existing=append_to_existing)
        
        if df.empty and not append_to_existing:
            st.error("❌ No valid job data found in the provided JSON.")
            return False
        
        st.session_state.df = df
        st.session_state.processor = processor
        
        # Update categories list
        st.session_state.categories = processor.get_categories()
        
        # Update visualizer with current data
        if not df.empty:
            st.session_state.visualizer = JobMarketVisualizer(df)
            st.session_state.data_loaded = True
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        return False

def display_welcome_screen():
    """Display welcome screen with instructions."""
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.info("📊 **Witaj w SkillViz Analytics!**\n\nMożesz przeglądać ograniczone dane o rynku pracy (50 wyników). Zaloguj się dla pełnego dostępu do wszystkich funkcji i danych.")
        if not st.session_state.get('data_loaded', False):
            st.warning("📁 Brak danych do wyświetlenia. Skontaktuj się z administratorem lub spróbuj później.")
    elif auth_manager.is_admin():
        st.info("👈 Prześlij plik JSON lub wklej dane w pasku bocznym aby rozpocząć analizę.")
    else:
        st.info("📊 Witaj w SkillViz Analytics!\n\nMożesz przeglądać i analizować wszystkie dane o rynku pracy. Przesyłanie nowych danych zarządzają administratorzy.")
        if not st.session_state.get('data_loaded', False):
            st.warning("📁 Brak danych. Skontaktuj się z administratorem aby przesłać dane o rynku pracy.")
    
    with st.expander("📋 Oczekiwany Format JSON"):
        st.markdown("Dane o rynku pracy powinny zawierać tablicę obiektów ofert pracy o następującej strukturze:")
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
    
    # Guest data is already limited in the processor, no need to apply additional limits here
    
    # Create visualizer with filtered data
    if not display_df.empty:
        visualizer = JobMarketVisualizer(display_df)
    else:
        visualizer = None
    
    # Data overview
    col1, col2, col3, col4 = st.columns(4)
    
    total_jobs = len(display_df) if not display_df.empty else 0
    
    with col1:
        st.metric("Łączna liczba ofert", total_jobs)
    with col2:
        if not display_df.empty:
            all_skills = []
            for skills_list in display_df['requiredSkills']:
                all_skills.extend(skills_list)
            unique_skills = len(set(all_skills))
        else:
            unique_skills = 0
        st.metric("Unikalne umiejętności", unique_skills)
    with col3:
        cities_count = display_df['city'].nunique() if not display_df.empty else 0
        st.metric("Miasta", cities_count)
    with col4:
        companies_count = display_df['companyName'].nunique() if not display_df.empty else 0
        st.metric("Firmy", companies_count)
    
    st.divider()
    
    # Filters in sidebar
    with st.sidebar:
        if st.session_state.data_loaded:
            st.divider()
            st.header("🔍 Filtry")
            
            # Category filter
            category_options = ['all'] + st.session_state.categories
            
            # For guests, disable the selectbox and limit to 'all'
            if not auth_manager.is_authenticated():
                selected_category = st.selectbox(
                    "Specjalizacja:", 
                    ['all'], 
                    format_func=lambda x: 'Wszystkie Specjalizacje (Ograniczone do 50)',
                    disabled=True,
                    help="Zaloguj się aby filtrować według specjalizacji"
                )
                st.session_state.selected_category = 'all'
            else:
                selected_category = st.selectbox(
                    "Specjalizacja:", 
                    category_options, 
                    format_func=lambda x: x.title() if x != 'all' else 'Wszystkie Specjalizacje'
                )
                st.session_state.selected_category = selected_category
            
            # Get data for selected category
            if selected_category == 'all':
                filtered_df = df.copy() if df is not None else pd.DataFrame()
            else:
                filtered_df = st.session_state.processor.get_data_by_category(selected_category)
            
            # Limit data for guest users
            if not auth_manager.is_authenticated() and not filtered_df.empty:
                filtered_df = filtered_df.head(50)
            
            # City filter
            cities = ['All'] + sorted(filtered_df['city'].unique().tolist()) if not filtered_df.empty else ['All']
            if auth_manager.is_authenticated():
                selected_city = st.selectbox("Miasto:", cities)
            else:
                selected_city = st.selectbox("Miasto:", ['All'], disabled=True, help="Zaloguj się aby filtrować")
            
            # Experience level filter
            exp_levels = ['All'] + sorted(filtered_df['experienceLevel'].unique().tolist()) if not filtered_df.empty else ['All']
            if auth_manager.is_authenticated():
                selected_exp = st.selectbox("Poziom Doświadczenia:", exp_levels)
            else:
                selected_exp = st.selectbox("Poziom Doświadczenia:", ['All'], disabled=True, help="Zaloguj się aby filtrować")
            
            # Company filter
            companies = ['All'] + sorted(filtered_df['companyName'].unique().tolist()) if not filtered_df.empty else ['All']
            if auth_manager.is_authenticated():
                selected_company = st.selectbox("Firma:", companies)
            else:
                selected_company = st.selectbox("Firma:", ['All'], disabled=True, help="Zaloguj się aby filtrować")
            
            # Apply additional filters (only for authenticated users)
            if not filtered_df.empty and auth_manager.is_authenticated():
                if selected_city != 'All':
                    filtered_df = filtered_df[filtered_df['city'] == selected_city]
                if selected_exp != 'All':
                    filtered_df = filtered_df[filtered_df['experienceLevel'] == selected_exp]
                if selected_company != 'All':
                    filtered_df = filtered_df[filtered_df['companyName'] == selected_company]
            
            total_jobs = len(df) if df is not None and not df.empty else 0
            filtered_jobs = len(filtered_df) if not filtered_df.empty else 0
            
            if auth_manager.is_authenticated():
                st.info(f"Pokazuje {filtered_jobs} z {total_jobs} ofert")
            else:
                st.warning(f"🔍 **Tryb Gościa**: Pokazuje {filtered_jobs} z {total_jobs} ofert (limit 50)")
            
            # Clear specific category (admin only)
            if auth_manager.is_admin() and selected_category != 'all':
                if st.button(f"🗑️ Clear '{selected_category.title()}'", type="secondary"):
                    st.session_state.processor.clear_category_data(selected_category)
                    st.session_state.categories = st.session_state.processor.get_categories()
                    if not st.session_state.categories:
                        st.session_state.data_loaded = False
                        st.session_state.df = None
                        st.session_state.visualizer = None
                    else:
                        st.session_state.df = st.session_state.processor.df
                        st.session_state.visualizer = JobMarketVisualizer(st.session_state.df)
                    st.rerun()
    
    # Show current category info
    if st.session_state.selected_category != 'all':
        st.info(f"📊 Aktualna specjalizacja: **{st.session_state.selected_category.title()}**")
    elif not auth_manager.is_authenticated():
        st.warning("🔍 **Tryb Gościa**: Przeglądasz ograniczone dane (50 wyników). Zaloguj się dla pełnego dostępu.")
    
    if display_df.empty:
        if auth_manager.is_authenticated():
            st.warning("⚠️ Brak danych dla wybranej specjalizacji. Administrator musi najpierw przesłać dane.")
        else:
            st.warning("⚠️ Brak danych do wyświetlenia. Skontaktuj się z administratorem lub zaloguj się.")
        return
    
    # Apply additional filters from sidebar to display_df
    if 'filtered_df' in locals() and not filtered_df.empty:
        display_df = filtered_df.copy()
    
    # Main analytics tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Skills Analysis", "🎯 Experience Levels", "🌍 Location Analysis", "🏢 Company Insights", "📈 Trends"])
    
    with tab1:
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
    
    with tab2:
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
    
    with tab3:
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
    
    with tab4:
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
    
    with tab5:
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
    
    
    # Show user role info
    if not auth_manager.is_authenticated():
        col1, col2 = st.columns(2)
        with col1:
            st.info("🔍 **Tryb Gościa**: Możesz przeglądać ograniczone analizy (limit 50 wyników).")
        with col2:
            if st.button("🔐 Zaloguj się dla pełnego dostępu"):
                st.session_state.show_login = True
                st.rerun()
    elif not auth_manager.is_admin():
        st.info("🗂️ **Tryb Przeglądania**: Możesz eksplorować wszystkie analizy. Zarządzanie danymi wymaga uprawnień administratora.")

if __name__ == "__main__":
    main()
