from app import app
import streamlit as st
from supabase import create_client, Client

# Supabase Credentials
SUPABASE_URL = "https://hjcwijsywehnuojrjdps.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqY3dpanN5d2VobnVvanJqZHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3Nzg4MjQsImV4cCI6MjA1NDM1NDgyNH0.rVyVwhjEsXQ7V9ntWgx1hHDjQOxq4SJaWHDPONBfjP4"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_styles():
    # Apply custom styling using st.markdown with CSS
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(to right, #0d0b33, #4c2f6f, #52489f, #c266a7, #e7c8e7);
            }
            
            .main {
                color: white;
            }
            
            h1 {
                color: white !important;
                text-align: center;
                font-size: 40px !important;
            }
            
            .stButton>button {
                background-color: #6C63FF !important;
                color: white !important;
                padding: 10px 20px;
                font-size: 16px !important;
                border-radius: 10px !important;
                border: none;
                width: 100%;
                transition: all 0.3s;
            }
            
            .stButton>button:hover {
                background-color: #5248C7 !important;
                transform: scale(1.05);
            }
            
            .stTextInput>div>div>input {
                border-radius: 10px;
                border: 2px solid #6C63FF !important;
                color: white;
                background-color: rgba(108, 99, 255, 0.1);
            }
            
            .success-message {
                padding: 1rem;
                border-radius: 0.5rem;
                background-color: rgba(0, 255, 0, 0.1);
                border: 1px solid #00ff00;
            }
            
            .error-message {
                padding: 1rem;
                border-radius: 0.5rem;
                background-color: rgba(255, 0, 0, 0.1);
                border: 1px solid #ff0000;
            }
            
            .centered-buttons {
                max-width: 300px;
                margin: 0 auto;
            }
            
            .centered-text {
                text-align: center;
                color: white;
                margin-bottom: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)

def show_message(message, type="info"):
    """Display styled messages"""
    if type == "success":
        st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
    elif type == "error":
        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
    else:
        st.info(message)

def login_page():
    st.title("🔑 Login to MindMate")
    with st.container():
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔒 Password", type="password", key="login_password")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Login", use_container_width=True):
                if email and password:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        if response.user:
                            st.session_state.user = response.user
                            show_message("Login Successful!", "success")
                            app()
                        else:
                            show_message("Invalid Credentials!", "error")
                    except Exception as e:
                        show_message(f"Error: {str(e)}", "error")
                else:
                    show_message("Please enter email and password.", "error")
        
        with col2:
            if st.button("Back", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

def signup_page():
    st.title("📝 Create an Account")
    with st.container():
        email = st.text_input("📧 Email", key="signup_email")
        password = st.text_input("🔒 Password", type="password", key="signup_password")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Sign Up", use_container_width=True):
                if email and password:
                    try:
                        response = supabase.auth.sign_up({"email": email, "password": password})
                        if response.user:
                            show_message("Account created! Please check your email to confirm.", "success")
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            show_message("Sign-up failed. Please try again.", "error")
                    except Exception as e:
                        show_message(f"Error: {str(e)}", "error")
                else:
                    show_message("Please enter email and password.", "error")
        
        with col2:
            if st.button("Back", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

def dashboard():
    if "user" not in st.session_state or st.session_state.user is None:
        show_message("Please log in first.", "error")
        st.session_state.page = "login"
        st.rerun()
        return

    st.title("🎉 Welcome to MindMate!")
    st.markdown('<p class="centered-text">Hello, <strong>{}</strong> 👋</p>'.format(st.session_state.user.email), unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

def home_page():
    st.title("🧠 MindMate Login System")
    st.markdown('<p class="centered-text">Welcome to MindMate! Sign up or log in to access your account.</p>', unsafe_allow_html=True)

    # Create a container for centered buttons
    with st.container():
        # Add some vertical spacing
        st.write("")
        st.write("")
        
        # Create a centered column
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Sign Up button first
            if st.button("Sign Up", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()
            
            # Add some space between buttons
            st.write("")
            
            # Login button second
            if st.button("Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "user" not in st.session_state:
        st.session_state.user = None

    # Apply custom styling
    init_styles()

    # Route to appropriate page
    pages = {
        "home": home_page,
        "login": login_page,
        "signup": signup_page,
        "dashboard": dashboard
    }
    
    current_page = st.session_state.page
    if current_page in pages:
        pages[current_page]()

if __name__ == "__main__":
    main()
