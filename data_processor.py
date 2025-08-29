import pandas as pd
import json
from collections import Counter, defaultdict
from datetime import datetime
import re
from persistent_storage import PersistentStorage

class JobDataProcessor:
    """Class for processing and analyzing job market data."""
    
    def __init__(self):
        self.df = None  # Real admin data
        self.demo_df = None  # Demo data for guests
        self.categories_data = {}  # Store real data by categories
        self.demo_categories_data = {}  # Store demo data by categories
        
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
        
    def process_json_data(self, json_data, category=None, append_to_existing=False):
        """Convert JSON data to processed DataFrame with category support."""
        if not isinstance(json_data, list):
            raise ValueError("JSON data should be a list of job objects")
        
        if len(json_data) == 0:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        
        # Validate required columns for new format
        required_columns = ['role', 'company', 'city', 'seniority', 'skills']
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
        
        # Add derived columns
        df['skillsCount'] = df['skills'].apply(len)
        df['requiredSkills'] = df['skills'].apply(lambda x: list(x.keys()) if isinstance(x, dict) else [])
        
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
        """Get skills distribution by seniority level."""
        if df is None:
            df = self.df
        
        exp_skills = defaultdict(lambda: defaultdict(int))
        
        for _, row in df.iterrows():
            seniority_level = row['seniority']
            for skill in row['requiredSkills']:
                exp_skills[seniority_level][skill] += 1
        
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
    
    def get_skill_weight_analysis(self, df=None):
        """Analyze skill importance weighted by required proficiency level."""
        if df is None:
            df = self.df
        
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
        
        for _, row in df.iterrows():
            skills_dict = row['skills']
            if isinstance(skills_dict, dict):
                for skill, level in skills_dict.items():
                    weight = level_weights.get(level, 2)  # Default weight for unknown levels
                    skill_weight_data[skill]['total_weight'] += weight
                    skill_weight_data[skill]['count'] += 1
                    skill_weight_data[skill]['levels'][level] += 1
        
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
    
