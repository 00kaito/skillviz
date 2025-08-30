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
            - -1.0 = korelacja ujemna (rzadkie w praktyce)
            - Im większa wartość, tym silniejszy związek
            
            **Interpretacja:**
            - >0.5: Silna pozytywna korelacja
            - 0.3-0.5: Umiarkowana korelacja  
            - 0.1-0.3: Słaba korelacja
            - <0.1: Bardzo słaba/brak korelacji
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