"""Persistent storage module for SkillViz Analytics."""

import json
import os
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

class PersistentStorage:
    """Handle persistent storage of job market data."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.main_data_file = self.data_dir / "admin_data.json"
        self.categories_file = self.data_dir / "categories_data.json"
        self.metadata_file = self.data_dir / "metadata.json"
        
    def save_main_data(self, df):
        """Save main DataFrame to JSON file."""
        if df is not None and not df.empty:
            try:
                # Convert DataFrame to JSON
                data = df.to_dict('records')
                with open(self.main_data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                return True
            except Exception as e:
                print(f"Error saving main data: {e}")
                return False
        return False
    
    def load_main_data(self):
        """Load main DataFrame from JSON file."""
        if self.main_data_file.exists():
            try:
                with open(self.main_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data:
                    return pd.DataFrame(data)
            except Exception as e:
                print(f"Error loading main data: {e}")
        return None
    
    def save_categories_data(self, categories_data):
        """Save categories data to JSON file."""
        if categories_data:
            try:
                # Convert each DataFrame in categories to dict
                serializable_data = {}
                for category, df in categories_data.items():
                    if df is not None and not df.empty:
                        serializable_data[category] = df.to_dict('records')
                
                with open(self.categories_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_data, f, ensure_ascii=False, indent=2, default=str)
                return True
            except Exception as e:
                print(f"Error saving categories data: {e}")
                return False
        return False
    
    def load_categories_data(self):
        """Load categories data from JSON file."""
        if self.categories_file.exists():
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert back to DataFrames
                categories_data = {}
                for category, records in data.items():
                    if records:
                        categories_data[category] = pd.DataFrame(records)
                
                return categories_data
            except Exception as e:
                print(f"Error loading categories data: {e}")
        return {}
    
    def save_metadata(self, metadata):
        """Save metadata (last updated, counts, etc.)."""
        try:
            metadata['last_updated'] = datetime.now().isoformat()
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def load_metadata(self):
        """Load metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return {}
    
    def clear_all_data(self):
        """Clear all stored data files."""
        try:
            files_to_remove = [
                self.main_data_file,
                self.categories_file,
                self.metadata_file
            ]
            
            for file_path in files_to_remove:
                if file_path.exists():
                    file_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def clear_category_data(self, category):
        """Clear specific category data."""
        try:
            categories_data = self.load_categories_data()
            if category in categories_data:
                del categories_data[category]
                self.save_categories_data(categories_data)
                
                # Rebuild main data from remaining categories
                if categories_data:
                    all_dfs = list(categories_data.values())
                    main_df = pd.concat(all_dfs, ignore_index=True)
                    self.save_main_data(main_df)
                else:
                    # No categories left, clear main data
                    if self.main_data_file.exists():
                        self.main_data_file.unlink()
                
                return True
        except Exception as e:
            print(f"Error clearing category data: {e}")
            return False
    
    def has_stored_data(self):
        """Check if there is any stored data."""
        return (self.main_data_file.exists() and self.main_data_file.stat().st_size > 0) or \
               (self.categories_file.exists() and self.categories_file.stat().st_size > 0)
    
    def get_data_info(self):
        """Get information about stored data."""
        info = {
            'has_main_data': self.main_data_file.exists(),
            'has_categories': self.categories_file.exists(),
            'total_records': 0,
            'categories_count': 0
        }
        
        try:
            if info['has_main_data']:
                df = self.load_main_data()
                info['total_records'] = len(df) if df is not None else 0
            
            if info['has_categories']:
                categories = self.load_categories_data()
                info['categories_count'] = len(categories)
                info['categories'] = list(categories.keys())
        except Exception as e:
            print(f"Error getting data info: {e}")
        
        return info