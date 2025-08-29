"""Main application module for SkillViz Analytics."""

import streamlit as st
from config import setup_page_config, setup_app_title
from auth import AuthManager, show_auth_header
from data_management import initialize_session_state
from ui_components import (
    show_guest_header, 
    show_login_section,
    show_admin_data_input,
    show_admin_data_management,
    show_user_sidebar_info,
    show_guest_sidebar_info,
    show_sidebar_filters,
    display_welcome_screen
)
from analytics_dashboard import display_analytics

def handle_email_verification():
    """Handle email verification from URL parameters."""
    auth_manager = AuthManager()
    query_params = st.query_params
    
    if 'verify_email' in query_params:
        verify_token = query_params.get('verify_email', [''])[0] if isinstance(query_params.get('verify_email'), list) else query_params.get('verify_email', '')
        if verify_token:
            success, message = auth_manager.verify_email_from_token(verify_token)
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                # Clear the URL parameter after successful verification
                st.query_params.clear()
            else:
                st.error(f"❌ {message}")
            
            # Show login form after verification
            st.session_state.show_login = True

def show_main_header():
    """Show main header based on authentication status."""
    auth_manager = AuthManager()
    
    if auth_manager.is_authenticated():
        show_auth_header()
    else:
        show_guest_header()
        show_login_section()

def setup_sidebar():
    """Setup sidebar content based on user role."""
    auth_manager = AuthManager()
    
    with st.sidebar:
        if auth_manager.is_admin():
            category = show_admin_data_input()
            show_admin_data_management()
        elif auth_manager.is_authenticated():
            show_user_sidebar_info()
        else:
            show_guest_sidebar_info()
        
        # Show filters if data is loaded
        filtered_df = None
        if st.session_state.get('data_loaded', False):
            filtered_df = show_sidebar_filters(auth_manager, st.session_state.df)
        
        # Store filtered data in session state for analytics
        st.session_state.filtered_df = filtered_df

def main():
    """Main application function."""
    setup_page_config()
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Handle email verification from URL parameters
    handle_email_verification()
    
    # Setup main title
    setup_app_title()
    
    # Show main header
    show_main_header()
    
    # Initialize session state
    initialize_session_state(auth_manager)
    
    # Setup sidebar
    setup_sidebar()
    
    # Main content area - allow guest access
    if (st.session_state.get('data_loaded', False) and st.session_state.df is not None) or not auth_manager.is_authenticated():
        display_analytics()
    else:
        display_welcome_screen()