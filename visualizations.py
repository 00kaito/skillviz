import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from collections import Counter
import numpy as np
import streamlit as st

class JobMarketVisualizer:
    """Class for creating visualizations of job market data."""
    
    def __init__(self, df):
        self.df = df
        
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts
    def create_skills_demand_chart(_self, df=None, top_n=20):
        """Create a bar chart showing skills demand."""
        if df is None:
            df = _self.df
            
        # Optimized: use pandas explode instead of loops
        if 'requiredSkills' in df.columns and not df.empty:
            # Use explode to flatten the skills lists efficiently
            skills_series = df['requiredSkills'].explode().dropna()
            skills_counter = Counter(skills_series)
        else:
            skills_counter = Counter()
        
        top_skills = skills_counter.most_common(top_n)
        
        if not top_skills:
            return _self._create_empty_chart("Brak danych o umiejętnościach")
        
        skills, counts = zip(*top_skills)
        
        fig = px.bar(
            x=list(counts),
            y=list(skills),
            orientation='h',
            title=f'Top {top_n} Najbardziej Poszukiwanych Umiejętności',
            labels={'x': 'Liczba Ofert Pracy', 'y': 'Umiejętności'},
            color=list(counts),
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        return fig
    
    def create_experience_distribution_chart(self, df=None):
        """Create a pie chart showing experience level distribution."""
        if df is None:
            df = self.df
            
        exp_counts = df['seniority'].value_counts()
        
        if exp_counts.empty:
            return self._create_empty_chart("Brak danych o poziomach doświadczenia")
        
        fig = px.pie(
            values=exp_counts.values,
            names=exp_counts.index,
            title='Rozkład Ofert według Poziomu Doświadczenia'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts  
    def create_experience_skills_heatmap(_self, df=None, top_skills=15):
        """Create a heatmap showing skills by experience level."""
        if df is None:
            df = _self.df
        
        # Optimized: get top skills using explode
        if 'requiredSkills' in df.columns and not df.empty:
            skills_series = df['requiredSkills'].explode().dropna()
            top_skills_list = [skill for skill, _ in Counter(skills_series).most_common(top_skills)]
        else:
            top_skills_list = []
        
        # Create matrix
        exp_levels = df['seniority'].unique()
        matrix_data = []
        
        for exp_level in exp_levels:
            exp_df = df[df['seniority'] == exp_level]
            row_data = []
            
            for skill in top_skills_list:
                count = sum(1 for skills_list in exp_df['requiredSkills'] if skill in skills_list)
                percentage = (count / len(exp_df)) * 100 if len(exp_df) > 0 else 0
                row_data.append(percentage)
            
            matrix_data.append(row_data)
        
        if not matrix_data:
            return _self._create_empty_chart("Brak danych dla mapy ciepła")
        
        fig = px.imshow(
            matrix_data,
            x=top_skills_list,
            y=exp_levels,
            title='Zapotrzebowanie na Umiejętności według Poziomu Doświadczenia (%)',
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        
        fig.update_layout(
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_city_distribution_chart(self, df=None, top_n=15):
        """Create a bar chart showing job distribution by city."""
        if df is None:
            df = self.df
            
        city_counts = df['city'].value_counts().head(top_n)
        
        if city_counts.empty:
            return self._create_empty_chart("Brak danych o miastach")
        
        fig = px.bar(
            x=city_counts.index,
            y=city_counts.values,
            title=f'Top {top_n} Miast według Liczby Ofert Pracy',
            labels={'x': 'Miasto', 'y': 'Liczba Ofert Pracy'},
            color=city_counts.values,
            color_continuous_scale='blues'
        )
        
        fig.update_layout(
            height=400,
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        return fig
    
    def create_top_companies_chart(self, df=None, top_n=15):
        """Create a bar chart showing top hiring companies."""
        if df is None:
            df = self.df
            
        company_counts = df['company'].value_counts().head(top_n)
        
        if company_counts.empty:
            return self._create_empty_chart("Brak danych o firmach")
        
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title=f'Top {top_n} Rekrutujących Firm',
            labels={'x': 'Liczba Ofert Pracy', 'y': 'Firma'},
            color=company_counts.values,
            color_continuous_scale='greens'
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        return fig
    
    def create_workplace_type_chart(self, df=None):
        """Create a chart showing workplace type distribution."""
        if df is None:
            df = self.df
            
        if 'remote' not in df.columns:
            return self._create_empty_chart("Brak danych o typach miejsca pracy")
        
        # Convert boolean remote to categorical for visualization
        df['workplace_type'] = df['remote'].map({True: 'Remote', False: 'Stacjonarna/Hybrydowa'})
        workplace_counts = df['workplace_type'].value_counts()
        
        if workplace_counts.empty:
            return self._create_empty_chart("Brak danych o typach miejsca pracy")
        
        fig = px.pie(
            values=workplace_counts.values,
            names=workplace_counts.index,
            title='Rozkład Ofert według Typu Miejsca Pracy'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    def create_publishing_trends_chart(self, df=None):
        """Create a line chart showing job publishing trends over time."""
        if df is None:
            df = self.df
            
        if 'published_date' not in df.columns or df['published_date'].isna().all():
            return self._create_empty_chart("Brak danych o datach publikacji")
        
        # Filter out null dates and ensure datetime conversion
        df_with_dates = df.dropna(subset=['published_date']).copy()
        
        if df_with_dates.empty:
            return self._create_empty_chart("Nie znaleziono poprawnych dat publikacji")
        
        try:
            # Always convert to datetime to be safe
            df_with_dates['published_date'] = pd.to_datetime(df_with_dates['published_date'], errors='coerce')
            # Remove any rows where conversion failed
            df_with_dates = df_with_dates.dropna(subset=['published_date'])
                
            if df_with_dates.empty:
                return _self._create_empty_chart("Nie znaleziono poprawnych dat publikacji po konwersji")
            
            # Group by date
            df_with_dates['date'] = df_with_dates['published_date'].dt.date
            daily_counts = df_with_dates.groupby('date').size().reset_index(name='count')
        except Exception as e:
            return _self._create_empty_chart(f"Błąd przetwarzania dat: {str(e)}")
        
        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Oferty Pracy w Czasie',
            labels={'date': 'Data', 'count': 'Liczba Ofert Pracy'}
        )
        
        fig.update_layout(height=400)
        
        return fig
    
    def create_skills_by_experience_chart(self, df=None, top_skills=10):
        """Create a grouped bar chart showing skills distribution by experience level."""
        if df is None:
            df = self.df
        
        # Get top skills
        all_skills = []
        for skills_list in df['requiredSkills']:
            all_skills.extend(skills_list)
        
        top_skills_list = [skill for skill, _ in Counter(all_skills).most_common(top_skills)]
        
        # Prepare data for grouped bar chart
        chart_data = []
        
        for skill in top_skills_list:
            for exp_level in df['seniority'].unique():
                exp_df = df[df['seniority'] == exp_level]
                count = sum(1 for skills_list in exp_df['requiredSkills'] if skill in skills_list)
                
                chart_data.append({
                    'Umiejętność': skill,
                    'Poziom Doświadczenia': exp_level,
                    'Liczba': count
                })
        
        if not chart_data:
            return self._create_empty_chart("Brak danych dla wykresu umiejętności według doświadczenia")
        
        chart_df = pd.DataFrame(chart_data)
        
        fig = px.bar(
            chart_df,
            x='Umiejętność',
            y='Liczba',
            color='Poziom Doświadczenia',
            title=f'Top {top_skills} Umiejętności według Poziomu Doświadczenia',
            barmode='group'
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts
    def create_skills_trends_chart(_self, df=None, top_skills=5):
        """Create a line chart showing skills demand trends over time."""
        if df is None:
            df = _self.df
            
        if 'published_date' not in df.columns or df['published_date'].isna().all():
            return _self._create_empty_chart("Brak danych o datach publikacji dla trendów umiejętności")
        
        # Filter out null dates
        df_with_dates = df.dropna(subset=['published_date'])
        
        if df_with_dates.empty:
            return _self._create_empty_chart("Nie znaleziono poprawnych dat publikacji dla trendów umiejętności")
        
        # Optimized: get top skills using explode
        if 'requiredSkills' in df_with_dates.columns and not df_with_dates.empty:
            skills_series = df_with_dates['requiredSkills'].explode().dropna()
            top_skills_list = [skill for skill, _ in Counter(skills_series).most_common(top_skills)]
        else:
            top_skills_list = []
        
        if not top_skills_list:
            return _self._create_empty_chart("Brak danych o umiejętnościach dla trendów")
        
        try:
            # Always convert to datetime to be safe
            df_with_dates['published_date'] = pd.to_datetime(df_with_dates['published_date'], errors='coerce')
            # Remove any rows where conversion failed
            df_with_dates = df_with_dates.dropna(subset=['published_date'])
                
            if df_with_dates.empty:
                return _self._create_empty_chart("Nie znaleziono poprawnych dat publikacji po konwersji")
                
            # Group by date and skill
            df_with_dates['date'] = df_with_dates['published_date'].dt.date
        except Exception as e:
            return _self._create_empty_chart(f"Błąd przetwarzania dat: {str(e)}")
        
        # Create data for line chart
        trend_data = []
        for date in sorted(df_with_dates['date'].unique()):
            date_df = df_with_dates[df_with_dates['date'] == date]
            
            for skill in top_skills_list:
                count = sum(1 for skills_list in date_df['requiredSkills'] if skill in skills_list)
                trend_data.append({
                    'Data': date,
                    'Umiejętność': skill,
                    'Liczba': count
                })
        
        if not trend_data:
            return _self._create_empty_chart("Brak danych trendowych")
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = px.line(
            trend_df,
            x='Data',
            y='Liczba',
            color='Umiejętność',
            title=f'Top {top_skills} - Zapotrzebowanie na Umiejętności w Czasie',
            labels={'Data': 'Data Publikacji', 'Liczba': 'Liczba Ofert Pracy'}
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_skill_weight_chart(self, df=None, top_n=20):
        """Create a bar chart showing skill importance weighted by proficiency levels."""
        if df is None:
            df = self.df
        
        from data_processor import JobDataProcessor
        processor = JobDataProcessor()
        processor.df = df
        
        # Get skill weight analysis
        weight_analysis = processor.get_skill_weight_analysis(df)
        
        if weight_analysis.empty:
            return self._create_empty_chart("Brak danych o wagach umiejętności")
        
        # Get top skills by importance score
        top_skills = weight_analysis.head(top_n)
        
        fig = px.bar(
            top_skills,
            x='importance_score',
            y='skill',
            orientation='h',
            title=f'Top {top_n} Umiejętności według Wagi Ważności',
            labels={'importance_score': 'Ocena Ważności', 'skill': 'Umiejętności'},
            color='avg_weight',
            color_continuous_scale='viridis',
            hover_data=['frequency', 'avg_weight']
        )
        
        fig.update_layout(
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        return fig
    
    def create_skills_by_level_chart(self, df=None, top_levels=5):
        """Create a stacked bar chart showing skills distribution by proficiency level."""
        if df is None:
            df = self.df
        
        from data_processor import JobDataProcessor
        processor = JobDataProcessor()
        processor.df = df
        
        # Get skills by level analysis
        skills_by_level = processor.get_skills_by_level(df)
        
        if skills_by_level.empty:
            return self._create_empty_chart("Brak danych o poziomach umiejętności")
        
        # Get top skills overall for filtering
        top_skills_series = skills_by_level.groupby('skill')['count'].sum().nlargest(15)
        top_skills = top_skills_series.index.tolist()
        filtered_data = skills_by_level[skills_by_level['skill'].isin(top_skills)]
        
        fig = px.bar(
            filtered_data,
            x='skill',
            y='count',
            color='level',
            title='Rozkład Umiejętności według Poziomów Biegłości',
            labels={'count': 'Liczba Ofert', 'skill': 'Umiejętności', 'level': 'Poziom'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            legend_title_text='Poziom Biegłości'
        )
        
        return fig
    
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts
    def create_skill_importance_matrix(_self, df=None, top_n=15, excluded_skills=None):
        """Create a heatmap showing skill importance vs frequency."""
        if df is None:
            df = _self.df
        
        if excluded_skills is None:
            excluded_skills = []
        
        from data_processor import JobDataProcessor
        processor = JobDataProcessor()
        processor.df = df
        
        # Get skill weight analysis
        weight_analysis = processor.get_skill_weight_analysis(df)
        
        if weight_analysis.empty:
            return self._create_empty_chart("Brak danych do analizy ważności")
        
        # Filter out excluded skills
        if excluded_skills:
            weight_analysis = weight_analysis[~weight_analysis['skill'].isin(excluded_skills)]
        
        # Get top skills after filtering
        top_skills = weight_analysis.head(top_n)
        
        # Update title based on exclusions
        title = 'Macierz Ważności Umiejętności: Częstotliwość vs Ważność'
        if excluded_skills:
            excluded_count = len(excluded_skills)
            title += f' (wykluczono {excluded_count} umiejętności)'
        
        fig = px.scatter(
            top_skills,
            x='frequency',
            y='importance_score',
            size='frequency',
            hover_name='skill',
            title=title,
            labels={
                'frequency': 'Częstotliwość w Ofertach', 
                'importance_score': 'Ocena Ważności',
                'avg_weight': 'Średni Wymagany Poziom'
            },
            color='avg_weight',
            color_continuous_scale='RdYlBu_r',
            hover_data=['avg_weight']
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            coloraxis_colorbar=dict(
                title="Średni Wymagany<br>Poziom",
                title_font_size=12
            )
        )
        
        return fig
    
    def create_skills_salary_correlation_chart(self, processor, df=None, top_n=15):
        """Create a bar chart showing average salary by skill."""
        if df is None:
            df = self.df
        
        # Get salary correlation data
        salary_data = processor.get_skills_salary_correlation(df)
        
        if salary_data.empty:
            return self._create_empty_chart("Brak danych o wynagrodzeniach dla umiejętności")
        
        # Take top N skills by average salary
        top_skills_salary = salary_data.head(top_n)
        
        fig = px.bar(
            top_skills_salary,
            x='avg_salary',
            y='skill',
            orientation='h',
            title=f'Top {top_n} Najlepiej Płacących Umiejętności',
            labels={'avg_salary': 'Średnie Wynagrodzenie (PLN)', 'skill': 'Umiejętność'},
            color='avg_salary',
            color_continuous_scale='viridis',
            text='avg_salary'
        )
        
        fig.update_traces(texttemplate='%{text:,.0f} PLN', textposition='inside')
        fig.update_layout(
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        return fig
    
    def create_seniority_salary_chart(self, processor, df=None):
        """Create a bar chart showing average salary by seniority level."""
        if df is None:
            df = self.df
        
        # Get seniority salary data
        salary_data = processor.get_seniority_salary_analysis(df)
        
        if salary_data.empty:
            return self._create_empty_chart("Brak danych o wynagrodzeniach według doświadczenia")
        
        fig = px.bar(
            salary_data,
            x='seniority',
            y='avg_salary',
            title='Średnie Wynagrodzenia według Poziomu Doświadczenia',
            labels={'seniority': 'Poziom Doświadczenia', 'avg_salary': 'Średnie Wynagrodzenie (PLN)'},
            color='avg_salary',
            color_continuous_scale='blues',
            text='avg_salary'
        )
        
        fig.update_traces(texttemplate='%{text:,.0f} PLN', textposition='outside')
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_skill_level_salary_chart(self, processor, df=None):
        """Create a bar chart showing average salary by skill proficiency level."""
        if df is None:
            df = self.df
        
        # Get skill level salary data
        salary_data = processor.get_salary_by_skill_level(df)
        
        if salary_data.empty:
            return self._create_empty_chart("Brak danych o wynagrodzeniach według poziomu biegłości")
        
        fig = px.bar(
            salary_data,
            x='skill_level',
            y='avg_salary',
            title='Średnie Wynagrodzenia według Poziomu Biegłości w Umiejętnościach',
            labels={'skill_level': 'Poziom Biegłości', 'avg_salary': 'Średnie Wynagrodzenie (PLN)'},
            color='avg_salary',
            color_continuous_scale='oranges',
            text='avg_salary'
        )
        
        fig.update_traces(texttemplate='%{text:,.0f} PLN', textposition='outside')
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_salary_distribution_chart(self, df=None):
        """Create a histogram showing salary distribution."""
        if df is None:
            df = self.df
        
        if 'salary_avg' not in df.columns:
            return self._create_empty_chart("Brak danych o wynagrodzeniach")
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg'])
        
        if salary_df.empty:
            return self._create_empty_chart("Brak danych o wynagrodzeniach")
        
        fig = px.histogram(
            salary_df,
            x='salary_avg',
            nbins=20,
            title='Rozkład Wynagrodzeń',
            labels={'salary_avg': 'Wynagrodzenie (PLN)', 'count': 'Liczba Ofert'},
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_salary_range_chart(self, processor, df=None, top_n=10):
        """Create a chart showing salary ranges for top paying skills."""
        if df is None:
            df = self.df
        
        # Get salary correlation data
        salary_data = processor.get_skills_salary_correlation(df)
        
        if salary_data.empty:
            return self._create_empty_chart("Brak danych o zakresach wynagrodzeń")
        
        # Take top N skills by average salary
        top_skills_salary = salary_data.head(top_n)
        
        fig = go.Figure()
        
        for _, row in top_skills_salary.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['min_salary'], row['max_salary']],
                y=[row['skill'], row['skill']],
                mode='lines+markers',
                line=dict(width=4),
                marker=dict(size=8),
                name=row['skill'],
                text=[f"Min: {row['min_salary']:,.0f} PLN", f"Max: {row['max_salary']:,.0f} PLN"],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            # Add average salary point
            fig.add_trace(go.Scatter(
                x=[row['avg_salary']],
                y=[row['skill']],
                mode='markers',
                marker=dict(size=12, color='red', symbol='diamond'),
                name=f"{row['skill']} (średnia)",
                text=[f"Średnia: {row['avg_salary']:,.0f} PLN"],
                hovertemplate='%{text}<extra></extra>',
                showlegend=False
            ))
        
        fig.update_layout(
            title=f'Zakresy Wynagrodzeń dla Top {top_n} Najlepiej Płacących Umiejętności',
            xaxis_title='Wynagrodzenie (PLN)',
            yaxis_title='Umiejętność',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_correlation_heatmap(self, processor, df):
        """Create correlation matrix heatmap."""
        correlation_df = processor.get_correlation_matrix_data(df, top_skills=8)
        
        if correlation_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Brak danych do analizy korelacji",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            fig.update_layout(
                title="Macierz Korelacji",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='white'
            )
            return fig
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_df.values,
            x=correlation_df.columns,
            y=correlation_df.index,
            colorscale='RdBu',
            zmid=0,
            zmin=-1,
            zmax=1,
            text=correlation_df.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(
                title="Współczynnik Korelacji"
            )
        ))
        
        fig.update_layout(
            title="Macierz Korelacji: Wynagrodzenia vs Umiejętności",
            xaxis_title="Czynniki",
            yaxis_title="Czynniki",
            font=dict(size=10),
            height=600,
            width=700
        )
        
        return fig
    
    def create_seniority_regression_chart(self, processor, df):
        """Create seniority vs salary regression chart."""
        regression_results = processor.get_regression_analysis(df)
        
        if 'seniority' not in regression_results:
            fig = go.Figure()
            fig.add_annotation(
                text="Brak wystarczających danych do regresji",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Filter data with salary information
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        # Map seniority to numeric values
        seniority_mapping = {
            'Junior': 1, 'Mid': 2, 'Regular': 2, 'Senior': 3, 
            'Expert': 4, 'Lead': 4, 'Principal': 5
        }
        
        salary_df['seniority_numeric'] = salary_df['seniority'].map(seniority_mapping)
        salary_df['seniority_numeric'] = salary_df['seniority_numeric'].fillna(2)
        
        # Create scatter plot
        fig = go.Figure()
        
        # Add data points
        fig.add_trace(go.Scatter(
            x=salary_df['seniority_numeric'],
            y=salary_df['salary_avg'],
            mode='markers',
            name='Dane',
            marker=dict(
                size=8,
                color='lightblue',
                opacity=0.7
            ),
            hovertemplate='Poziom: %{x}<br>Wynagrodzenie: %{y:,.0f} PLN<extra></extra>'
        ))
        
        # Add regression line
        reg_data = regression_results['seniority']
        x_range = np.linspace(1, 5, 100)
        y_pred = reg_data['slope'] * x_range + reg_data['intercept']
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            name=f'Regresja (R² = {reg_data["r_squared"]:.3f})',
            line=dict(color='red', width=2),
            hovertemplate='Przewidywane: %{y:,.0f} PLN<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Regresja Liniowa: Poziom Doświadczenia vs Wynagrodzenie<br><sub>{reg_data["equation"]}</sub>',
            xaxis_title="Poziom Doświadczenia (1=Junior, 2=Mid, 3=Senior, 4=Expert, 5=Principal)",
            yaxis_title="Średnie Wynagrodzenie (PLN)",
            showlegend=True,
            hovermode='closest'
        )
        
        # Set x-axis ticks
        fig.update_xaxes(
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['Junior', 'Mid', 'Senior', 'Expert', 'Principal']
        )
        
        return fig
    
    def create_skills_count_regression_chart(self, processor, df):
        """Create skills count vs salary regression chart."""
        regression_results = processor.get_regression_analysis(df)
        
        if 'skills_count' not in regression_results:
            fig = go.Figure()
            fig.add_annotation(
                text="Brak wystarczających danych do regresji",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Filter data with salary information
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        # Create scatter plot
        fig = go.Figure()
        
        # Add data points
        fig.add_trace(go.Scatter(
            x=salary_df['skillsCount'],
            y=salary_df['salary_avg'],
            mode='markers',
            name='Dane',
            marker=dict(
                size=8,
                color='lightgreen',
                opacity=0.7
            ),
            hovertemplate='Liczba umiejętności: %{x}<br>Wynagrodzenie: %{y:,.0f} PLN<extra></extra>'
        ))
        
        # Add regression line
        reg_data = regression_results['skills_count']
        x_min, x_max = salary_df['skillsCount'].min(), salary_df['skillsCount'].max()
        x_range = np.linspace(x_min, x_max, 100)
        y_pred = reg_data['slope'] * x_range + reg_data['intercept']
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            name=f'Regresja (R² = {reg_data["r_squared"]:.3f})',
            line=dict(color='red', width=2),
            hovertemplate='Przewidywane: %{y:,.0f} PLN<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Regresja Liniowa: Liczba Umiejętności vs Wynagrodzenie<br><sub>{reg_data["equation"]}</sub>',
            xaxis_title="Liczba Wymaganych Umiejętności",
            yaxis_title="Średnie Wynagrodzenie (PLN)",
            showlegend=True,
            hovermode='closest'
        )
        
        return fig
    
    def create_correlation_bar_chart(self, processor, df):
        """Create correlation coefficients bar chart."""
        correlations = processor.get_correlation_analysis(df)
        
        if not correlations:
            fig = go.Figure()
            fig.add_annotation(
                text="Brak danych do analizy korelacji",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Filter skill correlations (exclude meta correlations)
        skill_correlations = {k: v for k, v in correlations.items() 
                            if k not in ['seniority_level', 'skills_count']}
        
        if not skill_correlations:
            fig = go.Figure()
            fig.add_annotation(
                text="Brak korelacji umiejętności do wyświetlenia",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Sort by correlation strength
        sorted_correlations = sorted(skill_correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        skills = [item[0] for item in sorted_correlations[:15]]  # Top 15
        correlation_values = [item[1] for item in sorted_correlations[:15]]
        
        # Color based on positive/negative correlation
        colors = ['green' if corr > 0 else 'red' for corr in correlation_values]
        
        fig = go.Figure(data=[
            go.Bar(
                x=skills,
                y=correlation_values,
                marker_color=colors,
                text=[f'{corr:.3f}' for corr in correlation_values],
                textposition='auto',
                hovertemplate='%{x}<br>Korelacja: %{y:.3f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Korelacja Umiejętności z Wynagrodzeniami<br><sub>Dodatnia = wyższe wynagrodzenia, Ujemna = niższe wynagrodzenia</sub>",
            xaxis_title="Umiejętności",
            yaxis_title="Współczynnik Korelacji",
            showlegend=False
        )
        
        # Add horizontal line at 0
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        # Rotate x-axis labels
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    # ============ SKILL-SPECIFIC VISUALIZATIONS ============
    
    def create_skill_level_distribution_chart(self, skill_analytics):
        """Create a pie chart showing skill level distribution for a specific skill."""
        if not skill_analytics or 'level_distribution' not in skill_analytics:
            return self._create_empty_chart("Brak danych o poziomach umiejętności")
        
        level_dist = skill_analytics['level_distribution']
        if not level_dist:
            return self._create_empty_chart("Brak danych o poziomach umiejętności")
        
        levels = list(level_dist.keys())
        counts = list(level_dist.values())
        
        fig = px.pie(
            values=counts,
            names=levels,
            title='Rozkład Poziomów Umiejętności'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    def create_skill_seniority_analysis_chart(self, seniority_df):
        """Create a bar chart showing skill frequency across seniority levels."""
        if seniority_df.empty:
            return self._create_empty_chart("Brak danych o poziomach seniority")
        
        fig = px.bar(
            seniority_df,
            x='seniority',
            y='percentage',
            title='Częstotliwość Umiejętności według Poziomu Seniority',
            labels={'seniority': 'Poziom Seniority', 'percentage': 'Procent ofert (%)'},
            color='percentage',
            color_continuous_scale='viridis',
            text='skill_offers'
        )
        
        fig.update_traces(texttemplate='%{text} ofert', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        
        return fig
    
    def create_skill_salary_by_level_chart(self, salary_level_df):
        """Create a bar chart showing salary differences by skill level."""
        if salary_level_df.empty:
            return self._create_empty_chart("Brak danych o wynagrodzeniach według poziomów")
        
        fig = px.bar(
            salary_level_df,
            x='Poziom umiejętności',
            y='Średnia',
            title='Średnie Wynagrodzenie według Poziomu Umiejętności',
            labels={'Średnia': 'Średnie wynagrodzenie (PLN)'},
            color='Średnia',
            color_continuous_scale='viridis',
            text='Liczba ofert'
        )
        
        fig.update_traces(texttemplate='%{text} ofert', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        
        return fig
    
    def create_skill_trends_chart(self, trends_df):
        """Create a line chart showing skill trends over time."""
        if trends_df.empty:
            return self._create_empty_chart("Brak danych o trendach")
        
        fig = go.Figure()
        
        # Add offers count line
        fig.add_trace(go.Scatter(
            x=trends_df['Data'],
            y=trends_df['Liczba ofert'],
            mode='lines+markers',
            name='Liczba ofert',
            line=dict(color='blue', width=2),
            yaxis='y'
        ))
        
        # Add average salary line (if available)
        if 'Średnia pensja' in trends_df.columns and not trends_df['Średnia pensja'].isna().all():
            fig.add_trace(go.Scatter(
                x=trends_df['Data'],
                y=trends_df['Średnia pensja'],
                mode='lines+markers',
                name='Średnia pensja',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
        
        fig.update_layout(
            title='Trendy Umiejętności w Czasie',
            xaxis_title='Data',
            yaxis=dict(title='Liczba ofert', side='left'),
            yaxis2=dict(title='Średnia pensja (PLN)', side='right', overlaying='y'),
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_skill_market_overview_chart(self, skill_analytics, skill_name):
        """Create a comprehensive overview chart for a skill."""
        if not skill_analytics:
            return self._create_empty_chart(f"Brak danych dla umiejętności: {skill_name}")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Rozkład Poziomów',
                'Rozkład Seniority', 
                'Top Firmy',
                'Top Miasta'
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # Level distribution pie chart
        if 'level_distribution' in skill_analytics and skill_analytics['level_distribution']:
            levels = list(skill_analytics['level_distribution'].keys())
            level_counts = list(skill_analytics['level_distribution'].values())
            fig.add_trace(
                go.Pie(labels=levels, values=level_counts, name="Poziomy"),
                row=1, col=1
            )
        
        # Seniority distribution bar chart
        if 'seniority_distribution' in skill_analytics and skill_analytics['seniority_distribution']:
            seniorities = list(skill_analytics['seniority_distribution'].keys())
            seniority_counts = list(skill_analytics['seniority_distribution'].values())
            fig.add_trace(
                go.Bar(x=seniorities, y=seniority_counts, name="Seniority", showlegend=False),
                row=1, col=2
            )
        
        # Top companies bar chart
        if 'top_companies' in skill_analytics and skill_analytics['top_companies']:
            companies = list(skill_analytics['top_companies'].keys())[:5]  # Top 5
            company_counts = list(skill_analytics['top_companies'].values())[:5]
            fig.add_trace(
                go.Bar(x=companies, y=company_counts, name="Firmy", showlegend=False),
                row=2, col=1
            )
        
        # Top cities bar chart
        if 'top_cities' in skill_analytics and skill_analytics['top_cities']:
            cities = list(skill_analytics['top_cities'].keys())[:5]  # Top 5
            city_counts = list(skill_analytics['top_cities'].values())[:5]
            fig.add_trace(
                go.Bar(x=cities, y=city_counts, name="Miasta", showlegend=False),
                row=2, col=2
            )
        
        fig.update_layout(
            height=600,
            title_text=f"Przegląd Rynkowy: {skill_name}",
            showlegend=False
        )
        
        return fig
    
    def _create_empty_chart(self, message):
        """Create an empty chart with a message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=400,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig
    
    def create_skills_weight_chart_from_df(self, weight_df, top_n=20):
        """Create a bar chart from pre-computed weight analysis DataFrame."""
        if weight_df.empty:
            return self._create_empty_chart("Brak danych o wagach umiejętności")
        
        # Get top skills by importance score
        top_skills = weight_df.head(top_n)
        
        fig = px.bar(
            top_skills,
            x='importance_score',
            y='skill',
            orientation='h',
            title=f'Top {top_n} Umiejętności według Wagi Ważności (Pre-agregowane)',
            labels={'importance_score': 'Ocena Ważności', 'skill': 'Umiejętności'},
            color='avg_weight',
            color_continuous_scale='viridis',
            hover_data=['frequency', 'avg_weight']
        )
        
        fig.update_layout(
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        
        return fig
