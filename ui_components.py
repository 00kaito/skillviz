"""UI components module for SkillViz Analytics."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auth import AuthManager, show_login_form, show_auth_header
from visualizations import JobMarketVisualizer
from config import SAMPLE_JSON_DATA
from data_management import handle_file_upload, handle_json_paste, clear_all_data, clear_category_data

def apply_date_filter(df, date_range):
    """Apply date filter to dataframe based on selected range."""
    if 'published_date' not in df.columns or df.empty:
        return df
    
    # Make a copy to avoid modifying original
    filtered_df = df.copy()
    
    try:
        # Ensure published_date is datetime
        filtered_df['published_date'] = pd.to_datetime(filtered_df['published_date'], errors='coerce')
        # Remove rows with invalid dates
        filtered_df = filtered_df.dropna(subset=['published_date'])
        
        if filtered_df.empty:
            return df  # Return original if no valid dates
        
        # Calculate date thresholds - handle timezone issues
        now = pd.Timestamp.now()
        
        if date_range == 'last_month':
            threshold = now - pd.Timedelta(days=30)
        elif date_range == 'last_quarter':
            threshold = now - pd.Timedelta(days=90)
        elif date_range == 'last_year':
            threshold = now - pd.Timedelta(days=365)
        else:
            return filtered_df  # Return all data for 'all' or unknown ranges
        
        # Convert to date only (ignore time) for comparison
        filtered_df['date_only'] = filtered_df['published_date'].dt.date
        threshold_date = threshold.date()
        
        # Filter by date only (time doesn't matter)
        filtered_df = filtered_df[filtered_df['date_only'] >= threshold_date]
        
        # Remove the temporary column
        filtered_df = filtered_df.drop('date_only', axis=1)
        
        return filtered_df
        
    except Exception as e:
        st.warning(f"⚠️ Błąd filtrowania dat: {str(e)}")
        return df  # Return original data if filtering fails

def show_guest_header():
    """Show header for guest users."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("🔍 **Tryb Gościa** - Ograniczony dostęp (50 wyników). Zaloguj się dla pełnego dostępu.")
    with col2:
        if st.button("🔐 Zaloguj się"):
            st.session_state.show_login = True

def show_login_section():
    """Show login form section if requested."""
    if st.session_state.get('show_login', False):
        with st.expander("🔐 Logowanie", expanded=True):
            show_login_form()
            if st.button("❌ Anuluj"):
                st.session_state.show_login = False
                st.rerun()
        st.divider()

def show_admin_data_input():
    """Show admin data input section in sidebar."""
    st.header("📂 Wprowadzanie Danych (Tylko Admin)")
    
    # Category input
    st.subheader("🏷️ Zarządzanie Kategoriami")
    # Upload mode selection
    append_mode = st.checkbox("Dodaj do istniejących danych (unikaj duplikatów)", value=st.session_state.append_mode)
    
    st.info("ℹ️ **Kategoria/specjalizacja będzie automatycznie pobrana z pola 'category' w JSON**")
    st.session_state.append_mode = append_mode
    
    # Data input options
    input_method = st.radio("Wybierz metodę wprowadzania:", ["Prześlij plik JSON", "Wklej dane JSON"])
    
    if input_method == "Prześlij plik JSON":
        uploaded_file = st.file_uploader("Prześlij plik JSON z danymi o ofertach pracy", type=['json'])
        if uploaded_file is not None:
            handle_file_upload(uploaded_file, append_mode)
    else:
        json_text = st.text_area("Wklej dane JSON tutaj:", height=200)
        if st.button("Załaduj Dane"):
            handle_json_paste(json_text, append_mode)

def show_admin_data_management():
    """Show admin data management controls in sidebar."""
    if st.session_state.data_loaded:
        st.divider()
        st.subheader("🛠️ Zarządzanie Danymi (Tylko Admin)")
        
        # Show current categories
        if st.session_state.categories:
            st.write("**Dostępne kategorie:**")
            for cat in st.session_state.categories:
                cat_data = st.session_state.processor.get_data_by_category(cat)
                st.write(f"- {cat.title()}: {len(cat_data)} ofert")
        
        # Clear data options
        if st.button("🗑️ Wyczyść Wszystkie Dane", type="secondary"):
            clear_all_data()

def show_user_sidebar_info():
    """Show info section for regular users in sidebar."""
    st.info("👁️ **Tryb Przeglądania**\n\nMożesz przeglądać wszystkie dostępne dane o rynku pracy i analizy. Przesyłanie danych jest ograniczone do administratorów.")

def show_guest_sidebar_info():
    """Show info section for guest users in sidebar."""
    st.info("🔍 **Tryb Gościa**\n\nMożesz przeglądać wszystkie dane dla specjalizacji **Go**. Aby uzyskać dostęp do innych specjalizacji, zaloguj się.")

