import pandas as pd
import json
from collections import Counter, defaultdict
from datetime import datetime
import re

class JobDataProcessor:
    """Class for processing and analyzing job market data."""
    
    def __init__(self):
        self.df = None
        self.categories_data = {}  # Store data by categories
        self._initialize_sample_data()  # Add sample data for guest users
    
    def _initialize_sample_data(self):
        """Initialize sample data for guest users."""
        import pandas as pd
        from datetime import datetime, timedelta
        import random
        
        # Sample job data for guests
        sample_jobs = [
            {
                "title": "Senior Python Developer",
                "companyName": "TechCorp",
                "city": "Warsaw",
                "experienceLevel": "senior",
                "workingTime": "full_time",
                "workplaceType": "remote",
                "publishedAt": "2025-08-20T10:00:00.000Z",
                "requiredSkills": ["Python", "Django", "PostgreSQL", "Docker"]
            },
            {
                "title": "Frontend Developer",
                "companyName": "WebStudio",
                "city": "Krakow",
                "experienceLevel": "mid",
                "workingTime": "full_time",
                "workplaceType": "hybrid",
                "publishedAt": "2025-08-19T14:30:00.000Z",
                "requiredSkills": ["JavaScript", "React", "TypeScript", "CSS"]
            },
            {
                "title": "Data Engineer",
                "companyName": "DataLab",
                "city": "Gdansk",
                "experienceLevel": "senior",
                "workingTime": "full_time",
                "workplaceType": "remote",
                "publishedAt": "2025-08-18T09:15:00.000Z",
                "requiredSkills": ["Python", "Apache Spark", "SQL", "AWS"]
            },
            {
                "title": "Java Developer",
                "companyName": "Enterprise Solutions",
                "city": "Warsaw",
                "experienceLevel": "mid",
                "workingTime": "full_time",
                "workplaceType": "office",
                "publishedAt": "2025-08-21T11:45:00.000Z",
                "requiredSkills": ["Java", "Spring Boot", "MySQL", "Kubernetes"]
            },
            {
                "title": "DevOps Engineer",
                "companyName": "CloudTech",
                "city": "Wroclaw",
                "experienceLevel": "senior",
                "workingTime": "full_time",
                "workplaceType": "remote",
                "publishedAt": "2025-08-17T16:20:00.000Z",
                "requiredSkills": ["Docker", "Kubernetes", "AWS", "Terraform"]
            }
        ]
        
        # Generate more sample data
        cities = ["Warsaw", "Krakow", "Gdansk", "Wroclaw", "Poznan", "Katowice"]
        companies = ["TechCorp", "WebStudio", "DataLab", "Enterprise Solutions", "CloudTech", "InnovateIT", "SoftwarePlus", "DevCompany"]
        levels = ["junior", "mid", "senior"]
        skills_sets = [
            ["Python", "Django", "FastAPI", "PostgreSQL"],
            ["JavaScript", "React", "Node.js", "MongoDB"],
            ["Java", "Spring Boot", "Hibernate", "MySQL"],
            ["TypeScript", "Angular", "RxJS", "Firebase"],
            ["C#", ".NET", "Entity Framework", "SQL Server"],
            ["Go", "Gin", "Redis", "Docker"],
            ["PHP", "Laravel", "Vue.js", "MariaDB"]
        ]
        
        base_date = datetime(2025, 8, 15)
        for i in range(45):  # Generate 45 more jobs to reach 50 total
            sample_jobs.append({
                "title": f"{random.choice(['Senior', 'Mid-level', 'Junior'])} {random.choice(['Backend', 'Frontend', 'Fullstack'])} Developer",
                "companyName": random.choice(companies),
                "city": random.choice(cities),
                "experienceLevel": random.choice(levels),
                "workingTime": "full_time",
                "workplaceType": random.choice(["remote", "hybrid", "office"]),
                "publishedAt": (base_date + timedelta(days=random.randint(0, 10))).isoformat() + "Z",
                "requiredSkills": random.choice(skills_sets) + [random.choice(["Git", "Docker", "Linux", "API"])]
            })
        
        # Process sample data
        try:
            df = pd.DataFrame(sample_jobs)
            df = self._clean_data(df)
            df['category'] = 'sample'
            df['upload_timestamp'] = pd.Timestamp.now()
            
            self.df = df
            self.categories_data['sample'] = df.copy()
        except Exception:
            # If sample data fails, continue with empty data
            pass
        
    def process_json_data(self, json_data, category=None, append_to_existing=False):
        """Convert JSON data to processed DataFrame with category support."""
        if not isinstance(json_data, list):
            raise ValueError("JSON data should be a list of job objects")
        
        if len(json_data) == 0:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        
        # Validate required columns
        required_columns = ['title', 'companyName', 'city', 'experienceLevel', 'requiredSkills']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean and normalize data
        df = self._clean_data(df)
        
        # Add category column
        if category:
            df['category'] = category.lower().strip()
        else:
            df['category'] = 'default'
        
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
        
        # Store by category
        category_key = category.lower().strip() if category else 'default'
        if category_key not in self.categories_data:
            self.categories_data[category_key] = df.copy()
        else:
            # Merge with existing category data, removing duplicates
            existing_category_df = self.categories_data[category_key]
            new_df = self._remove_duplicates(df, existing_category_df)
            self.categories_data[category_key] = pd.concat([existing_category_df, new_df], ignore_index=True)
        
        return self.df
    
    def _clean_data(self, df):
        """Clean and normalize the data."""
        # Remove rows with missing critical data
        df = df.dropna(subset=['title', 'companyName', 'requiredSkills'])
        
        # Normalize city names
        df['city'] = df['city'].str.strip().str.title()
        
        # Normalize company names
        df['companyName'] = df['companyName'].str.strip()
        
        # Normalize experience levels
        df['experienceLevel'] = df['experienceLevel'].str.lower().str.strip()
        
        # Clean and normalize skills
        df['requiredSkills'] = df['requiredSkills'].apply(self._normalize_skills)
        
        # Convert publishedAt to datetime if present
        if 'publishedAt' in df.columns:
            df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
        
        # Add derived columns
        df['skillsCount'] = df['requiredSkills'].apply(len)
        
        return df
    
    def _normalize_skills(self, skills):
        """Normalize skill names for consistency."""
        if not isinstance(skills, list):
            return []
        
        normalized = []
        for skill in skills:
            if isinstance(skill, str):
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
                normalized.append(clean_skill)
        
        return normalized
    
    def _remove_duplicates(self, new_df, existing_df):
        """Remove duplicates from new_df based on existing_df."""
        if existing_df.empty:
            return new_df
        
        # Create composite key for duplicate detection
        def create_key(row):
            skills_str = '|'.join(sorted(row['requiredSkills'])) if row['requiredSkills'] else ''
            return f"{row['title']}_{row['companyName']}_{row['city']}_{skills_str}".lower()
        
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
    
    def get_skills_by_location(self, df=None):
        """Get top skills by city."""
        if df is None:
            df = self.df
        
        city_skills = defaultdict(lambda: defaultdict(int))
        
        for _, row in df.iterrows():
            city = row['city']
            for skill in row['requiredSkills']:
                city_skills[city][skill] += 1
        
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
    
    def get_experience_skills_matrix(self, df=None):
        """Get skills distribution by experience level."""
        if df is None:
            df = self.df
        
        exp_skills = defaultdict(lambda: defaultdict(int))
        
        for _, row in df.iterrows():
            exp_level = row['experienceLevel']
            for skill in row['requiredSkills']:
                exp_skills[exp_level][skill] += 1
        
        # Convert to DataFrame for easier handling
        result_data = []
        for exp_level, skills in exp_skills.items():
            for skill, count in skills.items():
                result_data.append({
                    'experience_level': exp_level,
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
        summary['Unique Companies'] = df['companyName'].nunique()
        summary['Unique Cities'] = df['city'].nunique()
        summary['Average Skills per Job'] = round(df['skillsCount'].mean(), 1)
        
        # Most common values
        summary['Most Common Experience Level'] = df['experienceLevel'].mode().iloc[0] if not df['experienceLevel'].mode().empty else 'N/A'
        summary['Top Hiring City'] = df['city'].mode().iloc[0] if not df['city'].mode().empty else 'N/A'
        summary['Top Hiring Company'] = df['companyName'].mode().iloc[0] if not df['companyName'].mode().empty else 'N/A'
        
        # Remote work statistics
        if 'workplaceType' in df.columns:
            remote_pct = (df['workplaceType'] == 'remote').sum() / len(df) * 100
            summary['Remote Jobs Percentage'] = f"{remote_pct:.1f}%"
        
        # Skills statistics
        all_skills = self.get_skills_statistics(df)
        if not all_skills.empty:
            summary['Most Demanded Skill'] = all_skills.index[0]
            summary['Top Skill Demand'] = f"{all_skills.iloc[0]} jobs ({(all_skills.iloc[0]/len(df)*100):.1f}%)"
        
        return summary
    
    def get_categories(self):
        """Get all available categories."""
        return list(self.categories_data.keys())
    
    def get_data_by_category(self, category=None):
        """Get data filtered by category."""
        if category is None or category == 'all':
            return self.df
        
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
    
