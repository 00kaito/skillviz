import requests
import base64
import os
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import streamlit as st


class EmailLabsService:
    """Service for handling EmailLabs API integration and email verification."""
    
    def __init__(self):
        self.app_key = os.environ.get('EMAILLABS_APP_KEY', '')
        self.secret_key = os.environ.get('EMAILLABS_SECRET_KEY', '')
        self.from_email = os.environ.get('EMAILLABS_FROM_EMAIL', 'noreply@example.com')
        # EmailLabs API base URL 
        self.base_url = "https://api.emaillabs.net.pl/api"
        
        # Initialize verification tokens storage in session state
        if 'verification_tokens' not in st.session_state:
            st.session_state.verification_tokens = {}
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for EmailLabs API."""
        credentials = f"{self.app_key}:{self.secret_key}"
        auth_string = base64.b64encode(credentials.encode()).decode()
        return f"Basic {auth_string}"
    
    def is_configured(self) -> bool:
        """Check if EmailLabs is properly configured with API keys."""
        return bool(self.app_key and self.secret_key and self.from_email)
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """
        Send email using EmailLabs new_sendmail API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            st.error("⚠️ EmailLabs nie jest skonfigurowany. Sprawdź zmienne środowiskowe.")
            return False
        
        # Debug: Show basic configuration status 
        if not (self.app_key and self.secret_key):
            st.error("⚠️ EmailLabs API keys nie są ustawione")
            return False
        
        try:
            # EmailLabs API new_sendmail endpoint
            url = "https://api.emaillabs.net.pl/api/new_sendmail"
            
            headers = {
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # EmailLabs new_sendmail API expects form-encoded format
            # smtp_account is required even with domain authorization
            form_data = {
                f"to[{to_email}]": "",  # Form format for recipients
                "subject": subject,
                "html": html_content, 
                "from": self.from_email,
                "smtp_account": "1.itngineer.smtp"  # Format: 1.{domain_name}.smtp
            }
            
            if text_content:
                form_data["text"] = text_content
                
            response = requests.post(url, headers=headers, data=form_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return True
                else:
                    st.warning(f"⚠️ EmailLabs API błąd: {result.get('message', 'Nieznany błąd')}")
                    return False
            else:
                st.warning(f"⚠️ EmailLabs HTTP błąd {response.status_code}: {response.text[:200]}")
                return False
                
        except requests.RequestException as e:
            st.error(f"❌ Błąd sieci: {str(e)}")
            return False
        except Exception as e:
            st.error(f"❌ Nieoczekiwany błąd: {str(e)}")
            return False
    
    def generate_verification_token(self, email: str) -> str:
        """Generate a verification token for email verification."""
        token = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(hours=24)  # Token valid for 24 hours
        
        st.session_state.verification_tokens[token] = {
            'email': email,
            'created_at': datetime.now(),
            'expires_at': expiry,
            'used': False
        }
        
        return token
    
    def send_verification_email(self, email: str, username: str) -> bool:
        """
        Send email verification email to user.
        
        Args:
            email: User's email address
            username: Username for personalization
            
        Returns:
            bool: True if email sent successfully
        """
        token = self.generate_verification_token(email)
        # Get current Replit URL or fallback to localhost
        base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        if base_url != 'localhost:5000':
            verification_link = f"https://{base_url}/?verify_email={token}"
        else:
            verification_link = f"http://localhost:5000/?verify_email={token}"
        
        subject = "Weryfikacja konta - SkillViz Analytics"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1f77b4; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                .footer {{ padding: 20px; font-size: 12px; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 SkillViz Analytics</h1>
                </div>
                <div class="content">
                    <h2>Witaj {username}!</h2>
                    <p>Dziękujemy za rejestrację w SkillViz Analytics. Aby aktywować swoje konto, kliknij przycisk poniżej:</p>
                    
                    <a href="{verification_link}" class="button">✅ Zweryfikuj Email</a>
                    
                    <p>Lub skopiuj i wklej ten link do przeglądarki:</p>
                    <p style="word-break: break-all; background: #eee; padding: 10px;">{verification_link}</p>
                    
                    <p><strong>Ważne informacje:</strong></p>
                    <ul>
                        <li>Link weryfikacyjny jest ważny przez 24 godziny</li>
                        <li>Po weryfikacji będziesz mógł w pełni korzystać z aplikacji</li>
                        <li>Jeśli nie rejestrowałeś się, zignoruj tę wiadomość</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>© 2025 SkillViz Analytics - Analiza rynku pracy dla inżynierów</p>
                    <p>Ta wiadomość została wysłana automatycznie, prosimy nie odpowiadać.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        SkillViz Analytics - Weryfikacja konta
        
        Witaj {username}!
        
        Dziękujemy za rejestrację w SkillViz Analytics. Aby aktywować swoje konto, 
        skopiuj i wklej ten link do przeglądarki:
        
        {verification_link}
        
        Ważne informacje:
        - Link weryfikacyjny jest ważny przez 24 godziny
        - Po weryfikacji będziesz mógł w pełni korzystać z aplikacji
        - Jeśli nie rejestrowałeś się, zignoruj tę wiadomość
        
        © 2025 SkillViz Analytics
        """
        
        return self.send_email(email, subject, html_content, text_content)
    
    def verify_email_token(self, token: str) -> Dict[str, Any]:
        """
        Verify email verification token.
        
        Args:
            token: Verification token
            
        Returns:
            dict: Verification result with status and details
        """
        if token not in st.session_state.verification_tokens:
            return {"success": False, "error": "Nieprawidłowy token weryfikacyjny"}
        
        token_data = st.session_state.verification_tokens[token]
        
        if token_data['used']:
            return {"success": False, "error": "Token już został użyty"}
        
        if datetime.now() > token_data['expires_at']:
            return {"success": False, "error": "Token weryfikacyjny wygasł"}
        
        # Mark token as used
        st.session_state.verification_tokens[token]['used'] = True
        
        return {
            "success": True, 
            "email": token_data['email'],
            "message": "Email został pomyślnie zweryfikowany"
        }
    
    def cleanup_expired_tokens(self):
        """Remove expired verification tokens from session state."""
        current_time = datetime.now()
        expired_tokens = [
            token for token, data in st.session_state.verification_tokens.items()
            if current_time > data['expires_at']
        ]
        
        for token in expired_tokens:
            del st.session_state.verification_tokens[token]
    
    def get_pending_verifications(self) -> Dict[str, Any]:
        """Get list of pending email verifications."""
        self.cleanup_expired_tokens()
        
        pending = {}
        for token, data in st.session_state.verification_tokens.items():
            if not data['used'] and datetime.now() <= data['expires_at']:
                pending[data['email']] = {
                    'token': token,
                    'created_at': data['created_at'],
                    'expires_at': data['expires_at']
                }
        
        return pending
    
    def resend_verification_email(self, email: str, username: str) -> bool:
        """Resend verification email to user."""
        # Remove old tokens for this email
        tokens_to_remove = [
            token for token, data in st.session_state.verification_tokens.items()
            if data['email'] == email and not data['used']
        ]
        
        for token in tokens_to_remove:
            del st.session_state.verification_tokens[token]
        
        # Send new verification email
        return self.send_verification_email(email, username)


def show_emaillabs_status():
    """Show EmailLabs configuration status in Streamlit interface."""
    service = EmailLabsService()
    
    if service.is_configured():
        st.success(f"✅ EmailLabs skonfigurowany ({service.from_email})")
    else:
        st.warning("⚠️ EmailLabs wymaga konfiguracji - sprawdź zmienne środowiskowe")
        with st.expander("📋 Wymagane zmienne środowiskowe"):
            st.code("""
EMAILLABS_APP_KEY=your_app_key_here
EMAILLABS_SECRET_KEY=your_secret_key_here  
EMAILLABS_FROM_EMAIL=noreply@yourdomain.com
            """)


def show_verification_management():
    """Show email verification management interface for admins."""
    service = EmailLabsService()
    
    st.subheader("📧 Zarządzanie Weryfikacją Email")
    
    # Show configuration status
    show_emaillabs_status()
    
    if not service.is_configured():
        st.info("Skonfiguruj EmailLabs aby włączyć weryfikację email.")
        return
    
    # Show pending verifications
    pending = service.get_pending_verifications()
    
    if pending:
        st.write(f"**Oczekujące weryfikacje:** {len(pending)}")
        for email, data in pending.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📧 {email}")
            with col2:
                st.write(f"⏰ {data['expires_at'].strftime('%H:%M %d.%m')}")
            with col3:
                if st.button(f"🔄 Wyślij ponownie", key=f"resend_btn_{hash(email)}"):
                    # Note: We need username, but we don't have it here
                    # This would need to be integrated with the auth system
                    st.info("Funkcja dostępna po integracji z systemem użytkowników")
    else:
        st.info("Brak oczekujących weryfikacji email.")
    
    # Test email functionality
    st.divider()
    st.subheader("🧪 Test EmailLabs")
    
    with st.form("test_email_form"):
        test_email = st.text_input("Adres testowy:")
        test_subject = st.text_input("Temat:", value="Test EmailLabs - SkillViz Analytics")
        test_message = st.text_area("Wiadomość:", value="To jest testowa wiadomość z EmailLabs API.")
        
        if st.form_submit_button("📧 Wyślij Test"):
            if test_email and test_subject and test_message:
                html_content = f"<p>{test_message.replace(chr(10), '<br>')}</p>"
                success = service.send_email(test_email, test_subject, html_content, test_message)
                
                if success:
                    st.success(f"✅ Email testowy wysłany do {test_email}")
                else:
                    st.error("❌ Nie udało się wysłać emaila testowego")
            else:
                st.warning("⚠️ Wypełnij wszystkie pola")