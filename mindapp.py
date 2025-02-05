import streamlit as st
from datetime import datetime
import requests
from supabase import create_client, Client
import os

# Supabase credentials
SUPABASE_URL = "https://hjcwijsywehnuojrjdps.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqY3dpanN5d2VobnVvanJqZHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3Nzg4MjQsImV4cCI6MjA1NDM1NDgyNH0.rVyVwhjEsXQ7V9ntWgx1hHDjQOxq4SJaWHDPONBfjP4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to fetch Quote of the Day
def get_quote_of_the_day():
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            return response.json()["content"]
    except:
        pass
    return "Stay positive, work hard, and make it happen."

# Navigation function
def navigate(page):
    st.session_state.page = page

# Home Page
def home_page():
    st.title("MindMate")
    st.write("Your Personal Mental Health Assistant")
    st.write("Empowering your mental well-being, one day at a time.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            navigate("login")
    with col2:
        if st.button("Sign Up"):
            navigate("signup")

# Login Page
def login_page():
    st.title("Login to MindMate")
    username = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if username and password:
            try:
                response = supabase.auth.sign_in_with_password({"email": username, "password": password})
                st.session_state["user"] = response.user
                navigate("dashboard")
            except Exception as e:
                st.error("Invalid credentials. Please try again.")
        else:
            st.warning("Please enter both email and password.")

# Sign-Up Page
def signup_page():
    st.title("Sign Up for MindMate")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if email and password:
            try:
                response = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Registration successful! Please log in.")
                navigate("login")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter both email and password.")

# Dashboard Page
def dashboard():
    if "user" not in st.session_state:
        st.warning("Please log in first.")
        navigate("login")
        return

    st.title("Welcome to MindMate")
    st.subheader("Quote of the Day")
    st.write(get_quote_of_the_day())

    if st.button("Logout"):
        supabase.auth.sign_out()
        del st.session_state["user"]
        navigate("home")

# Router
if "page" not in st.session_state:
    st.session_state.page = "home"

page = st.session_state.page

if page == "login":
    login_page()
elif page == "signup":
    signup_page()
elif page == "dashboard":
    dashboard()
else:
    home_page()