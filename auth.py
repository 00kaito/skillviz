import streamlit as st
import hashlib

class AuthManager:
    """Class for managing user authentication and authorization."""
    
    def __init__(self):
        # Initialize default users if not exists
        if 'users_db' not in st.session_state:
            st.session_state.users_db = {
                'skillviz': {
                    'password': self._hash_password('Skillviz^2'),
                    'role': 'admin',
                    'created_by': 'system'
                },
                'testuser': {
                    'password': self._hash_password('test123'),
                    'role': 'user',
                    'created_by': 'system'
                }
            }
        
        # Initialize auth state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
    
    def _hash_password(self, password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user with username and password."""
        if username in st.session_state.users_db:
            stored_password = st.session_state.users_db[username]['password']
            if stored_password == self._hash_password(password):
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.user_role = st.session_state.users_db[username]['role']
                return True
        return False
    
    def logout(self):
        """Logout current user."""
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
    
    def is_authenticated(self):
        """Check if user is authenticated."""
        return st.session_state.get('authenticated', False)
    
    def is_admin(self):
        """Check if current user is admin."""
        return (self.is_authenticated() and 
                st.session_state.get('user_role') == 'admin')
    
    def get_current_user(self):
        """Get current user username."""
        return st.session_state.get('current_user')
    
    def register_user(self, username, password, created_by=None):
        """Register new user (admin only)."""
        if username in st.session_state.users_db:
            return False, "User already exists"
        
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        st.session_state.users_db[username] = {
            'password': self._hash_password(password),
            'role': 'user',
            'created_by': created_by or st.session_state.get('current_user', 'system')
        }
        return True, "User registered successfully"
    
    def get_all_users(self):
        """Get all users (admin only)."""
        if not self.is_admin():
            return []
        
        users = []
        for username, data in st.session_state.users_db.items():
            users.append({
                'username': username,
                'role': data['role'],
                'created_by': data.get('created_by', 'system')
            })
        return users
    
    def delete_user(self, username):
        """Delete user (admin only, cannot delete self)."""
        if not self.is_admin():
            return False, "Access denied"
        
        if username == st.session_state.current_user:
            return False, "Cannot delete your own account"
        
        if username == 'skillviz':
            return False, "Cannot delete main admin account"
        
        if username in st.session_state.users_db:
            del st.session_state.users_db[username]
            return True, "User deleted successfully"
        
        return False, "User not found"

def show_login_form():
    """Display login form as a popup/modal."""
    auth_manager = AuthManager()
    
    with st.container():
        st.markdown("### 🔐 Login to SkillViz Analytics")
        
        with st.form("login_form"):
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("Login", type="primary")
            with col2:
                if st.form_submit_button("Demo Credentials"):
                    st.info("**Test User:** testuser / test123")
                    st.info("**Admin:** skillviz / Skillviz^2")
            
            if login_submitted:
                if username and password:
                    if auth_manager.authenticate(username, password):
                        st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")

def show_user_management():
    """Display user management interface (admin only)."""
    auth_manager = AuthManager()
    
    if not auth_manager.is_admin():
        st.error("❌ Access denied. Admin privileges required.")
        return
    
    st.subheader("👥 User Management")
    
    # Register new user
    with st.expander("➕ Register New User"):
        with st.form("register_form"):
            new_username = st.text_input("New Username:")
            new_password = st.text_input("New Password:", type="password")
            confirm_password = st.text_input("Confirm Password:", type="password")
            
            if st.form_submit_button("Register User"):
                if new_username and new_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords don't match")
                    else:
                        success, message = auth_manager.register_user(new_username, new_password)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill all fields")
    
    # List all users
    st.write("**Registered Users:**")
    users = auth_manager.get_all_users()
    
    for user in users:
        col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
        
        with col1:
            st.write(f"**{user['username']}**")
        with col2:
            st.write(user['role'])
        with col3:
            st.write(f"by {user['created_by']}")
        with col4:
            if (user['username'] != 'skillviz' and 
                user['username'] != auth_manager.get_current_user()):
                if st.button("🗑️", key=f"delete_{user['username']}", 
                           help=f"Delete {user['username']}"):
                    success, message = auth_manager.delete_user(user['username'])
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

def show_auth_header():
    """Display authentication header with user info and logout."""
    auth_manager = AuthManager()
    
    if auth_manager.is_authenticated():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            role_emoji = "👑" if auth_manager.is_admin() else "👤"
            st.write(f"{role_emoji} Welcome, **{auth_manager.get_current_user()}** ({st.session_state.user_role})")
        
        with col2:
            if auth_manager.is_admin():
                if st.button("👥 Users"):
                    st.session_state.show_user_management = not st.session_state.get('show_user_management', False)
        
        with col3:
            if st.button("🚪 Logout"):
                auth_manager.logout()
                st.rerun()
        
        st.divider()
        
        # Show user management if requested
        if st.session_state.get('show_user_management', False):
            show_user_management()
            st.divider()