def show_sidebar_filters(auth_manager, df):
    """Show filters section in sidebar."""
    if st.session_state.data_loaded:
        st.divider()
        st.header("🔍 Filtry")
        
        # Category filter
        category_options = ['all'] + st.session_state.categories
        
        # For guests, show all categories but limit access to 'go' only
        if not auth_manager.is_authenticated():
            # Initialize guest category selection if not set
            if 'guest_selected_category' not in st.session_state:
                st.session_state.guest_selected_category = 'go' if 'go' in st.session_state.categories else 'all'
            
            # Show all categories but monitor selection
            guest_category_options = ['go'] + [cat for cat in st.session_state.categories if cat != 'go']
            if 'go' not in st.session_state.categories:
                guest_category_options = ['all'] + st.session_state.categories
            
            # Get the current index for the selectbox
            try:
                current_index = guest_category_options.index(st.session_state.guest_selected_category)
            except ValueError:
                current_index = 0
            
            selected_category = st.selectbox(
                "Specjalizacja:", 
                guest_category_options,
                index=current_index,
                format_func=lambda x: {
                    'go': 'Go (Dostępne)',
                    'all': 'Go (Przykładowe dane)'
                }.get(x, f"{x.title()} (Niedostępne - Zaloguj się)"),
                key="guest_category_selector"
            )
            
            # Check if guest tries to select non-Go category
            if selected_category != 'go' and selected_category != 'all':
                st.warning("⚠️ Aby uzyskać dostęp do specjalizacji \"{}\" musisz się zalogować. Obecnie możesz przeglądać tylko dane specjalizacji Go.".format(selected_category.title()))
                # Force back to 'go' without rerun to avoid infinite loop
                st.session_state.guest_selected_category = 'go' if 'go' in st.session_state.categories else 'all'
                selected_category = st.session_state.guest_selected_category
            else:
                st.session_state.guest_selected_category = selected_category
            
            st.session_state.selected_category = selected_category
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
        if not filtered_df.empty:
            # Filter out None values before sorting
            city_values = [x for x in filtered_df['city'].unique() if x is not None]
            cities = ['Wszystkie'] + sorted(city_values)
        else:
            cities = ['Wszystkie']
        if auth_manager.is_authenticated():
            selected_city = st.selectbox("Miasto:", cities)
        else:
            selected_city = st.selectbox("Miasto:", ['Wszystkie'], disabled=True, help="Zaloguj się aby filtrować")
        
        # Experience level filter
        if not filtered_df.empty:
            # Filter out None values before sorting
            seniority_values = [x for x in filtered_df['seniority'].unique() if x is not None]
            exp_levels = ['Wszystkie'] + sorted(seniority_values)
        else:
            exp_levels = ['Wszystkie']
        if auth_manager.is_authenticated():
            selected_exp = st.selectbox("Poziom Doświadczenia:", exp_levels)
        else:
            selected_exp = st.selectbox("Poziom Doświadczenia:", ['Wszystkie'], disabled=True, help="Zaloguj się aby filtrować")
        
        # Company filter
        if not filtered_df.empty:
            # Filter out None values before sorting
            company_values = [x for x in filtered_df['company'].unique() if x is not None]
            companies = ['Wszystkie'] + sorted(company_values)
        else:
            companies = ['Wszystkie']
        if auth_manager.is_authenticated():
            selected_company = st.selectbox("Firma:", companies)
        else:
            selected_company = st.selectbox("Firma:", ['Wszystkie'], disabled=True, help="Zaloguj się aby filtrować")
        
        # Date range filter
        date_options = {
            'all': 'Cały okres',
            'last_month': 'Ostatni miesiąc',
            'last_quarter': 'Ostatni kwartał',
            'last_year': 'Ostatni rok'
        }
        
        if auth_manager.is_authenticated():
            selected_date_range = st.selectbox(
                "Okres czasowy:", 
                list(date_options.keys()),
                format_func=lambda x: date_options[x]
            )
        else:
            selected_date_range = st.selectbox(
                "Okres czasowy:", 
                ['all'], 
                format_func=lambda x: 'Cały okres (Wymagane logowanie)',
                disabled=True, 
                help="Zaloguj się aby filtrować według dat"
            )
        
        # Apply additional filters (only for authenticated users)
        if not filtered_df.empty and auth_manager.is_authenticated():
            if selected_city != 'Wszystkie':
                filtered_df = filtered_df[filtered_df['city'] == selected_city]
            if selected_exp != 'Wszystkie':
                filtered_df = filtered_df[filtered_df['seniority'] == selected_exp]
            if selected_company != 'Wszystkie':
                filtered_df = filtered_df[filtered_df['company'] == selected_company]
            
            # Apply date filter
            if selected_date_range != 'all' and 'published_date' in filtered_df.columns:
                filtered_df = apply_date_filter(filtered_df, selected_date_range)
        
        total_jobs = len(df) if df is not None and not df.empty else 0
        filtered_jobs = len(filtered_df) if filtered_df is not None and len(filtered_df) > 0 else 0
        
        if auth_manager.is_authenticated():
            st.info(f"Pokazuje {filtered_jobs} z {total_jobs} ofert")
        else:
            st.warning(f"🔍 **Tryb Gościa**: Pokazuje {filtered_jobs} z {total_jobs} ofert (limit 50)")
        
        # Clear specific category (admin only)
        if auth_manager.is_admin() and selected_category != 'all':
            if st.button(f"🗑️ Wyczyść '{selected_category.title()}'", type="secondary"):
                clear_category_data(selected_category)
        
        return filtered_df

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
        st.json([SAMPLE_JSON_DATA])

def display_data_overview(display_df):
    """Display data overview metrics."""
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
        companies_count = display_df['company'].nunique() if not display_df.empty else 0
        st.metric("Firmy", companies_count)

def show_category_info(auth_manager):
    """Show current category information."""
    if st.session_state.selected_category != 'all':
        st.info(f"📊 Aktualna specjalizacja: **{st.session_state.selected_category.title()}**")
    elif not auth_manager.is_authenticated():
        st.warning("🔍 **Tryb Gościa**: Przeglądasz ograniczone dane (50 wyników). Zaloguj się dla pełnego dostępu.")

def show_user_role_footer(auth_manager):
    """Show user role information at the bottom."""
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