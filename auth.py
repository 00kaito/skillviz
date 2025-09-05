import streamlit as st
import hashlib
import re
from emaillabs_service import EmailLabsService

class AuthManager:
    """Class for managing user authentication and authorization."""
    
    def __init__(self):
        # Initialize EmailLabs service
        self.email_service = EmailLabsService()
        
        # Initialize default users if not exists
        if 'users_db' not in st.session_state:
            st.session_state.users_db = {
                'admin': {
                    'password': self._hash_password('a@a.com'),
                    'email': 'a@a.com',
                    'email_verified': True,
                    'role': 'admin',
                    'created_by': 'system'
                },
                'testuser': {
                    'password': self._hash_password('test123'),
                    'email': 'test@skillviz.com',
                    'email_verified': True,
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
    
    def _validate_email(self, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def authenticate(self, email, password):
        """Authenticate user with email and password."""
        # Find user by email
        for username, user_data in st.session_state.users_db.items():
            if user_data.get('email') == email:
                stored_password = user_data['password']
                if stored_password == self._hash_password(password):
                    # Check if email verification is required and user is not verified
                    if self.email_service.is_configured() and not user_data.get('email_verified', False):
                        st.warning("⚠️ Twoje konto wymaga weryfikacji email. Sprawdź swoją skrzynkę pocztową.")
                        return False
                    
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_role = user_data['role']
                    return True
                break
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
    
    def register_user(self, username, password, email=None, created_by=None, send_verification=True):
        """Register new user with optional email verification."""
        if username in st.session_state.users_db:
            return False, "Użytkownik już istnieje"
        
        if len(username.strip()) < 3:
            return False, "Nazwa użytkownika musi mieć co najmniej 3 znaki"
        
        if len(password) < 6:
            return False, "Hasło musi mieć co najmniej 6 znaków"
        
        if email and not self._validate_email(email):
            return False, "Nieprawidłowy format adresu email"
        
        # Check if email is already used
        if email:
            for existing_user, data in st.session_state.users_db.items():
                if data.get('email') == email:
                    return False, "Adres email jest już używany"
        
        # Create user account
        email_verified = not self.email_service.is_configured() or not email or not send_verification
        
        st.session_state.users_db[username] = {
            'password': self._hash_password(password),
            'email': email or f'{username}@example.com',
            'email_verified': email_verified,
            'role': 'user',
            'created_by': created_by or st.session_state.get('current_user', 'system')
        }
        
        # Send verification email if configured and requested
        if email and self.email_service.is_configured() and send_verification:
            if self.email_service.send_verification_email(email, username):
                return True, "✅ Konto utworzone! Sprawdź email aby zweryfikować konto."
            else:
                # If email sending fails, mark account as verified so user can still login
                st.session_state.users_db[username]['email_verified'] = True
                return True, "✅ Konto utworzone! (Email weryfikacyjny nie został wysłany - możesz się zalogować)"
        
        return True, "Użytkownik zarejestrowany pomyślnie"
    
    def verify_email_from_token(self, token):
        """Verify email using verification token."""
        result = self.email_service.verify_email_token(token)
        
        if result['success']:
            email = result['email']
            # Find user by email and mark as verified
            for username, data in st.session_state.users_db.items():
                if data.get('email') == email:
                    st.session_state.users_db[username]['email_verified'] = True
                    return True, f"Email zweryfikowany pomyślnie dla użytkownika {username}"
            
            return False, "Nie znaleziono użytkownika z tym adresem email"
        else:
            return False, result['error']
    
    def resend_verification_email(self, username):
        """Resend verification email for user."""
        if username not in st.session_state.users_db:
            return False, "Użytkownik nie istnieje"
        
        user_data = st.session_state.users_db[username]
        if user_data.get('email_verified', False):
            return False, "Email już został zweryfikowany"
        
        email = user_data.get('email')
        if not email or email.endswith('@example.com'):
            return False, "Brak prawidłowego adresu email"
        
        if self.email_service.resend_verification_email(email, username):
            return True, "Email weryfikacyjny został wysłany ponownie"
        else:
            return False, "Nie udało się wysłać emaila weryfikacyjnego"
    
    def get_all_users(self):
        """Get all users (admin only)."""
        if not self.is_admin():
            return []
        
        users = []
        for username, data in st.session_state.users_db.items():
            users.append({
                'username': username,
                'email': data.get('email', ''),
                'email_verified': data.get('email_verified', False),
                'role': data['role'],
                'created_by': data.get('created_by', 'system')
            })
        return users
    
    def delete_user(self, username):
        """Delete user (admin only, cannot delete self)."""
        if not self.is_admin():
            return False, "Brak dostępu"
        
        if username == st.session_state.current_user:
            return False, "Nie można usunąć własnego konta"
        
        if username == 'admin':
            return False, "Nie można usunąć głównego konta administratora"
        
        if username in st.session_state.users_db:
            del st.session_state.users_db[username]
            return True, "Użytkownik usunięty pomyślnie"
        
        return False, "Użytkownik nie znaleziony"

def show_login_form():
    """Display login/register form with tabs."""
    auth_manager = AuthManager()
    
    with st.container():
        # Create tabs for Login and Register
        tab1, tab2 = st.tabs(["🔐 Logowanie", "📝 Załóż konto"])
        
        with tab1:
            st.markdown("### Zaloguj się do SkillViz Analytics")
            
            with st.form("login_form"):
                email = st.text_input("Adres email:", value="a@a.com")
                password = st.text_input("Hasło:", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_submitted = st.form_submit_button("Zaloguj się", type="primary")
                with col2:
                    if st.form_submit_button("Dane testowe"):
                        st.info("**Użytkownik testowy:** test@skillviz.com / test123")
                        st.info("**Administrator:** a@a.com / a@a.com")
                
                if login_submitted:
                    if email and password:
                        if auth_manager.authenticate(email, password):
                            st.success(f"✅ Witaj!")
                            st.rerun()
                        else:
                            st.error("❌ Nieprawidłowy email lub hasło")
                    else:
                        st.warning("⚠️ Wprowadź email i hasło")
        
        with tab2:
            st.markdown("### Załóż nowe konto")
            
            with st.form("register_form_public"):
                reg_username = st.text_input("Nazwa użytkownika:", key="reg_username")
                reg_email = st.text_input("Adres email:", key="reg_email") 
                reg_password = st.text_input("Hasło:", type="password", key="reg_password")
                reg_confirm_password = st.text_input("Potwierdź hasło:", type="password", key="reg_confirm_password")
                
                # Show info about email verification
                if auth_manager.email_service.is_configured():
                    st.info("📧 Po rejestracji otrzymasz email weryfikacyjny")
                else:
                    st.info("📧 EmailLabs nie skonfigurowany - konto zostanie aktywowane automatycznie")
                
                register_submitted = st.form_submit_button("Załóż konto", type="primary")
                
                if register_submitted:
                    if reg_username and reg_email and reg_password and reg_confirm_password:
                        if reg_password != reg_confirm_password:
                            st.error("❌ Hasła nie pasują do siebie")
                        else:
                            success, message = auth_manager.register_user(
                                reg_username, reg_password, reg_email, 
                                created_by='self_registered'
                            )
                            if success:
                                st.success(f"✅ {message}")
                                if auth_manager.email_service.is_configured():
                                    st.info("📧 Sprawdź swoją skrzynkę pocztową i kliknij link weryfikacyjny")
                                else:
                                    st.info("🔄 Możesz się teraz zalogować")
                                    # Auto-switch to login tab after successful registration
                                    st.session_state.show_login_tab = True
                            else:
                                st.error(f"❌ {message}")
                    else:
                        st.warning("⚠️ Wypełnij wszystkie pola")

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
            new_username = st.text_input("Nazwa użytkownika:")
            new_email = st.text_input("Adres email:")
            new_password = st.text_input("Hasło:", type="password")
            confirm_password = st.text_input("Potwierdź hasło:", type="password")
            
            # Show email verification option if EmailLabs is configured
            send_verification = True
            if auth_manager.email_service.is_configured():
                send_verification = st.checkbox("Wyślij email weryfikacyjny", value=True)
                st.info("📧 EmailLabs skonfigurowany - weryfikacja email dostępna")
            else:
                st.warning("⚠️ EmailLabs nie skonfigurowany - weryfikacja email wyłączona")
            
            if st.form_submit_button("Zarejestruj użytkownika"):
                if new_username and new_password and new_email:
                    if new_password != confirm_password:
                        st.error("❌ Hasła nie pasują do siebie")
                    else:
                        success, message = auth_manager.register_user(
                            new_username, new_password, new_email, 
                            send_verification=send_verification
                        )
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Wypełnij wszystkie pola")
    
    # List all users
    st.write("**Zarejestrowani użytkownicy:**")
    users = auth_manager.get_all_users()
    
    for user in users:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{user['username']}**")
            st.write(f"📧 {user['email']}")
        with col2:
            st.write(user['role'])
        with col3:
            if user['email_verified']:
                st.write("✅ Verified")
            else:
                st.write("❌ Not verified")
        with col4:
            # Show resend verification button for unverified users
            if (not user['email_verified'] and 
                auth_manager.email_service.is_configured() and
                not user['email'].endswith('@example.com')):
                if st.button("📧", key=f"resend_{user['username']}", 
                           help=f"Wyślij ponownie email weryfikacyjny dla {user['username']}"):
                    success, message = auth_manager.resend_verification_email(user['username'])
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.write("")
        with col5:
            if (user['username'] != 'admin' and 
                user['username'] != auth_manager.get_current_user()):
                if st.button("🗑️", key=f"delete_{user['username']}", 
                           help=f"Usuń {user['username']}"):
                    success, message = auth_manager.delete_user(user['username'])
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Show EmailLabs management if configured
    if auth_manager.email_service.is_configured():
        st.divider()
        from emaillabs_service import show_verification_management
        show_verification_management()

def show_auth_header():
    """Display authentication header with user info and logout."""
    auth_manager = AuthManager()
    
    if auth_manager.is_authenticated():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            role_emoji = "👑" if auth_manager.is_admin() else "👤"
            st.write(f"{role_emoji} Witaj, **{auth_manager.get_current_user()}** ({st.session_state.user_role})")
        
        with col2:
            if auth_manager.is_admin():
                if st.button("👥 Użytkownicy"):
                    st.session_state.show_user_management = not st.session_state.get('show_user_management', False)
        
        with col3:
            if st.button("🚪 Wyloguj"):
                auth_manager.logout()
                st.rerun()
        
        st.divider()
        
        # Show user management if requested
        if st.session_state.get('show_user_management', False):
            show_user_management()
            st.divider()