"""
API endpoints for SkillViz Analytics
Provides REST API for data upload with bearer token authentication
"""

import streamlit as st
import json
import pandas as pd
from data_processor import JobDataProcessor
from persistent_storage import PersistentStorage

# Hardcoded bearer token for API authentication
API_BEARER_TOKEN = "skillviz_api_2025_secure_token_xyz789"

def validate_bearer_token(token):
    """Validate bearer token for API access."""
    return token == API_BEARER_TOKEN

def api_add_data():
    """API endpoint for adding job data via POST request."""
    
    # Check if request is made to API endpoint
    if st.query_params.get('api') != 'add_data':
        return None
    
    # Get bearer token from query params (simplified for Streamlit)
    token = st.query_params.get('token', '')
    
    if not validate_bearer_token(token):
        return {
            "error": "Invalid or missing bearer token. Use ?api=add_data&token=YOUR_TOKEN",
            "status": 401
        }
    
    # Get request body (JSON payload) from query params or session state
    try:
        # First try to get from query params
        payload_str = st.query_params.get('payload', '')
        if payload_str:
            payload = json.loads(payload_str)
        else:
            return {
                "error": "No JSON payload provided. Use ?payload='{\"category\":\"name\",\"data\":[...]}'",
                "status": 400
            }
        
        # Validate required fields
        if 'category' not in payload:
            return {
                "error": "Missing 'category' field in payload",
                "status": 400
            }
        
        if 'data' not in payload:
            return {
                "error": "Missing 'data' field in payload",
                "status": 400
            }
        
        category = payload['category']
        data = payload['data']
        
        # Process data using JobDataProcessor
        processor = JobDataProcessor()
        
        try:
            # Validate and process JSON data
            processed_df = processor.process_json_data(data, category=category, append_to_existing=True)
            
            if processed_df.empty:
                return {
                    "error": "No valid data to process",
                    "status": 400
                }
            
            # Get persistent storage instance
            storage = PersistentStorage()
            
            # Get existing data for duplicate checking
            existing_categories = storage.load_categories_data()
            if category in existing_categories:
                existing_df = existing_categories[category]
            else:
                existing_df = pd.DataFrame()
            
            # Remove duplicates
            unique_df = processor._remove_duplicates(processed_df, existing_df)
            
            duplicates_count = len(processed_df) - len(unique_df)
            
            if unique_df.empty:
                return {
                    "message": "All records were duplicates, no new data added",
                    "status": 200,
                    "stats": {
                        "total_records": len(data),
                        "duplicates_removed": duplicates_count,
                        "new_records_added": 0
                    }
                }
            
            # Save to persistent storage
            if existing_df.empty:
                # New category
                existing_categories[category] = unique_df
            else:
                # Append to existing category
                combined_df = pd.concat([existing_df, unique_df], ignore_index=True)
                existing_categories[category] = combined_df
            
            # Save updated categories
            storage.save_categories_data(existing_categories)
            
            # Update main data file
            all_dfs = list(existing_categories.values())
            main_df = pd.concat(all_dfs, ignore_index=True)
            storage.save_main_data(main_df)
            
            return {
                "message": "Data added successfully",
                "status": 200,
                "stats": {
                    "total_records": len(data),
                    "duplicates_removed": duplicates_count,
                    "new_records_added": len(unique_df),
                    "category": category
                }
            }
            
        except ValueError as e:
            return {
                "error": f"Data validation error: {str(e)}",
                "status": 400
            }
        except Exception as e:
            return {
                "error": f"Processing error: {str(e)}",
                "status": 500
            }
            
    except Exception as e:
        return {
            "error": f"Request processing error: {str(e)}",
            "status": 500
        }

def setup_api_routes():
    """Setup and handle API routes."""
    
    # Check if this is an API request
    if st.query_params.get('api'):
        api_type = st.query_params.get('api')
        
        if api_type == 'add_data':
            response = api_add_data()
            if response:
                # Display API response
                st.json(response)
                st.stop()
        else:
            st.json({
                "error": f"Unknown API endpoint: {api_type}",
                "status": 404,
                "available_endpoints": [
                    "/app.py?api=add_data"
                ]
            })
            st.stop()

# API Documentation
def show_api_documentation():
    """Display API documentation in the UI."""
    
    st.markdown("""
    ## 🔌 API Endpoints
    
    ### POST Data Upload
    **Endpoint:** `?api=add_data`
    
    **Headers:**
    ```
    Authorization: Bearer skillviz_api_2025_secure_token_xyz789
    Content-Type: application/json
    ```
    
    **Payload:**
    ```json
    {
        "category": "nazwa_kategorii",
        "data": [
            {
                "role": "Python Developer",
                "company": "TechCorp",
                "city": "Warszawa",
                "seniority": "Senior",
                "skills": {
                    "Python": "Senior",
                    "Django": "Regular",
                    "PostgreSQL": "Regular"
                },
                "employment_type": "B2B",
                "job_time_type": "Full-time",
                "remote": true,
                "salary": "15000 - 20000 PLN",
                "published_date": "29.08.2025",
                "url": "https://example.com/job/123"
            }
        ]
    }
    ```
    
    **Response:**
    ```json
    {
        "message": "Data added successfully",
        "status": 200,
        "stats": {
            "total_records": 1,
            "duplicates_removed": 0,
            "new_records_added": 1,
            "category": "nazwa_kategorii"
        }
    }
    ```
    """)