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
            return self._create_empty_chart("No skills data available")
        
        skills, counts = zip(*top_skills)
        
        fig = px.bar(
            x=list(counts),
            y=list(skills),
            orientation='h',
            title=f'Top {top_n} Most Demanded Skills',
            labels={'x': 'Number of Job Postings', 'y': 'Skills'},
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
            return self._create_empty_chart("No experience level data available")
        
        fig = px.pie(
            values=exp_counts.values,
            names=exp_counts.index,
            title='Job Distribution by Experience Level'
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
            return self._create_empty_chart("No data available for heatmap")
        
        fig = px.imshow(
            matrix_data,
            x=top_skills_list,
            y=exp_levels,
            title='Skills Demand by Experience Level (%)',
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
            return self._create_empty_chart("No city data available")
        
        fig = px.bar(
            x=city_counts.index,
            y=city_counts.values,
            title=f'Top {top_n} Cities by Job Postings',
            labels={'x': 'City', 'y': 'Number of Job Postings'},
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
            return self._create_empty_chart("No company data available")
        
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title=f'Top {top_n} Hiring Companies',
            labels={'x': 'Number of Job Postings', 'y': 'Company'},
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
            return self._create_empty_chart("Workplace type data not available")
        
        workplace_counts = df['workplaceType'].value_counts()
        
        if workplace_counts.empty:
            return self._create_empty_chart("No workplace type data available")
        
        fig = px.pie(
            values=workplace_counts.values,
            names=workplace_counts.index,
            title='Job Distribution by Workplace Type'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        return fig
    
    def create_publishing_trends_chart(self, df=None):
        """Create a line chart showing job publishing trends over time."""
        if df is None:
            df = self.df
            
        if 'publishedAt' not in df.columns or df['publishedAt'].isna().all():
            return self._create_empty_chart("Publishing date data not available")
        
        # Filter out null dates and group by date
        df_with_dates = df.dropna(subset=['publishedAt'])
        
        if df_with_dates.empty:
            return self._create_empty_chart("No valid publishing dates found")
        
        # Group by date
        df_with_dates['date'] = df_with_dates['publishedAt'].dt.date
        daily_counts = df_with_dates.groupby('date').size().reset_index(name='count')
        
        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Job Postings Over Time',
            labels={'date': 'Date', 'count': 'Number of Job Postings'}
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
                    'Skill': skill,
                    'Experience Level': exp_level,
                    'Count': count
                })
        
        if not chart_data:
            return self._create_empty_chart("No data available for skills by experience chart")
        
        chart_df = pd.DataFrame(chart_data)
        
        fig = px.bar(
            chart_df,
            x='Skill',
            y='Count',
            color='Experience Level',
            title=f'Top {top_skills} Skills by Experience Level',
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
            
        if 'publishedAt' not in df.columns or df['publishedAt'].isna().all():
            return self._create_empty_chart("Publishing date data not available for skills trends")
        
        # Filter out null dates
        df_with_dates = df.dropna(subset=['publishedAt'])
        
        if df_with_dates.empty:
            return self._create_empty_chart("No valid publishing dates found for skills trends")
        
        # Get top skills first
        all_skills = []
        for skills_list in df_with_dates['requiredSkills']:
            all_skills.extend(skills_list)
        
        top_skills_list = [skill for skill, _ in Counter(all_skills).most_common(top_skills)]
        
        if not top_skills_list:
            return self._create_empty_chart("No skills data available for trends")
        
        # Group by date and skill
        df_with_dates['date'] = df_with_dates['publishedAt'].dt.date
        
        # Create data for line chart
        trend_data = []
        for date in sorted(df_with_dates['date'].unique()):
            date_df = df_with_dates[df_with_dates['date'] == date]
            
            for skill in top_skills_list:
                count = sum(1 for skills_list in date_df['requiredSkills'] if skill in skills_list)
                trend_data.append({
                    'Date': date,
                    'Skill': skill,
                    'Count': count
                })
        
        if not trend_data:
            return self._create_empty_chart("No trend data available")
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = px.line(
            trend_df,
            x='Date',
            y='Count',
            color='Skill',
            title=f'Top {top_skills} Skills Demand Over Time',
            labels={'Date': 'Publication Date', 'Count': 'Number of Job Postings'}
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified'
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
