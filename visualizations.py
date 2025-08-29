import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from collections import Counter
import numpy as np

class JobMarketVisualizer:
    """Class for creating visualizations of job market data."""
    
    def __init__(self, df):
        self.df = df
        
    def create_skills_demand_chart(self, df=None, top_n=20):
        """Create a bar chart showing skills demand."""
        if df is None:
            df = self.df
            
        # Get skills statistics
        all_skills = []
        for skills_list in df['requiredSkills']:
            all_skills.extend(skills_list)
        
        skills_counter = Counter(all_skills)
        top_skills = skills_counter.most_common(top_n)
        
        if not top_skills:
            return self._create_empty_chart("Brak danych o umiejętnościach")
        
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
            
        exp_counts = df['experienceLevel'].value_counts()
        
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
    
    def create_experience_skills_heatmap(self, df=None, top_skills=15):
        """Create a heatmap showing skills by experience level."""
        if df is None:
            df = self.df
        
        # Get top skills first
        all_skills = []
        for skills_list in df['requiredSkills']:
            all_skills.extend(skills_list)
        
        top_skills_list = [skill for skill, _ in Counter(all_skills).most_common(top_skills)]
        
        # Create matrix
        exp_levels = df['experienceLevel'].unique()
        matrix_data = []
        
        for exp_level in exp_levels:
            exp_df = df[df['experienceLevel'] == exp_level]
            row_data = []
            
            for skill in top_skills_list:
                count = sum(1 for skills_list in exp_df['requiredSkills'] if skill in skills_list)
                percentage = (count / len(exp_df)) * 100 if len(exp_df) > 0 else 0
                row_data.append(percentage)
            
            matrix_data.append(row_data)
        
        if not matrix_data:
            return self._create_empty_chart("Brak danych dla mapy ciepła")
        
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
            
        company_counts = df['companyName'].value_counts().head(top_n)
        
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
            
        if 'workplaceType' not in df.columns:
            return self._create_empty_chart("Brak danych o typach miejsca pracy")
        
        workplace_counts = df['workplaceType'].value_counts()
        
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
                return self._create_empty_chart("Nie znaleziono poprawnych dat publikacji po konwersji")
            
            # Group by date
            df_with_dates['date'] = df_with_dates['published_date'].dt.date
            daily_counts = df_with_dates.groupby('date').size().reset_index(name='count')
        except Exception as e:
            return self._create_empty_chart(f"Błąd przetwarzania dat: {str(e)}")
        
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
            for exp_level in df['experienceLevel'].unique():
                exp_df = df[df['experienceLevel'] == exp_level]
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
    
    def create_skills_trends_chart(self, df=None, top_skills=5):
        """Create a line chart showing skills demand trends over time."""
        if df is None:
            df = self.df
            
        if 'published_date' not in df.columns or df['published_date'].isna().all():
            return self._create_empty_chart("Brak danych o datach publikacji dla trendów umiejętności")
        
        # Filter out null dates
        df_with_dates = df.dropna(subset=['published_date'])
        
        if df_with_dates.empty:
            return self._create_empty_chart("Nie znaleziono poprawnych dat publikacji dla trendów umiejętności")
        
        # Get top skills first
        all_skills = []
        for skills_list in df_with_dates['requiredSkills']:
            all_skills.extend(skills_list)
        
        top_skills_list = [skill for skill, _ in Counter(all_skills).most_common(top_skills)]
        
        if not top_skills_list:
            return self._create_empty_chart("Brak danych o umiejętnościach dla trendów")
        
        try:
            # Always convert to datetime to be safe
            df_with_dates['published_date'] = pd.to_datetime(df_with_dates['published_date'], errors='coerce')
            # Remove any rows where conversion failed
            df_with_dates = df_with_dates.dropna(subset=['published_date'])
                
            if df_with_dates.empty:
                return self._create_empty_chart("Nie znaleziono poprawnych dat publikacji po konwersji")
                
            # Group by date and skill
            df_with_dates['date'] = df_with_dates['published_date'].dt.date
        except Exception as e:
            return self._create_empty_chart(f"Błąd przetwarzania dat: {str(e)}")
        
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
            return self._create_empty_chart("Brak danych trendowych")
        
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
        top_skills = skills_by_level.groupby('skill')['count'].sum().nlargest(15).index
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
    
    def create_skill_importance_matrix(self, df=None, top_n=15):
        """Create a heatmap showing skill importance vs frequency."""
        if df is None:
            df = self.df
        
        from data_processor import JobDataProcessor
        processor = JobDataProcessor()
        processor.df = df
        
        # Get skill weight analysis
        weight_analysis = processor.get_skill_weight_analysis(df)
        
        if weight_analysis.empty:
            return self._create_empty_chart("Brak danych do analizy ważności")
        
        # Get top skills
        top_skills = weight_analysis.head(top_n)
        
        fig = px.scatter(
            top_skills,
            x='frequency',
            y='avg_weight',
            size='importance_score',
            hover_name='skill',
            title='Macierz Ważności Umiejętności: Częstotliwość vs Średni Poziom',
            labels={
                'frequency': 'Częstotliwość w Ofertach', 
                'avg_weight': 'Średni Wymagany Poziom',
                'importance_score': 'Ocena Ważności'
            },
            color='importance_score',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=500,
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
