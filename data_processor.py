import pandas as pd
import numpy as np
import json
from collections import Counter, defaultdict
from datetime import datetime
import re
import streamlit as st
from persistent_storage import PersistentStorage

class JobDataProcessor:
    """Class for processing and analyzing job market data."""
    
    def __init__(self):
        self.df = None  # Real admin data
        self.demo_df = None  # Demo data for guests
        self.categories_data = {}  # Store real data by categories
        self.demo_categories_data = {}  # Store demo data by categories
        
        # Pre-computed aggregated data for faster access
        self.precomputed_data = {}
        self.demo_precomputed_data = {}
        
        # Initialize persistent storage
        self.storage = PersistentStorage()
        
        # Load existing admin data from storage
        self._load_persistent_data()
        
        # Initialize demo data for guest users
        self._initialize_demo_data()
    
    def _load_persistent_data(self):
        """Load persistent admin data from storage."""
        try:
            # Load main DataFrame
            self.df = self.storage.load_main_data()
            
            # Load categories data
            self.categories_data = self.storage.load_categories_data()
            
            # If we have categories but no main df, rebuild main df
            if not self.categories_data and self.df is None:
                # No stored data, that's fine
                pass
            elif self.categories_data and (self.df is None or self.df.empty):
                # Rebuild main df from categories
                all_dfs = [df for df in self.categories_data.values() if df is not None and not df.empty]
                if all_dfs:
                    self.df = pd.concat(all_dfs, ignore_index=True)
        except Exception as e:
            print(f"Error loading persistent data: {e}")
            # Initialize empty if loading fails
            self.df = None
            self.categories_data = {}
    
    def _save_persistent_data(self):
        """Save current admin data to persistent storage."""
        try:
            # Save main DataFrame
            self.storage.save_main_data(self.df)
            
            # Save categories data
            self.storage.save_categories_data(self.categories_data)
            
            # Save metadata
            metadata = {
                'total_records': len(self.df) if self.df is not None and not self.df.empty else 0,
                'categories_count': len(self.categories_data),
                'categories': list(self.categories_data.keys())
            }
            self.storage.save_metadata(metadata)
            
        except Exception as e:
            print(f"Error saving persistent data: {e}")
    
    def _initialize_demo_data(self):
        """Initialize sample data for guest users."""
        import pandas as pd
        import json
        
        # Sample job data in new format with skill proficiency levels - Only Go specialization for guest users
        sample_jobs_json = """[
  {
    "role": "Senior Go Developer",
    "company": "TechCorp Poland",
    "city": "Warszawa",
    "employment_type": "B2B",
    "job_time_type": "Full-time",
    "remote": true,
    "seniority": "Senior",
    "salary": "16 000 - 22 000 PLN",
    "published_date": "18.08.2025",
    "skills": {
      "Go": "Senior",
      "Docker": "Senior",
      "Kubernetes": "Regular",
      "PostgreSQL": "Senior",
      "REST API": "Expert",
      "Microservices": "Senior",
      "English": "B2"
    },
    "url": "https://example.com/go-developer-1"
  },
  {
    "role": "Go Backend Developer",
    "company": "Innovation Labs",
    "city": "Kraków",
    "employment_type": "B2B",
    "job_time_type": "Full-time",
    "remote": false,
    "seniority": "Regular",
    "salary": "12 000 - 18 000 PLN",
    "published_date": "19.08.2025",
    "skills": {
      "Go": "Senior",
      "gRPC": "Regular",
      "Redis": "Regular",
      "MongoDB": "Regular",
      "Git": "Senior",
      "Linux": "Regular",
      "English": "B2"
    },
    "url": "https://example.com/go-developer-2"
  },
  {
    "role": "Golang Architect",
    "company": "CloudTech Solutions",
    "city": "Gdańsk",
    "employment_type": "B2B",
    "job_time_type": "Full-time",
    "remote": true,
    "seniority": "Expert",
    "salary": "20 000 - 28 000 PLN",
    "published_date": "20.08.2025",
    "skills": {
      "Go": "Expert",
      "AWS": "Senior",
      "Terraform": "Senior",
      "Microservices": "Expert",
      "Event Sourcing": "Senior",
      "CQRS": "Regular",
      "English": "C1"
    },
    "url": "https://example.com/go-architect-1"
  },
  {
    "role": "Go Developer (FinTech)",
    "company": "FinanceFlow",
    "city": "Wrocław",
    "employment_type": "UoP",
    "job_time_type": "Full-time",
    "remote": true,
    "seniority": "Senior",
    "salary": "14 000 - 20 000 PLN",
    "published_date": "21.08.2025",
    "skills": {
      "Go": "Senior",
      "Blockchain": "Regular",
      "PostgreSQL": "Senior",
      "RabbitMQ": "Regular",
      "Testing": "Senior",
      "CI/CD": "Regular",
      "English": "B2"
    },
    "url": "https://example.com/go-fintech-1"
  },
  {
    "role": "Junior Go Developer",
    "company": "StartupHub",
    "city": "Warszawa",
    "employment_type": "UoP",
    "job_time_type": "Full-time",
    "remote": false,
    "seniority": "Junior",
    "salary": "8 000 - 12 000 PLN",
    "published_date": "22.08.2025",
    "skills": {
      "Go": "Regular",
      "Git": "Regular",
      "SQL": "Regular",
      "REST API": "Regular",
      "JSON": "Regular",
      "Linux": "Beginner",
      "English": "B1"
    },
    "url": "https://example.com/go-junior-1"
  }]"""
        
        # Process sample data
        try:
            # Load from the attached file if available, otherwise use inline data
            try:
                with open('attached_assets/Pasted--companyLogoThumbUrl-https-imgproxy-justjoinit-tech-bFGNTASeWwjwkqRg-RQp1jBciVPTsqx-1756343982663_1756343982665.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                sample_jobs = json.loads(content)
            except:
                # Fallback to inline sample data
                sample_jobs = json.loads(sample_jobs_json)
            
            # Limit to 50 results for guest users
            sample_jobs = sample_jobs[:50]
            
            df = pd.DataFrame(sample_jobs)
            df = self._clean_data(df)
            df['category'] = 'guest_data'
            df['upload_timestamp'] = pd.Timestamp.now()
            
            self.demo_df = df
            self.demo_categories_data['demo'] = df.copy()
        except Exception:
            # If sample data fails, continue with empty data
            pass
        
    def process_json_data(self, json_data, append_to_existing=False):
        """Convert JSON data to processed DataFrame with automatic category detection."""
        if not isinstance(json_data, list):
            raise ValueError("JSON data should be a list of job objects")
        
        if len(json_data) == 0:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        
        # Normalize column names to handle case insensitive fields
        df = self._normalize_column_names(df)
        
        # Validate required columns for new format
        required_columns = ['role', 'company', 'city', 'seniority', 'skills']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean and normalize data
        df = self._clean_data(df)
        
        # Set default category if not present in JSON
        if 'category' not in df.columns:
            df['category'] = 'default'
        
        # Normalize category to lowercase
        df['category'] = df['category'].astype(str).str.lower().str.strip()
        
        # Add upload timestamp for trend tracking
        df['upload_timestamp'] = pd.Timestamp.now()
        
        # Handle duplicate detection and data merging
        if append_to_existing and self.df is not None:
            # Remove duplicates based on title, company, city, and skills
            df = self._remove_duplicates(df, self.df)
            # Append to existing data
            self.df = pd.concat([self.df, df], ignore_index=True)
        else:
            self.df = df
        
        # Store by category (using extracted category from JSON)
        category_keys = df['category'].unique()
        for category_key in category_keys:
            category_df = df[df['category'] == category_key].copy()
            if category_key not in self.categories_data:
                self.categories_data[category_key] = category_df
            else:
                # Merge with existing category data, removing duplicates
                existing_category_df = self.categories_data[category_key]
                new_df = self._remove_duplicates(category_df, existing_category_df)
                self.categories_data[category_key] = pd.concat([existing_category_df, new_df], ignore_index=True)
        
        # Pre-compute aggregated data for performance
        self._precompute_aggregated_data()
        
        # Save to persistent storage
        self._save_persistent_data()
        
        return self.df
    
    def _clean_data(self, df):
        """Clean and normalize the data."""
        # Remove rows with missing critical data
        df = df.dropna(subset=['role', 'company', 'skills'])
        
        # Normalize city names
        df['city'] = df['city'].str.strip().str.title()
        
        # Normalize company names
        df['company'] = df['company'].str.strip()
        
        # Normalize seniority levels
        df['seniority'] = df['seniority'].str.strip()
        
        # Clean and normalize skills object
        df['skills'] = df['skills'].apply(self._normalize_skills_object)
        
        # Convert published_date to datetime if present
        if 'published_date' in df.columns:
            df['published_date'] = pd.to_datetime(df['published_date'], format='%d.%m.%Y', errors='coerce')
            # If parsing fails, try ISO format for backwards compatibility
            if df['published_date'].isna().all():
                df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
        
        # Parse and normalize salary if present
        if 'salary' in df.columns:
            df = self._normalize_salary(df)
        
        # Add derived columns
        df['skillsCount'] = df['skills'].apply(len)
        df['requiredSkills'] = df['skills'].apply(lambda x: list(x.keys()) if isinstance(x, dict) else [])
        
        return df
    
    def _normalize_column_names(self, df):
        """Normalize column names to handle case insensitive fields."""
        # Create mapping for common field variations
        field_mapping = {
            # Standard fields
            'role': 'role',
            'company': 'company', 
            'city': 'city',
            'seniority': 'seniority',
            'skills': 'skills',
            'category': 'category',
            'employment_type': 'employment_type',
            'job_time_type': 'job_time_type',
            'remote': 'remote',
            'salary': 'salary',
            'published_date': 'published_date',
            'url': 'url'
        }
        
        # Create case insensitive mapping
        normalized_columns = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in field_mapping:
                normalized_columns[col] = field_mapping[col_lower]
            else:
                normalized_columns[col] = col  # Keep original if no mapping found
        
        # Rename columns
        df = df.rename(columns=normalized_columns)
        return df
    
    def _normalize_skills_object(self, skills):
        """Normalize skills object with levels for consistency."""
        if not isinstance(skills, dict):
            return {}
        
        normalized = {}
        for skill, level in skills.items():
            if isinstance(skill, str) and isinstance(level, str):
                # Clean the skill name
                clean_skill = re.sub(r'[^\w\s+#.-]', '', skill.strip())
                clean_skill = clean_skill.title()
                
                # Handle common variations
                skill_mapping = {
                    'Javascript': 'JavaScript',
                    'Nodejs': 'Node.js',
                    'Reactjs': 'React',
                    'Vuejs': 'Vue.js',
                    'Angularjs': 'Angular',
                    'Postgresql': 'PostgreSQL',
                    'Mysql': 'MySQL',
                    'Mongodb': 'MongoDB',
                    'Aws': 'AWS',
                    'Gcp': 'GCP',
                    'Html': 'HTML',
                    'Css': 'CSS',
                    'Api': 'API',
                    'Rest': 'REST',
                    'Json': 'JSON',
                    'Xml': 'XML',
                    'Git': 'Git',
                    'Docker': 'Docker',
                    'Kubernetes': 'Kubernetes'
                }
                
                clean_skill = skill_mapping.get(clean_skill, clean_skill)
                clean_level = level.strip().title()
                normalized[clean_skill] = clean_level
        
        return normalized
    
    def _normalize_salary(self, df):
        """Parse and normalize salary data."""
        import re
        
        def parse_salary(salary_str):
            """Parse salary string to extract min, max, avg and currency."""
            if pd.isna(salary_str) or not isinstance(salary_str, str):
                return pd.Series({'salary_min': None, 'salary_max': None, 'salary_avg': None, 'salary_currency': None})
            
            salary_str = str(salary_str).strip()
            
            # Extract currency (PLN, EUR, USD, etc.)
            currency_match = re.search(r'(PLN|EUR|USD|zł|€|\$)', salary_str, re.IGNORECASE)
            currency = currency_match.group(1) if currency_match else 'PLN'
            
            # Extract numbers (handle different formats)
            # Remove currency symbols and normalize spaces
            clean_str = re.sub(r'[PLNEURUSDzł€\$]', '', salary_str, flags=re.IGNORECASE).strip()
            
            # Find numbers with potential ranges
            numbers = re.findall(r'(\d+(?:\s?\d{3})*(?:\s?\d{3})*)', clean_str)
            
            if len(numbers) >= 2:
                # Range format (e.g., "10 000 - 16 000 PLN")
                try:
                    min_sal = int(re.sub(r'\s+', '', numbers[0]))
                    max_sal = int(re.sub(r'\s+', '', numbers[1]))
                    
                    # Convert hourly rates to monthly (if below 300 PLN, treat as hourly * 168)
                    if min_sal < 300:
                        min_sal = min_sal * 168
                    if max_sal < 300:
                        max_sal = max_sal * 168
                    
                    avg_sal = (min_sal + max_sal) / 2
                    return pd.Series({'salary_min': min_sal, 'salary_max': max_sal, 'salary_avg': avg_sal, 'salary_currency': currency})
                except:
                    pass
            elif len(numbers) == 1:
                # Single value
                try:
                    sal = int(re.sub(r'\s+', '', numbers[0]))
                    
                    # Convert hourly rates to monthly (if below 300 PLN, treat as hourly * 168)
                    if sal < 300:
                        sal = sal * 168
                    
                    return pd.Series({'salary_min': sal, 'salary_max': sal, 'salary_avg': sal, 'salary_currency': currency})
                except:
                    pass
            
            return pd.Series({'salary_min': None, 'salary_max': None, 'salary_avg': None, 'salary_currency': None})
        
        # Apply salary parsing
        salary_data = df['salary'].apply(parse_salary)
        df = pd.concat([df, salary_data], axis=1)
        
        return df
    
    def _remove_duplicates(self, new_df, existing_df):
        """Remove duplicates from new_df based on existing_df."""
        if existing_df.empty:
            return new_df
        
        # Create composite key for duplicate detection
        def create_key(row):
            # Handle skills object (new format)
            if isinstance(row['skills'], dict):
                skills_str = '|'.join(sorted(row['skills'].keys()))
            else:
                skills_str = ''
            return f"{row['role']}_{row['company']}_{row['city']}_{skills_str}".lower()
        
        existing_keys = set(existing_df.apply(create_key, axis=1))
        new_df_with_keys = new_df.copy()
        new_df_with_keys['_key'] = new_df_with_keys.apply(create_key, axis=1)
        
        # Filter out duplicates
        unique_new_df = new_df_with_keys[~new_df_with_keys['_key'].isin(existing_keys)]
        
        # Remove the temporary key column
        if '_key' in unique_new_df.columns:
            unique_new_df = unique_new_df.drop('_key', axis=1)
        
        return unique_new_df
    
    def get_all_skills(self):
        """Get all unique skills from the dataset."""
        if self.df is None:
            return []
        
        all_skills = []
        for skills_list in self.df['requiredSkills']:
            all_skills.extend(skills_list)
        
        return list(set(all_skills))
    
    def get_skills_statistics(self, df=None):
        """Get skills frequency statistics."""
        if df is None:
            df = self.df
        
        all_skills = []
        for skills_list in df['requiredSkills']:
            all_skills.extend(skills_list)
        
        skills_counter = Counter(all_skills)
        return pd.Series(skills_counter).sort_values(ascending=False)
    
    def get_skill_combinations(self, df=None, min_frequency=2):
        """Get most common skill combinations."""
        if df is None:
            df = self.df
        
        combinations = []
        for skills_list in df['requiredSkills']:
            if len(skills_list) >= 2:
                # Sort skills to ensure consistent combination representation
                sorted_skills = sorted(skills_list)
                for i in range(len(sorted_skills)):
                    for j in range(i+1, len(sorted_skills)):
                        combinations.append(f"{sorted_skills[i]} + {sorted_skills[j]}")
        
        combo_counter = Counter(combinations)
        combo_df = pd.DataFrame(list(combo_counter.items()), columns=['Skill Combination', 'Frequency'])
        combo_df = combo_df[combo_df['Frequency'] >= min_frequency]
        
        return combo_df.sort_values('Frequency', ascending=False)
    
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts
    def get_skills_by_location(_self, df=None):
        """Get top skills by city."""
        if df is None:
            df = _self.df
        
        city_skills = defaultdict(lambda: defaultdict(int))
        
        # Optimized: avoid iterrows, use explode instead
        if 'requiredSkills' in df.columns and not df.empty:
            # Create expanded DataFrame with one row per city-skill combination
            expanded_df = df[['city', 'requiredSkills']].explode('requiredSkills')
            expanded_df = expanded_df.dropna(subset=['requiredSkills'])
            
            # Group by city and skill, count occurrences
            city_skill_counts = expanded_df.groupby(['city', 'requiredSkills']).size().reset_index(name='count')
            
            # Build defaultdict structure for compatibility
            for _, row in city_skill_counts.iterrows():
                city_skills[row['city']][row['requiredSkills']] = row['count']
        
        # Convert to DataFrame
        result_data = []
        for city, skills in city_skills.items():
            top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]
            for rank, (skill, count) in enumerate(top_skills, 1):
                result_data.append({
                    'City': city,
                    'Rank': rank,
                    'Skill': skill,
                    'Count': count
                })
        
        return pd.DataFrame(result_data)
    
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts
    def get_experience_skills_matrix(_self, df=None):
        """Get skills distribution by seniority level."""
        if df is None:
            df = _self.df
        
        exp_skills = defaultdict(lambda: defaultdict(int))
        
        # Optimized: avoid iterrows, use explode instead
        if 'requiredSkills' in df.columns and 'seniority' in df.columns and not df.empty:
            # Create expanded DataFrame with one row per seniority-skill combination
            expanded_df = df[['seniority', 'requiredSkills']].explode('requiredSkills')
            expanded_df = expanded_df.dropna(subset=['requiredSkills', 'seniority'])
            
            # Group by seniority and skill, count occurrences
            seniority_skill_counts = expanded_df.groupby(['seniority', 'requiredSkills']).size().reset_index(name='count')
            
            # Build defaultdict structure for compatibility
            for _, row in seniority_skill_counts.iterrows():
                exp_skills[row['seniority']][row['requiredSkills']] = row['count']
        
        # Convert to DataFrame for easier handling
        result_data = []
        for seniority_level, skills in exp_skills.items():
            for skill, count in skills.items():
                result_data.append({
                    'seniority_level': seniority_level,
                    'skill': skill,
                    'count': count
                })
        
        return pd.DataFrame(result_data)
    
    def get_market_summary(self, df=None):
        """Get overall market summary statistics."""
        if df is None:
            df = self.df
        
        summary = {}
        
        # Basic statistics
        summary['Total Jobs'] = len(df)
        summary['Unique Companies'] = df['company'].nunique()
        summary['Unique Cities'] = df['city'].nunique()
        summary['Average Skills per Job'] = round(df['skillsCount'].mean(), 1)
        
        # Most common values
        summary['Most Common Seniority Level'] = df['seniority'].mode().iloc[0] if not df['seniority'].mode().empty else 'N/A'
        summary['Top Hiring City'] = df['city'].mode().iloc[0] if not df['city'].mode().empty else 'N/A'
        summary['Top Hiring Company'] = df['company'].mode().iloc[0] if not df['company'].mode().empty else 'N/A'
        
        # Remote work statistics
        if 'remote' in df.columns:
            remote_pct = (df['remote'] == True).sum() / len(df) * 100
            summary['Remote Jobs Percentage'] = f"{remote_pct:.1f}%"
        
        # Skills statistics
        all_skills = self.get_skills_statistics(df)
        if not all_skills.empty:
            summary['Most Demanded Skill'] = all_skills.index[0]
            summary['Top Skill Demand'] = f"{all_skills.iloc[0]} jobs ({(all_skills.iloc[0]/len(df)*100):.1f}%)"
        
        return summary
    
    @st.cache_data(ttl=300, hash_funcs={pd.DataFrame: lambda x: str(x.shape)})  # Custom hash for DataFrame with dicts
    def get_skill_weight_analysis(_self, df=None):
        """Analyze skill importance weighted by required proficiency level."""
        if df is None:
            df = _self.df
        
        if df.empty:
            return pd.DataFrame()
        
        # Weight mapping for skill levels
        level_weights = {
            'Beginner': 1,
            'Regular': 2,
            'Advanced': 3,
            'Senior': 4,
            'Expert': 5,
            'B1': 1,
            'B2': 2,
            'C1': 3,
            'C2': 4
        }
        
        skill_weight_data = defaultdict(lambda: {'total_weight': 0, 'count': 0, 'levels': defaultdict(int)})
        
        # Optimized: process all skills at once avoiding iterrows
        if 'skills' in df.columns and not df.empty:
            # Extract all skill-level pairs from the DataFrame
            all_skill_data = []
            for skills_dict in df['skills'].dropna():
                if isinstance(skills_dict, dict):
                    for skill, level in skills_dict.items():
                        all_skill_data.append({'skill': skill, 'level': level})
            
            if all_skill_data:
                # Convert to DataFrame for vectorized operations
                skills_df = pd.DataFrame(all_skill_data)
                skills_df['weight'] = skills_df['level'].map(level_weights).fillna(2)
                
                # Group by skill and aggregate
                skill_groups = skills_df.groupby('skill').agg({
                    'weight': ['sum', 'count'],
                    'level': lambda x: dict(pd.Series(x).value_counts())
                }).reset_index()
                
                # Flatten columns
                skill_groups.columns = ['skill', 'total_weight', 'count', 'levels']
                
                # Build the original structure for compatibility
                for _, row in skill_groups.iterrows():
                    skill = row['skill']
                    skill_weight_data[skill]['total_weight'] = row['total_weight']
                    skill_weight_data[skill]['count'] = row['count']
                    skill_weight_data[skill]['levels'] = defaultdict(int, row['levels'])
        
        # Convert to DataFrame
        result_data = []
        for skill, data in skill_weight_data.items():
            avg_weight = data['total_weight'] / data['count'] if data['count'] > 0 else 0
            importance_score = data['total_weight']  # Total weighted importance
            
            result_data.append({
                'skill': skill,
                'frequency': data['count'],
                'total_weight': data['total_weight'],
                'avg_weight': round(avg_weight, 2),
                'importance_score': importance_score,
                'level_distribution': dict(data['levels'])
            })
        
        result_df = pd.DataFrame(result_data)
        if not result_df.empty:
            result_df = result_df.sort_values('importance_score', ascending=False)
        
        return result_df
    
    def _precompute_aggregated_data(self):
        """Pre-compute aggregated data for all screens to improve performance."""
        print("🔄 Pre-computing aggregated data for better performance...")
        
        # Get all data for aggregation (both demo and real)
        data_sets = {
            'real': self.df,
            'demo': self.demo_df
        }
        
        for data_type, df in data_sets.items():
            if df is None or df.empty:
                continue
                
            # Choose the right storage based on data type
            if data_type == 'demo':
                storage = self.demo_precomputed_data
            else:
                storage = self.precomputed_data
            
            try:
                # 1. SKILLS SCREEN - Pre-aggregate skills data
                storage['skills'] = {
                    'top_skills': self._precompute_skills_demand(df),
                    'skills_combinations': self._precompute_skill_combinations(df),
                    'skills_weight_analysis': self._precompute_skills_weight(df),
                    'experience_skills_matrix': self._precompute_experience_skills_matrix(df)
                }
                
                # 2. LOCATION SCREEN - Pre-aggregate location data  
                storage['location'] = {
                    'skills_by_location': self._precompute_skills_by_location(df),
                    'location_statistics': self._precompute_location_stats(df)
                }
                
                # 3. TRENDS SCREEN - Pre-aggregate time series data
                storage['trends'] = {
                    'skills_trends': self._precompute_skills_trends(df),
                    'salary_trends': self._precompute_salary_trends(df),
                    'monthly_stats': self._precompute_monthly_stats(df)
                }
                
                # 4. SALARY SCREEN - Pre-aggregate salary data
                storage['salary'] = {
                    'salary_correlation': self._precompute_salary_correlation(df),
                    'salary_by_skills': self._precompute_salary_by_skills(df),
                    'salary_statistics': self._precompute_salary_statistics(df)
                }
                
                # 5. COMPANIES SCREEN - Pre-aggregate company data
                storage['companies'] = {
                    'top_companies': self._precompute_company_stats(df),
                    'company_requirements': self._precompute_company_requirements(df)
                }
                
                # 6. DETAILED SKILLS SCREEN - Pre-aggregate individual skill analytics
                storage['detailed_skills'] = self._precompute_detailed_skills_analytics(df)
                
                print(f"✅ Pre-computed data for {data_type} dataset: {len(df)} records")
                
            except Exception as e:
                print(f"❌ Error pre-computing {data_type} data: {e}")
        
        print("🎯 Pre-computation complete! Application performance significantly improved.")
    
    def _precompute_skills_demand(self, df):
        """Pre-compute skills demand data."""
        if 'requiredSkills' not in df.columns:
            return {}
        
        # Get top 50 skills with counts
        skills_series = df['requiredSkills'].explode().dropna()
        skills_counts = skills_series.value_counts()
        
        return {
            'top_20': skills_counts.head(20).to_dict(),
            'top_50': skills_counts.head(50).to_dict(),
            'all_skills': skills_counts.to_dict(),
            'total_unique_skills': len(skills_counts)
        }
    
    def _precompute_skill_combinations(self, df):
        """Pre-compute skill combinations."""
        if 'requiredSkills' not in df.columns:
            return {}
        
        combinations = {}
        for skills_list in df['requiredSkills']:
            if len(skills_list) >= 2:
                sorted_skills = sorted(skills_list)
                for i in range(len(sorted_skills)):
                    for j in range(i+1, len(sorted_skills)):
                        combo = f"{sorted_skills[i]} + {sorted_skills[j]}"
                        combinations[combo] = combinations.get(combo, 0) + 1
        
        # Sort by frequency and get top combinations
        sorted_combos = sorted(combinations.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_20': dict(sorted_combos[:20]),
            'top_50': dict(sorted_combos[:50]),
            'all_combinations': combinations
        }
    
    def _precompute_skills_weight(self, df):
        """Pre-compute skills weight analysis."""
        if 'skills' not in df.columns:
            return {}
        
        level_weights = {
            'Beginner': 1, 'Regular': 2, 'Advanced': 3, 'Senior': 4, 'Expert': 5,
            'B1': 1, 'B2': 2, 'C1': 3, 'C2': 4
        }
        
        skill_weights = {}
        for skills_dict in df['skills'].dropna():
            if isinstance(skills_dict, dict):
                for skill, level in skills_dict.items():
                    weight = level_weights.get(level, 2)
                    if skill not in skill_weights:
                        skill_weights[skill] = {'total_weight': 0, 'count': 0, 'levels': {}}
                    skill_weights[skill]['total_weight'] += weight
                    skill_weights[skill]['count'] += 1
                    skill_weights[skill]['levels'][level] = skill_weights[skill]['levels'].get(level, 0) + 1
        
        # Calculate average weights and importance scores
        for skill, data in skill_weights.items():
            data['avg_weight'] = data['total_weight'] / data['count'] if data['count'] > 0 else 0
            data['importance_score'] = data['total_weight']
        
        return skill_weights
    
    def _precompute_experience_skills_matrix(self, df):
        """Pre-compute experience-skills matrix."""
        if 'requiredSkills' not in df.columns or 'seniority' not in df.columns:
            return {}
        
        matrix_data = {}
        for seniority in df['seniority'].unique():
            seniority_df = df[df['seniority'] == seniority]
            skills_series = seniority_df['requiredSkills'].explode().dropna()
            skills_counts = skills_series.value_counts()
            matrix_data[seniority] = skills_counts.to_dict()
        
        return matrix_data
    
    def _precompute_skills_by_location(self, df):
        """Pre-compute skills by location."""
        if 'requiredSkills' not in df.columns or 'city' not in df.columns:
            return {}
        
        location_skills = {}
        for city in df['city'].unique():
            city_df = df[df['city'] == city]
            skills_series = city_df['requiredSkills'].explode().dropna()
            skills_counts = skills_series.value_counts()
            location_skills[city] = {
                'top_5': skills_counts.head(5).to_dict(),
                'all_skills': skills_counts.to_dict(),
                'total_jobs': len(city_df)
            }
        
        return location_skills
    
    def _precompute_location_stats(self, df):
        """Pre-compute location statistics."""
        if 'city' not in df.columns:
            return {}
        
        city_stats = df['city'].value_counts().to_dict()
        
        return {
            'top_cities': city_stats,
            'total_cities': len(city_stats),
            'remote_percentage': (df['remote'] == True).sum() / len(df) * 100 if 'remote' in df.columns else 0
        }
    
    def _precompute_skills_trends(self, df):
        """Pre-compute skills trends over time."""
        if 'published_date' not in df.columns or 'requiredSkills' not in df.columns:
            return {}
        
        # Filter valid dates
        df_with_dates = df.dropna(subset=['published_date'])
        if df_with_dates.empty:
            return {}
        
        # Get monthly aggregations
        df_with_dates['month'] = pd.to_datetime(df_with_dates['published_date']).dt.to_period('M')
        
        trends = {}
        top_skills = df_with_dates['requiredSkills'].explode().dropna().value_counts().head(10).index
        
        for skill in top_skills:
            skill_trends = []
            for month in df_with_dates['month'].unique():
                month_df = df_with_dates[df_with_dates['month'] == month]
                count = sum(1 for skills_list in month_df['requiredSkills'] if skill in skills_list)
                skill_trends.append({'month': str(month), 'count': count})
            trends[skill] = skill_trends
        
        return trends
    
    def _precompute_salary_trends(self, df):
        """Pre-compute salary trends over time."""
        if 'published_date' not in df.columns or 'salary_avg' not in df.columns:
            return {}
        
        df_with_data = df.dropna(subset=['published_date', 'salary_avg'])
        if df_with_data.empty:
            return {}
        
        df_with_data = df_with_data.copy()
        df_with_data['month'] = pd.to_datetime(df_with_data['published_date']).dt.to_period('M')
        monthly_salary = df_with_data.groupby('month')['salary_avg'].agg(['mean', 'median', 'count']).reset_index()
        
        return {
            'monthly_averages': monthly_salary.to_dict('records'),
            'overall_trend': 'increasing' if monthly_salary['mean'].is_monotonic_increasing else 'mixed'
        }
    
    def _precompute_monthly_stats(self, df):
        """Pre-compute monthly job statistics."""
        if 'published_date' not in df.columns:
            return {}
        
        df_with_dates = df.dropna(subset=['published_date'])
        if df_with_dates.empty:
            return {}
        
        df_with_dates = df_with_dates.copy()
        df_with_dates['month'] = pd.to_datetime(df_with_dates['published_date']).dt.to_period('M')
        monthly_counts = df_with_dates.groupby('month').size().reset_index(name='job_count')
        
        return {
            'monthly_job_counts': monthly_counts.to_dict('records'),
            'peak_month': monthly_counts.loc[monthly_counts['job_count'].idxmax(), 'month'] if not monthly_counts.empty else None
        }
    
    def _precompute_salary_correlation(self, df):
        """Pre-compute salary correlation data."""
        if 'salary_avg' not in df.columns or 'requiredSkills' not in df.columns:
            return {}
        
        salary_df = df.dropna(subset=['salary_avg'])
        if salary_df.empty:
            return {}
        
        # Calculate correlations for top skills
        correlations = {}
        top_skills = salary_df['requiredSkills'].explode().dropna().value_counts().head(20).index
        
        for skill in top_skills:
            skill_salaries = []
            skill_presence = []
            
            for _, row in salary_df.iterrows():
                has_skill = 1 if skill in row['requiredSkills'] else 0
                skill_salaries.append(row['salary_avg'])
                skill_presence.append(has_skill)
            
            if sum(skill_presence) >= 3:  # At least 3 occurrences
                correlation = np.corrcoef(skill_presence, skill_salaries)[0, 1]
                if not np.isnan(correlation):
                    correlations[skill] = correlation
        
        return correlations
    
    def _precompute_salary_by_skills(self, df):
        """Pre-compute salary statistics by skills."""
        if 'salary_avg' not in df.columns or 'requiredSkills' not in df.columns:
            return {}
        
        salary_df = df.dropna(subset=['salary_avg'])
        if salary_df.empty:
            return {}
        
        skills_salary = {}
        top_skills = salary_df['requiredSkills'].explode().dropna().value_counts().head(30).index
        
        for skill in top_skills:
            skill_salaries = []
            for _, row in salary_df.iterrows():
                if skill in row['requiredSkills']:
                    skill_salaries.append(row['salary_avg'])
            
            if len(skill_salaries) >= 3:
                skills_salary[skill] = {
                    'mean': np.mean(skill_salaries),
                    'median': np.median(skill_salaries),
                    'min': np.min(skill_salaries),
                    'max': np.max(skill_salaries),
                    'count': len(skill_salaries),
                    'std': np.std(skill_salaries)
                }
        
        return skills_salary
    
    def _precompute_salary_statistics(self, df):
        """Pre-compute general salary statistics."""
        if 'salary_avg' not in df.columns:
            return {}
        
        salary_df = df.dropna(subset=['salary_avg'])
        if salary_df.empty:
            return {}
        
        return {
            'overall_mean': salary_df['salary_avg'].mean(),
            'overall_median': salary_df['salary_avg'].median(),
            'overall_std': salary_df['salary_avg'].std(),
            'overall_min': salary_df['salary_avg'].min(),
            'overall_max': salary_df['salary_avg'].max(),
            'count': len(salary_df),
            'quartiles': salary_df['salary_avg'].quantile([0.25, 0.5, 0.75]).to_dict()
        }
    
    def _precompute_company_stats(self, df):
        """Pre-compute company statistics."""
        if 'company' not in df.columns:
            return {}
        
        company_counts = df['company'].value_counts()
        
        return {
            'top_companies': company_counts.head(20).to_dict(),
            'total_companies': len(company_counts),
            'single_job_companies': sum(1 for count in company_counts.values if count == 1)
        }
    
    def _precompute_company_requirements(self, df):
        """Pre-compute company skill requirements."""
        if 'company' not in df.columns or 'requiredSkills' not in df.columns:
            return {}
        
        company_skills = {}
        top_companies = df['company'].value_counts().head(10).index
        
        for company in top_companies:
            company_df = df[df['company'] == company]
            skills_series = company_df['requiredSkills'].explode().dropna()
            skills_counts = skills_series.value_counts()
            company_skills[company] = {
                'top_skills': skills_counts.head(10).to_dict(),
                'total_jobs': len(company_df),
                'unique_skills': len(skills_counts)
            }
        
        return company_skills
    
    def _precompute_detailed_skills_analytics(self, df):
        """Pre-compute detailed analytics for individual skills."""
        if 'requiredSkills' not in df.columns:
            return {}
        
        detailed_analytics = {}
        all_skills = df['requiredSkills'].explode().dropna().value_counts()
        
        # Pre-compute for top 100 skills
        for skill in all_skills.head(100).index:
            skill_df = df[df['requiredSkills'].apply(lambda x: skill in x)]
            
            analytics = {
                'total_offers': len(skill_df),
                'market_share': (len(skill_df) / len(df)) * 100
            }
            
            # Level distribution
            if 'skills' in df.columns:
                levels = {}
                for skills_dict in skill_df['skills'].dropna():
                    if isinstance(skills_dict, dict) and skill in skills_dict:
                        level = skills_dict[skill]
                        levels[level] = levels.get(level, 0) + 1
                analytics['level_distribution'] = levels
            
            # Seniority distribution
            if 'seniority' in df.columns:
                analytics['seniority_distribution'] = skill_df['seniority'].value_counts().to_dict()
            
            # Company and city distribution
            if 'company' in df.columns:
                analytics['top_companies'] = skill_df['company'].value_counts().head(5).to_dict()
            
            if 'city' in df.columns:
                analytics['top_cities'] = skill_df['city'].value_counts().head(5).to_dict()
            
            # Salary statistics for this skill
            if 'salary_avg' in df.columns:
                skill_salaries = skill_df.dropna(subset=['salary_avg'])['salary_avg']
                if not skill_salaries.empty:
                    analytics['salary_stats'] = {
                        'mean': skill_salaries.mean(),
                        'median': skill_salaries.median(),
                        'min': skill_salaries.min(),
                        'max': skill_salaries.max(),
                        'std': skill_salaries.std(),
                        'count': len(skill_salaries)
                    }
            
            detailed_analytics[skill] = analytics
        
        return detailed_analytics
    
    # Fast getter methods for pre-computed data
    def get_precomputed_skills_data(self, is_guest=False):
        """Get pre-computed skills data."""
        storage = self.demo_precomputed_data if is_guest else self.precomputed_data
        return storage.get('skills', {})
    
    def get_precomputed_location_data(self, is_guest=False):
        """Get pre-computed location data."""
        storage = self.demo_precomputed_data if is_guest else self.precomputed_data
        return storage.get('location', {})
    
    def get_precomputed_trends_data(self, is_guest=False):
        """Get pre-computed trends data."""
        storage = self.demo_precomputed_data if is_guest else self.precomputed_data
        return storage.get('trends', {})
    
    def get_precomputed_salary_data(self, is_guest=False):
        """Get pre-computed salary data."""
        storage = self.demo_precomputed_data if is_guest else self.precomputed_data
        return storage.get('salary', {})
    
    def get_precomputed_companies_data(self, is_guest=False):
        """Get pre-computed companies data."""
        storage = self.demo_precomputed_data if is_guest else self.precomputed_data
        return storage.get('companies', {})
    
    def get_precomputed_detailed_skills_data(self, is_guest=False):
        """Get pre-computed detailed skills data."""
        storage = self.demo_precomputed_data if is_guest else self.precomputed_data
        return storage.get('detailed_skills', {})
    
    def get_skills_by_level(self, df=None):
        """Get skills statistics grouped by proficiency level."""
        if df is None:
            df = self.df
        
        if df.empty:
            return pd.DataFrame()
        
        level_skills = defaultdict(lambda: defaultdict(int))
        
        for _, row in df.iterrows():
            skills_dict = row['skills']
            if isinstance(skills_dict, dict):
                for skill, level in skills_dict.items():
                    level_skills[level][skill] += 1
        
        # Convert to DataFrame
        result_data = []
        for level, skills in level_skills.items():
            for skill, count in skills.items():
                result_data.append({
                    'level': level,
                    'skill': skill,
                    'count': count
                })
        
        return pd.DataFrame(result_data)
    
    def calculate_skill_importance_score(self, skill_name, df=None):
        """Calculate importance score for a specific skill."""
        if df is None:
            df = self.df
        
        if df.empty:
            return 0
        
        level_weights = {
            'Beginner': 1,
            'Regular': 2,
            'Advanced': 3,
            'Senior': 4,
            'Expert': 5,
            'B1': 1,
            'B2': 2,
            'C1': 3,
            'C2': 4
        }
        
        total_score = 0
        count = 0
        
        for _, row in df.iterrows():
            skills_dict = row['skills']
            if isinstance(skills_dict, dict) and skill_name in skills_dict:
                level = skills_dict[skill_name]
                weight = level_weights.get(level, 2)
                total_score += weight
                count += 1
        
        return total_score
    
    def get_salary_analysis(self, df=None):
        """Get comprehensive salary analysis."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty:
            return pd.DataFrame()
        
        analysis_results = []
        
        # Basic salary statistics
        basic_stats = {
            'metric': 'Podstawowe Statystyki',
            'min_salary': salary_df['salary_min'].min(),
            'max_salary': salary_df['salary_max'].max(),
            'avg_salary': salary_df['salary_avg'].mean(),
            'median_salary': salary_df['salary_avg'].median(),
            'count': len(salary_df)
        }
        analysis_results.append(basic_stats)
        
        return pd.DataFrame(analysis_results)
    
    def get_skills_salary_correlation(self, df=None, min_occurrences=3):
        """Analyze salary correlation with skills."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty:
            return pd.DataFrame()
        
        skill_salary_data = defaultdict(list)
        
        # Collect salary data for each skill
        for _, row in salary_df.iterrows():
            skills_dict = row['skills']
            salary = row['salary_avg']
            
            if isinstance(skills_dict, dict) and pd.notna(salary):
                for skill, level in skills_dict.items():
                    skill_salary_data[skill].append(salary)
        
        # Calculate statistics for each skill
        result_data = []
        for skill, salaries in skill_salary_data.items():
            if len(salaries) >= min_occurrences:  # Only include skills with enough data
                avg_salary = sum(salaries) / len(salaries)
                min_salary = min(salaries)
                max_salary = max(salaries)
                median_salary = sorted(salaries)[len(salaries) // 2]
                count = len(salaries)
                
                result_data.append({
                    'skill': skill,
                    'avg_salary': round(avg_salary, 0),
                    'median_salary': round(median_salary, 0),
                    'min_salary': round(min_salary, 0),
                    'max_salary': round(max_salary, 0),
                    'count': count,
                    'salary_range': round(max_salary - min_salary, 0)
                })
        
        result_df = pd.DataFrame(result_data)
        if not result_df.empty:
            result_df = result_df.sort_values('avg_salary', ascending=False)
        
        return result_df
    
    def get_seniority_salary_analysis(self, df=None):
        """Analyze salary by seniority level."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty:
            return pd.DataFrame()
        
        # Group by seniority
        seniority_groups = salary_df.groupby('seniority')['salary_avg']
        
        result_data = []
        for seniority, salaries in seniority_groups:
            result_data.append({
                'seniority': seniority,
                'avg_salary': round(salaries.mean(), 0),
                'median_salary': round(salaries.median(), 0),
                'min_salary': round(salaries.min(), 0),
                'max_salary': round(salaries.max(), 0),
                'count': len(salaries)
            })
        
        result_df = pd.DataFrame(result_data)
        if not result_df.empty:
            result_df = result_df.sort_values('avg_salary', ascending=False)
        
        return result_df
    
    def get_salary_by_skill_level(self, df=None):
        """Analyze salary by skill proficiency level."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty:
            return pd.DataFrame()
        
        skill_level_salary = defaultdict(list)
        
        # Collect salary data for each skill level
        for _, row in salary_df.iterrows():
            skills_dict = row['skills']
            salary = row['salary_avg']
            
            if isinstance(skills_dict, dict) and pd.notna(salary):
                for skill, level in skills_dict.items():
                    skill_level_salary[level].append(salary)
        
        # Calculate statistics for each skill level
        result_data = []
        for level, salaries in skill_level_salary.items():
            if len(salaries) >= 3:  # Only include levels with at least 3 data points
                result_data.append({
                    'skill_level': level,
                    'avg_salary': round(sum(salaries) / len(salaries), 0),
                    'median_salary': round(sorted(salaries)[len(salaries) // 2], 0),
                    'count': len(salaries)
                })
        
        result_df = pd.DataFrame(result_data)
        if not result_df.empty:
            result_df = result_df.sort_values('avg_salary', ascending=False)
        
        return result_df
    
    def get_correlation_analysis(self, df=None):
        """Analyze correlations between skills and salary."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return {}
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty:
            return {}
        
        correlations = {}
        
        # 1. Skills frequency vs salary correlation
        skill_salary_data = {}
        for _, row in salary_df.iterrows():
            skills_dict = row['skills']
            salary = row['salary_avg']
            
            if isinstance(skills_dict, dict) and pd.notna(salary):
                for skill in skills_dict.keys():
                    if skill not in skill_salary_data:
                        skill_salary_data[skill] = {'salaries': [], 'counts': []}
        
        # Count skill occurrences and collect salaries
        for skill in skill_salary_data.keys():
            skill_salaries = []
            skill_counts = []
            
            for _, row in salary_df.iterrows():
                skills_dict = row['skills']
                salary = row['salary_avg']
                
                if isinstance(skills_dict, dict):
                    has_skill = 1 if skill in skills_dict else 0
                    skill_salaries.append(salary)
                    skill_counts.append(has_skill)
            
            if len(skill_salaries) >= 3 and sum(skill_counts) >= 3:  # Need at least 3 occurrences
                correlation = np.corrcoef(skill_counts, skill_salaries)[0, 1]
                if not np.isnan(correlation):
                    correlations[skill] = correlation
        
        # 2. Seniority level correlation (convert to numeric)
        seniority_mapping = {
            'Junior': 1, 'Mid': 2, 'Regular': 2, 'Senior': 3, 
            'Expert': 4, 'Lead': 4
        }
        
        salary_df['seniority_numeric'] = salary_df['seniority'].map(seniority_mapping)
        salary_df['seniority_numeric'] = salary_df['seniority_numeric'].fillna(2)  # Default to Mid level
        
        if len(salary_df) > 3:
            seniority_correlation = np.corrcoef(salary_df['seniority_numeric'], salary_df['salary_avg'])[0, 1]
            if not np.isnan(seniority_correlation):
                correlations['seniority_level'] = seniority_correlation
        
        # 3. Skills count correlation
        if len(salary_df) > 3:
            skills_count_correlation = np.corrcoef(salary_df['skillsCount'], salary_df['salary_avg'])[0, 1]
            if not np.isnan(skills_count_correlation):
                correlations['skills_count'] = skills_count_correlation
        
        return correlations
    
    def get_regression_analysis(self, df=None, target_skill=None):
        """Perform linear regression analysis for salary prediction."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return {}
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty or len(salary_df) < 5:
            return {}
        
        regression_results = {}
        
        # 1. Seniority vs salary regression
        seniority_mapping = {
            'Junior': 1, 'Mid': 2, 'Regular': 2, 'Senior': 3, 
            'Expert': 4, 'Lead': 4
        }
        
        salary_df['seniority_numeric'] = salary_df['seniority'].map(seniority_mapping)
        salary_df['seniority_numeric'] = salary_df['seniority_numeric'].fillna(2)
        
        if len(salary_df) >= 5:
            # Linear regression: y = ax + b
            x = salary_df['seniority_numeric'].values
            y = salary_df['salary_avg'].values
            
            # Calculate regression coefficients
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            # Slope (a) and intercept (b)
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator != 0:
                a = (n * sum_xy - sum_x * sum_y) / denominator
                b = (sum_y - a * sum_x) / n
            else:
                a = 0
                b = np.mean(y)
            
            # R-squared
            y_pred = a * x + b
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            regression_results['seniority'] = {
                'slope': a,
                'intercept': b,
                'r_squared': r_squared,
                'equation': f'Salary = {a:.0f} * Seniority + {b:.0f}',
                'data_points': len(salary_df)
            }
        
        # 2. Skills count vs salary regression
        if len(salary_df) >= 5:
            x = salary_df['skillsCount'].values
            y = salary_df['salary_avg'].values
            
            # Calculate regression coefficients
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            if sum_x2 - (sum_x * sum_x / n) != 0:  # Avoid division by zero
                a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                b = (sum_y - a * sum_x) / n
                
                # R-squared
                y_pred = a * x + b
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - np.mean(y)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                
                regression_results['skills_count'] = {
                    'slope': a,
                    'intercept': b,
                    'r_squared': r_squared,
                    'equation': f'Salary = {a:.0f} * Skills Count + {b:.0f}',
                    'data_points': len(salary_df)
                }
        
        # 3. Specific skill regression (if target_skill provided)
        if target_skill:
            skill_indicator = []
            salaries = []
            
            for _, row in salary_df.iterrows():
                skills_dict = row['skills']
                if isinstance(skills_dict, dict):
                    has_skill = 1 if target_skill in skills_dict else 0
                    skill_indicator.append(has_skill)
                    salaries.append(row['salary_avg'])
            
            if len(skill_indicator) >= 3 and sum(skill_indicator) >= 3:  # Need at least 3 positive cases
                x = np.array(skill_indicator)
                y = np.array(salaries)
                
                # Simple regression for binary variable
                salary_with_skill = np.mean([s for i, s in enumerate(salaries) if skill_indicator[i] == 1])
                salary_without_skill = np.mean([s for i, s in enumerate(salaries) if skill_indicator[i] == 0])
                
                regression_results[f'skill_{target_skill}'] = {
                    'salary_with_skill': salary_with_skill,
                    'salary_without_skill': salary_without_skill,
                    'difference': salary_with_skill - salary_without_skill,
                    'skill': target_skill,
                    'data_points': len(salaries)
                }
        
        return regression_results
    
    def get_correlation_matrix_data(self, df=None, top_skills=10):
        """Get correlation matrix data for visualization."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        # Filter out rows without salary data
        salary_df = df.dropna(subset=['salary_avg']).copy()
        
        if salary_df.empty:
            return pd.DataFrame()
        
        # Get top skills
        all_skills = []
        for skills_list in salary_df['requiredSkills']:
            all_skills.extend(skills_list)
        
        from collections import Counter
        top_skills_list = [skill for skill, _ in Counter(all_skills).most_common(top_skills)]
        
        # Create correlation matrix data
        matrix_data = []
        
        # Prepare numerical data
        seniority_mapping = {
            'Junior': 1, 'Mid': 2, 'Regular': 2, 'Senior': 3, 
            'Expert': 4, 'Lead': 4
        }
        
        salary_df['seniority_numeric'] = salary_df['seniority'].map(seniority_mapping)
        salary_df['seniority_numeric'] = salary_df['seniority_numeric'].fillna(2)
        
        # Base factors
        factors = ['Salary', 'Seniority', 'Skills Count']
        correlation_matrix = np.zeros((len(factors) + len(top_skills_list), len(factors) + len(top_skills_list)))
        factor_names = factors + top_skills_list
        
        # Create data arrays
        data_arrays = {}
        data_arrays['Salary'] = salary_df['salary_avg'].values
        data_arrays['Seniority'] = salary_df['seniority_numeric'].values
        data_arrays['Skills Count'] = salary_df['skillsCount'].values
        
        # Add skill indicators
        for skill in top_skills_list:
            skill_indicator = []
            for _, row in salary_df.iterrows():
                skills_dict = row['skills']
                has_skill = 1 if isinstance(skills_dict, dict) and skill in skills_dict else 0
                skill_indicator.append(has_skill)
            data_arrays[skill] = np.array(skill_indicator)
        
        # Calculate correlation matrix
        for i, factor1 in enumerate(factor_names):
            for j, factor2 in enumerate(factor_names):
                if i == j:
                    correlation_matrix[i, j] = 1.0
                else:
                    corr = np.corrcoef(data_arrays[factor1], data_arrays[factor2])[0, 1]
                    correlation_matrix[i, j] = corr if not np.isnan(corr) else 0.0
        
        # Convert to DataFrame for easier handling
        correlation_df = pd.DataFrame(
            correlation_matrix,
            index=factor_names,
            columns=factor_names
        )
        
        return correlation_df
    
    def get_data(self, is_guest=False):
        """Get appropriate data based on user type."""
        if is_guest:
            # Guests get all 'go' data, or demo data if no 'go' category exists
            if 'go' in self.categories_data:
                return self.categories_data['go']
            else:
                return self.demo_df if self.demo_df is not None else pd.DataFrame()
        else:
            return self.df if self.df is not None else pd.DataFrame()
    
    def get_categories(self, is_guest=False):
        """Get all available categories based on user type."""
        if is_guest:
            # Guests can see all categories but are limited to accessing only 'go'
            return list(self.categories_data.keys()) if self.categories_data else []
        else:
            return list(self.categories_data.keys())
    
    def has_demo_data(self):
        """Check if demo data is available."""
        return self.demo_df is not None and not self.demo_df.empty
    
    def has_real_data(self):
        """Check if real admin data is available."""
        return self.df is not None and not self.df.empty
    
    def get_data_by_category(self, category=None, is_guest=False):
        """Get data filtered by category based on user type."""
        if is_guest:
            if category is None or category == 'all':
                # Guests get all 'go' data when requesting 'all'
                if 'go' in self.categories_data:
                    return self.categories_data['go']
                else:
                    return self.demo_df if self.demo_df is not None else pd.DataFrame()
            
            category_key = category.lower().strip()
            # Guests can only access 'go' specialization data
            if category_key == 'go' and 'go' in self.categories_data:
                return self.categories_data['go']
            else:
                # For any other category, return empty (they don't have access)
                return pd.DataFrame()
        else:
            if category is None or category == 'all':
                return self.df if self.df is not None else pd.DataFrame()
            
            category_key = category.lower().strip()
            if category_key in self.categories_data:
                return self.categories_data[category_key]
            else:
                return pd.DataFrame()
    
    def clear_category_data(self, category=None):
        """Clear data for specific category or all data."""
        if category is None or category == 'all':
            self.df = pd.DataFrame()
            self.categories_data = {}
            # Clear persistent storage
            self.storage.clear_all_data()
        else:
            category_key = category.lower().strip()
            if category_key in self.categories_data:
                del self.categories_data[category_key]
                # Rebuild main dataframe
                if self.categories_data:
                    all_dfs = list(self.categories_data.values())
                    self.df = pd.concat(all_dfs, ignore_index=True)
                else:
                    self.df = pd.DataFrame()
                # Save updated data to persistent storage
                self._save_persistent_data()
    
    # ============ SKILL-SPECIFIC ANALYTICS ============
    
    def get_all_skills_list(self, df=None):
        """Get all unique skills for search/selection."""
        if df is None:
            df = self.df
        
        if df.empty:
            return []
        
        all_skills = set()
        for _, row in df.iterrows():
            skills_dict = row['skills']
            if isinstance(skills_dict, dict):
                all_skills.update(skills_dict.keys())
        
        return sorted(list(all_skills))
    
    def get_skill_detailed_analytics(self, skill_name, df=None, use_precomputed=True):
        """Get comprehensive analytics for a specific skill (optimized version)."""
        if df is None:
            df = self.df
        
        # Try to use pre-computed data first (MUCH FASTER!)
        if use_precomputed:
            is_guest = hasattr(self, '_current_user_is_guest') and self._current_user_is_guest
            precomputed_detailed = self.get_precomputed_detailed_skills_data(is_guest=is_guest)
            
            if skill_name in precomputed_detailed:
                return precomputed_detailed[skill_name]
        
        # Fallback to original computation if pre-computed data not available
        if df.empty or skill_name not in self.get_all_skills_list(df):
            return {}
        
        analytics = {}
        
        # OPTIMIZED: Use vectorized operations instead of iterrows()
        # Filter dataframe to only rows that contain the skill
        skill_mask = df['skills'].apply(lambda x: isinstance(x, dict) and skill_name in x)
        skill_df = df[skill_mask].copy()
        
        if skill_df.empty:
            return {}
        
        # Basic statistics
        analytics['total_offers'] = len(skill_df)
        analytics['market_share'] = (len(skill_df) / len(df)) * 100 if len(df) > 0 else 0
        
        # Level distribution - VECTORIZED
        skill_levels = skill_df['skills'].apply(lambda x: x.get(skill_name) if isinstance(x, dict) else None).dropna()
        analytics['level_distribution'] = dict(skill_levels.value_counts())
        
        # Seniority distribution - VECTORIZED
        if 'seniority' in skill_df.columns:
            analytics['seniority_distribution'] = dict(skill_df['seniority'].value_counts())
        else:
            analytics['seniority_distribution'] = {}
        
        # Salary statistics - VECTORIZED
        if 'salary_avg' in skill_df.columns:
            skill_salaries = skill_df['salary_avg'].dropna()
            if not skill_salaries.empty:
                analytics['salary_stats'] = {
                    'count': len(skill_salaries),
                    'mean': float(skill_salaries.mean()),
                    'median': float(skill_salaries.median()),
                    'min': float(skill_salaries.min()),
                    'max': float(skill_salaries.max()),
                    'std': float(skill_salaries.std())
                }
            else:
                analytics['salary_stats'] = None
        else:
            analytics['salary_stats'] = None
        
        # Top companies and cities - VECTORIZED
        if 'company' in skill_df.columns:
            analytics['top_companies'] = dict(skill_df['company'].value_counts().head(10))
        else:
            analytics['top_companies'] = {}
            
        if 'city' in skill_df.columns:
            analytics['top_cities'] = dict(skill_df['city'].value_counts().head(10))
        else:
            analytics['top_cities'] = {}
        
        return analytics
    
    def get_skill_vs_seniority_analysis(self, skill_name, df=None):
        """Analyze how skill appears across different seniority levels."""
        if df is None:
            df = self.df
        
        if df.empty:
            return pd.DataFrame()
        
        seniority_skill_data = []
        
        # Get all seniority levels
        all_seniorities = df['seniority'].dropna().unique()
        
        for seniority in all_seniorities:
            seniority_df = df[df['seniority'] == seniority]
            
            # Count offers with this skill at this seniority level
            skill_count = 0
            total_count = len(seniority_df)
            level_counts = defaultdict(int)
            
            for _, row in seniority_df.iterrows():
                skills_dict = row['skills']
                if isinstance(skills_dict, dict) and skill_name in skills_dict:
                    skill_count += 1
                    level_counts[skills_dict[skill_name]] += 1
            
            percentage = (skill_count / total_count) * 100 if total_count > 0 else 0
            
            seniority_skill_data.append({
                'seniority': seniority,
                'skill_offers': skill_count,
                'total_offers': total_count,
                'percentage': percentage,
                'most_common_level': max(level_counts, key=level_counts.get) if level_counts else 'N/A',
                'level_distribution': dict(level_counts)
            })
        
        return pd.DataFrame(seniority_skill_data)
    
    def get_skill_salary_by_level_analysis(self, skill_name, df=None):
        """Analyze salary differences by skill level."""
        if df is None:
            df = self.df
        
        if df.empty or 'salary_avg' not in df.columns:
            return pd.DataFrame()
        
        skill_salary_data = []
        
        for _, row in df.iterrows():
            skills_dict = row['skills']
            if isinstance(skills_dict, dict) and skill_name in skills_dict and pd.notna(row['salary_avg']):
                skill_salary_data.append({
                    'skill_level': skills_dict[skill_name],
                    'salary': row['salary_avg'],
                    'seniority': row.get('seniority', 'Unknown'),
                    'company': row.get('company', 'Unknown'),
                    'city': row.get('city', 'Unknown')
                })
        
        salary_df = pd.DataFrame(skill_salary_data)
        
        if salary_df.empty:
            return pd.DataFrame()
        
        # Group by skill level and calculate statistics
        level_stats = salary_df.groupby('skill_level')['salary'].agg([
            'count', 'mean', 'median', 'min', 'max', 'std'
        ]).round(0)
        
        level_stats.columns = ['Liczba ofert', 'Średnia', 'Mediana', 'Min', 'Max', 'Odchylenie std']
        level_stats = level_stats.reset_index()
        level_stats.columns = ['Poziom umiejętności'] + list(level_stats.columns[1:])
        
        return level_stats
    
    def get_skill_market_trends(self, skill_name, df=None):
        """Get market trends for a specific skill over time."""
        if df is None:
            df = self.df
        
        if df.empty or 'published_date' not in df.columns:
            return pd.DataFrame()
        
        # Filter for skill and valid dates
        skill_trends = []
        
        for _, row in df.iterrows():
            skills_dict = row['skills']
            if isinstance(skills_dict, dict) and skill_name in skills_dict and pd.notna(row['published_date']):
                skill_trends.append({
                    'date': row['published_date'],
                    'skill_level': skills_dict[skill_name],
                    'salary': row.get('salary_avg', None),
                    'seniority': row.get('seniority', 'Unknown')
                })
        
        trends_df = pd.DataFrame(skill_trends)
        
        if trends_df.empty:
            return pd.DataFrame()
        
        # Group by date and calculate statistics
        daily_stats = trends_df.groupby('date').agg({
            'skill_level': 'count',
            'salary': ['mean', 'count']
        }).reset_index()
        
        daily_stats.columns = ['Data', 'Liczba ofert', 'Średnia pensja', 'Oferty z pensją']
        
        return daily_stats
    
