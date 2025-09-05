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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Analiza Umiejętności", 
        "🎯 Poziomy Doświadczenia", 
        "🌍 Analiza Lokalizacji", 
        "🏢 Analiza Firm", 
        "📈 Trendy Rynkowe",
        "💰 Analiza Dochodów",
        "🔍 Szczegółowa Analiza Umiejętności"
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
    
    with tab7:
        show_detailed_skill_analysis(display_df, visualizer, processor)

def show_skills_analysis(display_df, visualizer, processor):
    """Show skills analysis tab content."""
    st.header("Analiza Umiejętności")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Top skills chart
        with st.expander("ℹ️ Jak interpretować wykres najpopularniejszych umiejętności?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Ranking najczęściej wymaganych umiejętności w ofertach pracy
            - Liczba ofert zawierających każdą umiejętność
            
            **Jak czytać:**
            - Oś X: Liczba wystąpień umiejętności
            - Oś Y: Nazwy umiejętności (sortowane malejąco)
            - Im dłuższy słupek, tym więcej ofert wymaga tej umiejętności
            
            **Zastosowanie:**
            - Identyfikacja najważniejszych umiejętności na rynku
            - Planowanie ścieżki rozwoju zawodowego
            - Analiza trendów technologicznych w branży
            """)
        if visualizer:
            fig_skills = visualizer.create_skills_demand_chart(display_df)
            st.plotly_chart(fig_skills, width='stretch')
    
    with col2:
        # Skills statistics - USE PRE-COMPUTED DATA
        st.subheader("Statystyki Umiejętności")
        try:
            # Get pre-computed skills data
            is_guest = st.session_state.get('user_role') == 'guest'
            precomputed_skills = processor.get_precomputed_skills_data(is_guest=is_guest)
            top_skills = precomputed_skills.get('top_skills', {}).get('top_20', {})
            
            if top_skills:
                total_jobs = len(display_df) if len(display_df) > 0 else 1
                for skill, count in list(top_skills.items())[:10]:
                    percentage = (count / total_jobs) * 100
                    st.metric(skill, f"{count} ofert", f"{percentage:.1f}%")
            else:
                # Fallback to original method if no pre-computed data
                skills_stats = processor.get_skills_statistics(display_df)
                for skill, count in skills_stats.head(10).items():
                    percentage = (count / len(display_df)) * 100 if len(display_df) > 0 else 0
                    st.metric(skill, f"{count} ofert", f"{percentage:.1f}%")
        except Exception as e:
            st.error(f"Błąd ładowania statystyk: {e}")
    
    # Skill combinations - USE PRE-COMPUTED DATA
    st.subheader("Najczęstsze Kombinacje Umiejętności")
    try:
        is_guest = st.session_state.get('user_role') == 'guest'
        precomputed_skills = processor.get_precomputed_skills_data(is_guest=is_guest)
        combinations_data = precomputed_skills.get('skills_combinations', {}).get('top_20', {})
        
        if combinations_data:
            # Convert to DataFrame format
            combo_df = pd.DataFrame([
                {'Kombinacja': combo, 'Liczba wystąpień': count} 
                for combo, count in combinations_data.items()
            ])
            st.dataframe(combo_df.head(15), width='stretch')
        else:
            # Fallback to original method
            combinations = processor.get_skill_combinations(display_df)
            if not combinations.empty:
                st.dataframe(combinations.head(15), width='stretch')
    except Exception as e:
        st.error(f"Błąd ładowania kombinacji: {e}")
    
    st.divider()
    
    # NEW: Skill importance weight analysis
    st.header("Analiza Wagi Umiejętności według Poziomów")
    st.markdown("*Analiza uwzględniająca nie tylko częstotliwość umiejętności, ale także wymagany poziom biegłości*")
    
    col1, col2 = st.columns(2)
    with col1:
        # Skill weight chart
        with st.expander("ℹ️ Jak interpretować wykres wagi umiejętności?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Ważność umiejętności uwzględniając zarówno częstotliwość jak i wymagany poziom
            - Ocena ważności = liczba wystąpień × średni poziom zaawansowania
            
            **Jak czytać:**
            - Oś X: Ocena ważności (wyższa = ważniejsza umiejętność)
            - Oś Y: Nazwy umiejętności
            - Uwzględnia nie tylko liczbę ofert, ale też wymagany poziom
            
            **Zastosowanie:**
            - Identyfikacja umiejętności o największej wartości rynkowej
            - Priorytetyzacja nauki nowych technologii
            - Ocena, które umiejętności dają największą przewagę
            """)
        if visualizer:
            # Use pre-computed weight analysis data  
            try:
                is_guest = st.session_state.get('user_role') == 'guest'
                precomputed_skills = processor.get_precomputed_skills_data(is_guest=is_guest)
                weight_data = precomputed_skills.get('skills_weight_analysis', {})
                
                if weight_data:
                    # Convert pre-computed data to DataFrame format expected by visualizer
                    weight_df_data = []
                    for skill, data in weight_data.items():
                        weight_df_data.append({
                            'skill': skill,
                            'frequency': data.get('count', 0),
                            'total_weight': data.get('total_weight', 0),
                            'avg_weight': data.get('avg_weight', 0),
                            'importance_score': data.get('importance_score', 0),
                            'level_distribution': data.get('levels', {})
                        })
                    
                    if weight_df_data:
                        weight_df = pd.DataFrame(weight_df_data).sort_values('importance_score', ascending=False)
                        fig_weight = visualizer.create_skills_weight_chart_from_df(weight_df)
                        st.plotly_chart(fig_weight, width='stretch')
                    else:
                        # Fallback to original method
                        fig_weight = visualizer.create_skill_weight_chart(display_df)
                        st.plotly_chart(fig_weight, width='stretch')
                else:
                    # Fallback to original method
                    fig_weight = visualizer.create_skill_weight_chart(display_df)
                    st.plotly_chart(fig_weight, width='stretch')
            except Exception as e:
                # Fallback to original method on error
                fig_weight = visualizer.create_skill_weight_chart(display_df)
                st.plotly_chart(fig_weight, width='stretch')
    
    with col2:
        # Skills by level chart
        with st.expander("ℹ️ Jak interpretować wykres umiejętności według poziomów?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Rozkład poziomów wymaganych dla każdej umiejętności
            - Stosunek różnych poziomów zaawansowania (Junior, Regular, Senior, Expert)
            
            **Jak czytać:**
            - Kolorowe segmenty przedstawiają różne poziomy:
              • Zielony: Junior
              • Niebieski: Regular/Mid
              • Pomarańczowy: Senior
              • Czerwony: Expert
            - Wysokość słupka = całkowita liczba ofert dla umiejętności
            
            **Zastosowanie:**
            - Ocena jak "seniorska" jest dana technologia
            - Planowanie progresji w konkretnej umiejętności
            - Identyfikacja umiejętności dla różnych poziomów doświadczenia
            """)
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
    
    with st.expander("ℹ️ Jak interpretować macierz ważności umiejętności?", expanded=False):
        st.write("""
        **Co pokazuje:**
        - Intensywność kolorów reprezentuje ważność umiejętności
        - Każda komórka pokazuje kombinację umiejętności i poziomu
        
        **Jak czytać:**
        - Ciemniejsze kolory = wyższa ważność
        - Oś X: Poziomy zaawansowania (Junior → Expert)
        - Oś Y: Nazwy umiejętności
        - Wartości liczbowe w komórkach = ocena ważności
        
        **Zastosowanie:**
        - Wizualna identyfikacja najbardziej pożądanych kombinacji skill+poziom
        - Porównanie wymagań dla różnych technologii
        - Strategiczne planowanie rozwoju kompetencji
        """)
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
        st.dataframe(display_data, width='stretch')

def show_experience_analysis(display_df, visualizer):
    """Show experience level analysis tab content."""
    # Check if user is authenticated - for guests, show login message
    from auth import AuthManager
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.header("Analiza Poziomów Doświadczenia")
        st.warning("🔒 **Ta sekcja jest dostępna tylko dla zalogowanych użytkowników.**\n\nAby zobaczyć analizy poziomów doświadczenia, zaloguj się na swoje konto.")
        st.info("👆 Kliknij przycisk 'Zaloguj się' w prawym górnym rogu strony.")
        return
        
    st.header("Analiza Poziomów Doświadczenia")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("ℹ️ Jak interpretować rozkład poziomów doświadczenia?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Podział ofert pracy według wymagań doświadczeniowych
            - Liczba ofert dla każdego poziomu seniority
            
            **Jak czytać:**
            - Wysokość słupków = liczba ofert dla danego poziomu
            - Kategorie: Junior, Mid, Senior, Expert
            - Pozwala ocenić zapotrzebowanie na poszczególne poziomy
            
            **Zastosowanie:**
            - Ocena możliwości zatrudnienia na swoim poziomie
            - Identyfikacja najchętniej poszukiwanych seniorów
            - Planowanie progresji kariery
            """)
        if visualizer:
            fig_exp = visualizer.create_experience_distribution_chart(display_df)
            st.plotly_chart(fig_exp, width='stretch')
    
    with col2:
        with st.expander("ℹ️ Jak interpretować heatmapę umiejętności vs doświadczenie?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Zależność między poziomem doświadczenia a wymaganymi umiejętnościami
            - Intensywność koloru = częstość wystąpień kombinacji
            
            **Jak czytać:**
            - Oś X: Poziomy doświadczenia (Junior → Expert)
            - Oś Y: Najważniejsze umiejętności
            - Ciemniejsze komórki = częśtsza kombinacja skill+seniority
            - Jasne komórki = rzadka lub nieistniejąca kombinacja
            
            **Zastosowanie:**
            - Identyfikacja umiejętności typowych dla każdego poziomu
            - Planowanie rozwoju kompetencji na wyższy poziom
            - Ocena, które technologie są "entry-level" vs "senior"
            """)
        if visualizer:
            fig_exp_skills = visualizer.create_experience_skills_heatmap(display_df)
            st.plotly_chart(fig_exp_skills, width='stretch')

def show_location_analysis(display_df, visualizer, processor):
    """Show location analysis tab content."""
    # Check if user is authenticated - for guests, show login message
    from auth import AuthManager
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.header("Analiza Według Lokalizacji")
        st.warning("🔒 **Ta sekcja jest dostępna tylko dla zalogowanych użytkowników.**\n\nAby zobaczyć analizy geograficzne rynku pracy, zaloguj się na swoje konto.")
        st.info("👆 Kliknij przycisk 'Zaloguj się' w prawym górnym rogu strony.")
        return
        
    st.header("Analiza Według Lokalizacji")
    
    # City job distribution
    with st.expander("ℹ️ Jak interpretować rozkład ofert w miastach?", expanded=False):
        st.write("""
        **Co pokazuje:**
        - Liczba ofert pracy dostępnych w różnych miastach
        - Koncentracja rynku pracy geograficznie
        
        **Jak czytać:**
        - Wysokość słupków = liczba ofert w danym mieście
        - Miasta sortowane malejąco według liczby ofert
        - Możliwa kategoria "Remote" dla pracy zdalnej
        
        **Zastosowanie:**
        - Identyfikacja najlepszych miast dla poszukujących pracy
        - Ocena lokalnych rynków pracy IT
        - Planowanie relokacji zawodowej
        - Porównanie możliwości pracy zdalnej vs stacjonarnej
        """)
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
    # Check if user is authenticated - for guests, show login message
    from auth import AuthManager
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.header("Analiza Firm")
        st.warning("🔒 **Ta sekcja jest dostępna tylko dla zalogowanych użytkowników.**\n\nAby zobaczyć analizy firm i pracodawców, zaloguj się na swoje konto.")
        st.info("👆 Kliknij przycisk 'Zaloguj się' w prawym górnym rogu strony.")
        return
        
    st.header("Analiza Firm")
    
    col1, col2 = st.columns(2)
    with col1:
        # Top hiring companies
        with st.expander("ℹ️ Jak interpretować ranking firm zatrudniających?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Firmy z największą liczbą aktywnych ofert pracy
            - Aktywność rekrutacyjna poszczególnych pracodawców
            
            **Jak czytać:**
            - Wysokość słupków = liczba ofert opublikowanych przez firmę
            - Firmy sortowane malejąco
            - Większa aktywność = więcej możliwości zatrudnienia
            
            **Zastosowanie:**
            - Identyfikacja firm w fazie ekspansji/wzrostu
            - Targetowanie aplikacji do aktywnych pracodawców
            - Ocena wielkości i aktywności firm IT
            - Monitoring trendów zatrudnienia w konkretnych firmach
            """)
        if visualizer:
            fig_companies = visualizer.create_top_companies_chart(display_df)
            st.plotly_chart(fig_companies, width='stretch')
    
    with col2:
        # Remote work analysis
        with st.expander("ℹ️ Jak interpretować analizę typów pracy?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Podział ofert według modalności pracy (remote vs office)
            - Preferencje pracodawców co do miejsca wykonywania pracy
            
            **Jak czytać:**
            - Kołowy wykres z proporcjami:
              • Remote: praca w pełni zdalna
              • Office: praca stacjonarna
              • Hybrid: praca hybrydowa (jeśli obecna)
            - Procenty pokazują udział każdego typu
            
            **Zastosowanie:**
            - Ocena dostępności pracy zdalnej na rynku
            - Dopasowanie preferencji do ofert
            - Identyfikacja trendów w modalnosti pracy
            - Planowanie strategii poszukiwania pracy
            """)
        if visualizer:
            fig_remote = visualizer.create_workplace_type_chart(display_df)
            st.plotly_chart(fig_remote, width='stretch')

def show_trends_analysis(display_df, visualizer, processor):
    """Show market trends tab content."""
    # Check if user is authenticated - for guests, show login message
    from auth import AuthManager
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.header("Trendy Rynkowe")
        st.warning("🔒 **Ta sekcja jest dostępna tylko dla zalogowanych użytkowników.**\n\nAby zobaczyć analizy trendów czasowych i rynkowych, zaloguj się na swoje konto.")
        st.info("👆 Kliknij przycisk 'Zaloguj się' w prawym górnym rogu strony.")
        return
        
    st.header("Trendy Rynkowe")
    
    # Publishing trends over time
    with st.expander("ℹ️ Jak interpretować trendy publikacji ofert w czasie?", expanded=False):
        st.write("""
        **Co pokazuje:**
        - Liczba opublikowanych ofert pracy w różnych okresach
        - Sezonowość i trendy rekrutacyjne w czasie
        
        **Jak czytać:**
        - Oś X: Daty publikacji (chronologicznie)
        - Oś Y: Liczba ofert opublikowanych w danym okresie
        - Linia trendu pokazuje ogólny kierunek zmian
        - Piki = okresy intensywnej rekrutacji
        
        **Zastosowanie:**
        - Identyfikacja najlepszych okresów do poszukiwania pracy
        - Ocena aktywności rynku pracy IT
        - Planowanie strategii aplikacyjnej w optymalnym czasie
        - Prognozowanie przyszłych trendów zatrudnienia
        """)
    if visualizer and 'published_date' in display_df.columns:
        fig_trends = visualizer.create_publishing_trends_chart(display_df)
        st.plotly_chart(fig_trends, width='stretch')
    
    # Skills trends over time
    st.subheader("Zapotrzebowanie na Umiejętności w Czasie")
    with st.expander("ℹ️ Jak interpretować trendy umiejętności w czasie?", expanded=False):
        st.write("""
        **Co pokazuje:**
        - Zmianę popularności poszczególnych umiejętności w czasie
        - Trendy wzrostowe i spadkowe dla technologii
        
        **Jak czytać:**
        - Oś X: Czas (daty publikacji ofert)
        - Oś Y: Liczba ofert wymagających danej umiejętności
        - Różne linie = różne umiejętności/technologie
        - Rosnące linie = rosnące zapotrzebowanie
        - Opadające linie = malejące zapotrzebowanie
        
        **Zastosowanie:**
        - Identyfikacja nowopowstających trendów technologicznych
        - Decyzje o inwestycji w naukę nowych umiejętności
        - Prognozowanie przyszłej wartości kompetencji
        - Wybór specjalizacji oparty na trendach rynkowych
        """)
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
    # Check if user is authenticated - for guests, show login message
    from auth import AuthManager
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.header("Analiza Dochodów")
        st.warning("🔒 **Ta sekcja jest dostępna tylko dla zalogowanych użytkowników.**\n\nAby zobaczyć szczegółowe analizy wynagrodzeń i korelacji, zaloguj się na swoje konto.")
        st.info("👆 Kliknij przycisk 'Zaloguj się' w prawym górnym rogu strony.")
        return
        
    st.header("Analiza Dochodów")
    
    # Check if salary data is available
    if 'salary_avg' not in display_df.columns or display_df['salary_avg'].isna().all():
        st.warning("⚠️ Brak danych o wynagrodzeniach do analizy. Upewnij się, że przesłane dane zawierają pole 'salary' z informacjami o wynagrodzeniach.")
        return
    
    # Filter out rows without salary data and extreme salaries (>70k PLN)
    salary_df = display_df.dropna(subset=['salary_avg'])
    
    # Convert any remaining hourly rates to monthly (for existing data)
    salary_df = salary_df.copy()
    salary_df.loc[salary_df['salary_avg'] < 300, 'salary_avg'] = salary_df.loc[salary_df['salary_avg'] < 300, 'salary_avg'] * 168
    salary_df.loc[salary_df['salary_min'] < 300, 'salary_min'] = salary_df.loc[salary_df['salary_min'] < 300, 'salary_min'] * 168
    salary_df.loc[salary_df['salary_max'] < 300, 'salary_max'] = salary_df.loc[salary_df['salary_max'] < 300, 'salary_max'] * 168
    
    # Remove extreme salary outliers (above 70,000 PLN and below 30 PLN/h equivalent = 5,040 PLN/month)
    original_count = len(salary_df)
    salary_df = salary_df[(salary_df['salary_avg'] >= 5040) & (salary_df['salary_avg'] <= 70000)]
    filtered_count = original_count - len(salary_df)
    
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
        # Use actual min/max from the filtered average salaries for more accurate range
        min_salary = salary_df['salary_avg'].min()
        max_salary = salary_df['salary_avg'].max()
        st.metric("Zakres Wynagrodzeń", f"{min_salary:,.0f} - {max_salary:,.0f} PLN")
    
    with col4:
        if filtered_count > 0:
            st.metric("Ofert w analizie", f"{len(salary_df)} z {len(display_df)}")
            st.caption(f"Odfiltrowano {filtered_count} ofert z ekstremalnymi wynagrodzeniami")
        else:
            st.metric("Ofert z danymi o wynagrodzeniach", f"{len(salary_df)} z {len(display_df)}")
    
    st.divider()
    
    # Correlation analysis section
    st.subheader("🔍 Analiza Korelacji z Wynagrodzeniami")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Współczynniki Korelacji dla Umiejętności**")
        with st.expander("ℹ️ Jak interpretować korelację umiejętności z wynagrodzeniami?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Siłę związku między posiadaniem umiejętności a wysokością wynagrodzenia
            - Współczynnik korelacji Pearsona dla każdej umiejętności
            
            **Jak czytać:**
            - Wartości od -1.0 do +1.0
            - +1.0 = perfekcyjna korelacja dodatnia (umiejętność = wyższe zarobki)
            - 0.0 = brak korelacji
            - -1.0 = perfekcyjna korelacja ujemna (umiejętność = niższe zarobki)
            - Im większa wartość bezwzględna, tym silniejszy związek
            
            **Interpretacja:**
            - >0.5: Silna pozytywna korelacja (wyższe zarobki)
            - 0.3-0.5: Umiarkowana pozytywna korelacja  
            - 0.1-0.3: Słaba pozytywna korelacja
            - -0.1 do 0.1: Brak korelacji
            - -0.3 do -0.1: Słaba negatywna korelacja (niższe zarobki)
            - -0.5 do -0.3: Umiarkowana negatywna korelacja
            - <-0.5: Silna negatywna korelacja
            
            **Przykłady ujemnych korelacji:**
            - Umiejętności junior-level często korelują negatywnie z zarobkami
            - Podstawowe narzędzia mogą być wymagane w gorzej płatnych pozycjach
            - Niektóre technologie mogą być używane głównie w mniejszych firmach
            """)
        if visualizer:
            fig_correlation_bar = visualizer.create_correlation_bar_chart(processor, salary_df)
            st.plotly_chart(fig_correlation_bar, width='stretch', key='correlation_bar')
    
    with col2:
        st.write("**Macierz Korelacji (Heatmap)**")
        with st.expander("ℹ️ Jak interpretować macierz korelacji wynagrodzenia?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Korelację między różnymi czynnikami a wynagrodzeniem w formie ciepłokrwistej mapy
            - Siłę związków za pomocą intensywności kolorów
            
            **Jak czytać:**
            - Skala kolorów od ciemnoniebieskigo (-1) do ciemnoczerwono (+1)
            - Czerwone = silna korelacja pozytywna
            - Niebieskie = korelacja negatywna
            - Białe/szare = brak korelacji
            - Wartości liczbowe w komórkach = dokładny współczynnik
            
            **Zastosowanie:**
            - Szybka identyfikacja najbardziej "opłacalnych" umiejętności
            - Porównanie wpływu różnych czynników na wynagrodzenie
            - Wizualna analiza zależności finansowych
            """)
        if visualizer:
            fig_correlation_heatmap = visualizer.create_correlation_heatmap(processor, salary_df)
            st.plotly_chart(fig_correlation_heatmap, width='stretch', key='correlation_heatmap')
    
    st.divider()
    
    # Regression analysis section
    st.subheader("📈 Analiza Regresji Liniowej")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Regresja: Poziom Doświadczenia vs Wynagrodzenie**")
        with st.expander("ℹ️ Jak interpretować regresję doświadczenia vs wynagrodzenie?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Matematyczny związek między poziomem seniority a wynagrodzeniem
            - Linia regresji liniowej z przewidywanymi wartościami
            
            **Jak czytać:**
            - Oś X: Poziom doświadczenia (1=Junior, 2=Mid, 3=Senior, 4=Expert)
            - Oś Y: Wynagrodzenie w PLN
            - Niebieska linia = przewidywane wynagrodzenia (regresja)
            - Punkty = rzeczywiste dane
            - R² = jak dobrze model dopasowuje dane (0-1, wyższe = lepiej)
            
            **Zastosowanie:**
            - Oszacowanie oczekiwanego wynagrodzenia dla poziomu
            - Ocena, czy progresja kariery skutkuje wzrostem wynagrodzeń
            - Porównanie własnego wynagrodzenia z trendem rynkowym
            """)
        if visualizer:
            fig_seniority_regression = visualizer.create_seniority_regression_chart(processor, salary_df)
            st.plotly_chart(fig_seniority_regression, width='stretch', key='seniority_regression')
    
    with col2:
        st.write("**Regresja: Liczba Umiejętności vs Wynagrodzenie**")
        with st.expander("ℹ️ Jak interpretować regresję liczby umiejętności vs wynagrodzenie?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Związek między liczbą wymaganych umiejętności a wysokością wynagrodzenia
            - Czy więcej umiejętności = większe zarobki?
            
            **Jak czytać:**
            - Oś X: Liczba wymaganych umiejętności w ofercie
            - Oś Y: Wynagrodzenie w PLN
            - Linia trendu pokazuje ogólną zależność
            - Nachylenie linii = jak bardzo liczba skills wpływa na pensję
            - R² = wiarygodność przewidywania
            
            **Zastosowanie:**
            - Ocena, czy warto rozwijać szerokie kompetencje
            - Przewidywanie wynagrodzenia na podstawie skill setu
            - Strategia rozwoju: głębokość vs szerokość umiejętności
            """)
        if visualizer:
            fig_skills_count_regression = visualizer.create_skills_count_regression_chart(processor, salary_df)
            st.plotly_chart(fig_skills_count_regression, width='stretch', key='skills_count_regression')
    
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
    detailed_salary_data = processor.get_skills_salary_correlation(salary_df, min_occurrences=3)
    
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

def show_detailed_skill_analysis(display_df, visualizer, processor):
    """Show detailed analysis for a specific skill."""
    # Check if user is authenticated - for guests, show login message
    from auth import AuthManager
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        st.header("🔍 Szczegółowa Analiza Umiejętności")
        st.warning("🔒 **Ta sekcja jest dostępna tylko dla zalogowanych użytkowników.**\n\nAby zobaczyć szczegółową analizę poszczególnych umiejętności, zaloguj się na swoje konto.")
        st.info("👆 Kliknij przycisk 'Zaloguj się' w prawym górnym rogu strony.")
        return
        
    st.header("🔍 Szczegółowa Analiza Umiejętności")
    st.markdown("*Wybierz umiejętność aby zobaczyć szczegółowe statystyki rynkowe*")
    
    # Performance info
    if st.session_state.get('show_performance_info', False):
        st.info("⚡ **Usprawnienia wydajności aktywne** - dane są ładowane z pre-computed cache dla maksymalnej szybkości")
    
    # Get all available skills - USE PRE-COMPUTED DATA
    @st.cache_data(ttl=300)  # 5 min cache
    def get_cached_all_skills(data_hash, is_guest=False):
        """Get cached list of all skills."""
        # Try pre-computed data first for speed
        precomputed_detailed = processor.get_precomputed_detailed_skills_data(is_guest=is_guest)
        if precomputed_detailed:
            return sorted(list(precomputed_detailed.keys()))
        else:
            # Fallback to original method
            return processor.get_all_skills_list(display_df)
    
    is_guest = st.session_state.get('user_role') == 'guest'
    data_hash = hash(str(len(display_df)) + str(display_df.columns.tolist()) + str(is_guest))
    all_skills = get_cached_all_skills(data_hash, is_guest)
    
    if not all_skills:
        st.warning("⚠️ Brak danych o umiejętnościach do analizy.")
        return
    
    # Skill selection with search
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_skill = st.selectbox(
            "🔍 Wyszukaj i wybierz umiejętność:",
            options=all_skills,
            index=0,
            help="Wybierz umiejętność z listy aby zobaczyć szczegółowe analizy (⚡ dane ładowane z cache)"
        )
        
        # Instant feedback on selection
        if selected_skill:
            if st.session_state.get('show_performance_info', False):
                st.success(f"⚡ Wybrano: **{selected_skill}** - dane ładowane błyskawicznie z pre-computed cache")
    
    with col2:
        st.metric("Dostępne umiejętności", len(all_skills))
    
    if not selected_skill:
        st.info("👆 Wybierz umiejętność z listy powyżej aby rozpocząć analizę.")
        return
    
    # Get analytics for selected skill - OPTIMIZED WITH INSTANT LOADING
    @st.cache_data(ttl=3600, show_spinner=False)  # 1 hour cache + no spinner for instant feel
    def get_cached_skill_analytics(skill_name, data_hash, is_guest=False):
        """Cached version of skill detailed analytics (SUPER OPTIMIZED)."""
        # Force use of pre-computed data for instant loading
        return processor.get_skill_detailed_analytics(skill_name, display_df, use_precomputed=True)
    
    # Create a hash of the data to invalidate cache when data changes
    is_guest = st.session_state.get('user_role') == 'guest'
    data_hash = hash(str(len(display_df)) + str(display_df.columns.tolist()) + str(is_guest))
    
    # INSTANT LOADING with progress indication
    with st.spinner("⚡ Ładuję dane..."):
        skill_analytics = get_cached_skill_analytics(selected_skill, data_hash, is_guest)
    
    if not skill_analytics:
        st.error(f"❌ Nie udało się pobrać danych dla umiejętności: {selected_skill}")
        st.info("💡 **Wskazówka**: Ta umiejętność może nie być w top 100 najczęściej wymaganych. Spróbuj wybrać inną umiejętność.")
        return
    
    # Display skill overview
    st.subheader(f"📊 Przegląd Umiejętności: {selected_skill}")
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Oferty z tą umiejętnością", skill_analytics.get('total_offers', 0))
    
    with col2:
        market_share = skill_analytics.get('market_share', 0)
        st.metric("Udział w rynku", f"{market_share:.1f}%")
    
    with col3:
        if skill_analytics.get('salary_stats'):
            avg_salary = skill_analytics['salary_stats']['mean']
            st.metric("Średnie wynagrodzenie", f"{avg_salary:,.0f} PLN")
        else:
            st.metric("Średnie wynagrodzenie", "Brak danych")
    
    with col4:
        level_dist = skill_analytics.get('level_distribution', {})
        most_common_level = max(level_dist, key=level_dist.get) if level_dist else "N/A"
        st.metric("Najczęstszy poziom", most_common_level)
    
    st.divider()
    
    # Detailed analytics sections
    col1, col2 = st.columns(2)
    
    with col1:
        # Level distribution chart
        st.subheader("🎯 Rozkład Poziomów Umiejętności")
        with st.expander("ℹ️ Jak interpretować rozkład poziomów?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Jakie poziomy biegłości w tej umiejętności są najczęściej wymagane
            - Rozkład wymagań: Junior, Regular, Senior, Expert
            
            **Jak czytać:**
            - Większe segmenty = częściej wymagane poziomy
            - Procenty pokazują udział każdego poziomu
            
            **Zastosowanie:**
            - Ocena na jakim poziomie warto rozwijać umiejętność
            - Identyfikacja najbardziej poszukiwanych poziomów biegłości
            """)
        
        if visualizer:
            fig_levels = visualizer.create_skill_level_distribution_chart(skill_analytics)
            st.plotly_chart(fig_levels, width='stretch', key=f'skill_levels_{selected_skill}')
    
    with col2:
        # Seniority analysis
        st.subheader("👨‍💼 Analiza według Seniority")
        with st.expander("ℹ️ Jak interpretować analizę seniority?", expanded=False):
            st.write("""
            **Co pokazuje:**
            - Na których poziomach kariery ta umiejętność jest najczęściej wymagana
            - Procent ofert dla każdego poziomu seniority
            
            **Jak czytać:**
            - Wysokość słupków = procent ofert wymagających tej umiejętności
            - Liczby na słupkach = konkretna liczba ofert
            
            **Zastosowanie:**
            - Ocena czy umiejętność jest typowa dla juniorów czy seniorów
            - Planowanie rozwoju kariery
            """)
        
        # Cache seniority analysis - INSTANT LOADING
        @st.cache_data(ttl=3600, show_spinner=False)  # 1 hour cache + no spinner
        def get_cached_seniority_analysis(skill_name, data_hash):
            return processor.get_skill_vs_seniority_analysis(skill_name, display_df)
        
        seniority_df = get_cached_seniority_analysis(selected_skill, data_hash)
        if not seniority_df.empty and visualizer:
            fig_seniority = visualizer.create_skill_seniority_analysis_chart(seniority_df)
            st.plotly_chart(fig_seniority, width='stretch', key=f'skill_seniority_{selected_skill}')
        else:
            st.info("Brak wystarczających danych o poziomach seniority")
    
    st.divider()
    
    # Salary analysis
    if skill_analytics.get('salary_stats'):
        st.subheader("💰 Analiza Wynagrodzeń")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Salary statistics table
            salary_stats = skill_analytics['salary_stats']
            st.write("**Statystyki wynagrodzeń:**")
            
            stats_data = {
                'Metryka': ['Liczba ofert', 'Średnia', 'Mediana', 'Minimum', 'Maksimum', 'Odchylenie standardowe'],
                'Wartość': [
                    f"{salary_stats['count']} ofert",
                    f"{salary_stats['mean']:,.0f} PLN",
                    f"{salary_stats['median']:,.0f} PLN", 
                    f"{salary_stats['min']:,.0f} PLN",
                    f"{salary_stats['max']:,.0f} PLN",
                    f"{salary_stats['std']:,.0f} PLN"
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), width='stretch')
        
        with col2:
            # Salary by skill level
            st.write("**Wynagrodzenia według poziomu umiejętności:**")
            with st.expander("ℹ️ Jak interpretować wynagrodzenia według poziomu?", expanded=False):
                st.write("""
                **Co pokazuje:**
                - Jak zmienia się wynagrodzenie w zależności od poziomu biegłości
                - Średnie pensje dla Junior, Regular, Senior, Expert
                
                **Jak czytać:**
                - Wysokość słupków = średnie wynagrodzenie dla poziomu
                - Liczby na słupkach = ile ofert uwzględniono w analizie
                
                **Zastosowanie:**
                - Ocena opłacalności rozwoju umiejętności na wyższy poziom
                - Negocjowanie wynagrodzenia na podstawie poziomu
                """)
            
            # Cache salary by level analysis
            @st.cache_data(ttl=300)
            def get_cached_salary_by_level(skill_name, data_hash):
                return processor.get_skill_salary_by_level_analysis(skill_name, display_df)
            
            salary_by_level = get_cached_salary_by_level(selected_skill, data_hash)
            if not salary_by_level.empty and visualizer:
                fig_salary_level = visualizer.create_skill_salary_by_level_chart(salary_by_level)
                st.plotly_chart(fig_salary_level, width='stretch', key=f'skill_salary_{selected_skill}')
            else:
                st.info("Brak wystarczających danych o wynagrodzeniach według poziomów")
    else:
        st.subheader("💰 Analiza Wynagrodzeń")
        st.info("⚠️ Brak danych o wynagrodzeniach dla tej umiejętności")
    
    st.divider()
    
    # Market trends
    st.subheader("📈 Trendy Rynkowe")
    with st.expander("ℹ️ Jak interpretować trendy rynkowe?", expanded=False):
        st.write("""
        **Co pokazuje:**
        - Jak zmieniała się popularność umiejętności w czasie
        - Trend wynagrodzeń dla tej umiejętności
        
        **Jak czytać:**
        - Niebieska linia = liczba ofert w czasie
        - Czerwona linia = średnie wynagrodzenie w czasie
        - Rosnące linie = zwiększające się zapotrzebowanie/wynagrodzenia
        
        **Zastosowanie:**
        - Ocena czy umiejętność zyskuje czy traci na popularności
        - Prognozowanie przyszłej wartości umiejętności
        """)
    
    # Cache market trends analysis - INSTANT LOADING
    @st.cache_data(ttl=3600, show_spinner=False)  # 1 hour cache + no spinner
    def get_cached_market_trends(skill_name, data_hash):
        return processor.get_skill_market_trends(skill_name, display_df)
    
    trends_df = get_cached_market_trends(selected_skill, data_hash)
    if not trends_df.empty and visualizer:
        fig_trends = visualizer.create_skill_trends_chart(trends_df)
        st.plotly_chart(fig_trends, width='stretch', key=f'skill_trends_{selected_skill}')
    else:
        st.info("Brak danych o trendach czasowych (wymagane pole 'published_date')")
    
    st.divider()
    
    # Additional insights
    st.subheader("🏢 Dodatkowe Informacje")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top companies
        st.write("**Top firmy wymagające tej umiejętności:**")
        top_companies = skill_analytics.get('top_companies', {})
        if top_companies:
            for i, (company, count) in enumerate(list(top_companies.items())[:5], 1):
                st.write(f"{i}. **{company}** - {count} ofert")
        else:
            st.info("Brak danych o firmach")
    
    with col2:
        # Top cities
        st.write("**Top miasta z ofertami tej umiejętności:**")
        top_cities = skill_analytics.get('top_cities', {})
        if top_cities:
            for i, (city, count) in enumerate(list(top_cities.items())[:5], 1):
                st.write(f"{i}. **{city}** - {count} ofert")
        else:
            st.info("Brak danych o miastach")
    
    # Comprehensive overview chart
    st.subheader("🎯 Kompleksowy Przegląd")
    with st.expander("ℹ️ Jak interpretować kompleksowy przegląd?", expanded=False):
        st.write("""
        **Co pokazuje:**
        - Cztery kluczowe aspekty umiejętności w jednym miejscu:
          1. Rozkład poziomów biegłości
          2. Rozkład według seniority
          3. Top firmy rekrutujące
          4. Top miasta z ofertami
        
        **Zastosowanie:**
        - Szybki przegląd wszystkich aspektów umiejętności
        - Porównanie różnych charakterystyk w jednym miejscu
        - Identyfikacja najlepszych kierunków rozwoju
        """)
    
    if visualizer:
        fig_overview = visualizer.create_skill_market_overview_chart(skill_analytics, selected_skill)
        st.plotly_chart(fig_overview, width='stretch', key=f'skill_overview_{selected_skill}')