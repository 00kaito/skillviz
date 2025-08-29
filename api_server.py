"""
Flask API Server for SkillViz Analytics
Provides REST API endpoints for data upload with bearer token authentication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pandas as pd
from data_processor import JobDataProcessor
from persistent_storage import PersistentStorage

app = Flask(__name__)
CORS(app)

# Hardcoded bearer token for API authentication
API_BEARER_TOKEN = "skillviz_api_2025_secure_token_xyz789"

def validate_bearer_token():
    """Validate bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False, "Missing or invalid Authorization header. Use 'Bearer <token>'"
    
    token = auth_header.replace('Bearer ', '')
    if token != API_BEARER_TOKEN:
        return False, "Invalid bearer token"
    
    return True, "Valid token"

@app.route('/api/add_data', methods=['POST'])
def add_data():
    """API endpoint for adding job data via POST request."""
    
    # Validate bearer token
    is_valid, message = validate_bearer_token()
    if not is_valid:
        return jsonify({
            "error": message,
            "status": 401
        }), 401
    
    # Check Content-Type
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json",
            "status": 400
        }), 400
    
    try:
        # Get JSON payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({
                "error": "Empty JSON payload",
                "status": 400
            }), 400
        
        # Validate required fields
        if 'category' not in payload:
            return jsonify({
                "error": "Missing 'category' field in payload",
                "status": 400
            }), 400
        
        if 'data' not in payload:
            return jsonify({
                "error": "Missing 'data' field in payload",
                "status": 400
            }), 400
        
        category = payload['category']
        data = payload['data']
        
        # Validate data is a list
        if not isinstance(data, list):
            return jsonify({
                "error": "Data field must be an array of job objects",
                "status": 400
            }), 400
        
        if len(data) == 0:
            return jsonify({
                "error": "Data array cannot be empty",
                "status": 400
            }), 400
        
        # Process data using JobDataProcessor
        processor = JobDataProcessor()
        
        try:
            # Validate and process JSON data
            processed_df = processor.process_json_data(data, category=category, append_to_existing=True)
            
            if processed_df.empty:
                return jsonify({
                    "error": "No valid data to process - check required fields",
                    "status": 400
                }), 400
            
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
                return jsonify({
                    "message": "All records were duplicates, no new data added",
                    "status": 200,
                    "stats": {
                        "total_records": len(data),
                        "duplicates_removed": duplicates_count,
                        "new_records_added": 0,
                        "category": category
                    }
                }), 200
            
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
            if all_dfs:
                main_df = pd.concat(all_dfs, ignore_index=True)
                storage.save_main_data(main_df)
            
            return jsonify({
                "message": "Data added successfully",
                "status": 200,
                "stats": {
                    "total_records": len(data),
                    "duplicates_removed": duplicates_count,
                    "new_records_added": len(unique_df),
                    "category": category
                }
            }), 200
            
        except ValueError as e:
            return jsonify({
                "error": f"Data validation error: {str(e)}",
                "status": 400
            }), 400
        except Exception as e:
            return jsonify({
                "error": f"Processing error: {str(e)}",
                "status": 500
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": f"Request processing error: {str(e)}",
            "status": 500
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "SkillViz Analytics API is running",
        "version": "1.0.0"
    })

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        "api_version": "1.0.0",
        "endpoints": {
            "/api/add_data": {
                "method": "POST",
                "description": "Add job market data to a category",
                "headers": {
                    "Authorization": "Bearer skillviz_api_2025_secure_token_xyz789",
                    "Content-Type": "application/json"
                },
                "payload": {
                    "category": "string - category name",
                    "data": "array - list of job objects"
                },
                "job_object_format": {
                    "role": "string - job title",
                    "company": "string - company name",
                    "city": "string - city name",
                    "seniority": "string - experience level",
                    "skills": "object - skills with proficiency levels",
                    "employment_type": "string - employment type",
                    "job_time_type": "string - working time",
                    "remote": "boolean - remote work",
                    "salary": "string - salary range",
                    "published_date": "string - date in DD.MM.YYYY format",
                    "url": "string - job posting URL"
                }
            },
            "/api/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "duplicate_detection": {
            "description": "Duplicates are detected based on combination of:",
            "fields": ["role", "company", "city", "skills (keys only)"]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)