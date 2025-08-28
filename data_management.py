"""Data management module for SkillViz Analytics."""

import streamlit as st
import json
from data_processor import JobDataProcessor
from visualizations import JobMarketVisualizer

def initialize_session_state(auth_manager):
    """Initialize session state with data processor and categories."""
    if 'data_loaded' not in st.session_state:
        st.session_state.processor = JobDataProcessor()
        
        # Get appropriate data based on authentication status
        is_guest = not auth_manager.is_authenticated()
        current_data = st.session_state.processor.get_data(is_guest=is_guest)
        
        if not current_data.empty:
            st.session_state.data_loaded = True
            st.session_state.df = current_data
            st.session_state.categories = st.session_state.processor.get_categories(is_guest=is_guest)
            st.session_state.visualizer = JobMarketVisualizer(st.session_state.df)
        else:
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.session_state.categories = []
            st.session_state.visualizer = None
        st.session_state.selected_category = 'all'
        st.session_state.append_mode = True

def process_data(json_data, category=None, append_to_existing=True):
    """Process the loaded JSON data with category support."""
    try:
        processor = st.session_state.processor
        df = processor.process_json_data(json_data, category=category, append_to_existing=append_to_existing)
        
        if df.empty and not append_to_existing:
            st.error("❌ No valid job data found in the provided JSON.")
            return False
        
        st.session_state.df = df
        st.session_state.processor = processor
        
        # Update categories list
        st.session_state.categories = processor.get_categories()
        
        # Update visualizer with current data
        if not df.empty:
            st.session_state.visualizer = JobMarketVisualizer(df)
            st.session_state.data_loaded = True
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        return False

def handle_file_upload(uploaded_file, category, append_mode):
    """Handle JSON file upload and processing."""
    try:
        json_data = json.load(uploaded_file)
        if process_data(json_data, category=category, append_to_existing=append_mode):
            added_count = len(json_data)
            category_text = f" to category '{category}'" if category else ""
            st.success(f"✅ {added_count} jobs loaded successfully{category_text}!")
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON file. Please check the format.")
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")

def handle_json_paste(json_text, category, append_mode):
    """Handle pasted JSON data processing."""
    if json_text.strip():
        try:
            json_data = json.loads(json_text)
            if process_data(json_data, category=category, append_to_existing=append_mode):
                added_count = len(json_data)
                category_text = f" to category '{category}'" if category else ""
                st.success(f"✅ {added_count} jobs loaded successfully{category_text}!")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format. Please check your data.")
        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
    else:
        st.warning("⚠️ Please paste JSON data first.")

def clear_all_data():
    """Clear all data from the application."""
    st.session_state.processor.clear_category_data()
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.categories = []
    st.session_state.visualizer = None
    st.rerun()

def clear_category_data(selected_category):
    """Clear data for a specific category."""
    st.session_state.processor.clear_category_data(selected_category)
    st.session_state.categories = st.session_state.processor.get_categories()
    if not st.session_state.categories:
        st.session_state.data_loaded = False
        st.session_state.df = None
        st.session_state.visualizer = None
    else:
        st.session_state.df = st.session_state.processor.df
        st.session_state.visualizer = JobMarketVisualizer(st.session_state.df)
    st.rerun()