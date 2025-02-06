import streamlit as st
import requests
from datetime import datetime

def quote():
    def get_quote_of_the_day():
        try:
            response = requests.get("https://zenquotes.io/api/random", timeout=5)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            quote_data = data[0]  # Access the first element of the list
            return quote_data.get("q", "Stay positive, work hard, and make it happen."), quote_data.get("a", "Unknown")
        except requests.exceptions.RequestException as e:
            return (f"Error fetching quote: {e}", "API Error")

    # Quote of the Day Page
    def quote_page():
        st.set_page_config(page_title="MindMate - Quote of the Day", page_icon="🧠", layout="centered")
        st.markdown("""
            <style>
                .main {
                    background-color: #f0f8ff;
                    padding: 2rem;
                    border-radius: 15px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }
                .quote {
                    font-size: 24px;
                    font-style: italic;
                    color: #333;
                    margin-bottom: 10px;
                }
                .author {
                    font-size: 18px;
                    font-weight: bold;
                    color: #555;
                }
            </style>
        """, unsafe_allow_html=True)

        st.title("🌟 MindMate - Quote of the Day🌟")
        quote, author = get_quote_of_the_day()

        st.markdown(f"<div class='main'><div class='quote'>\"{quote}\"</div><div class='author'>- {author}</div></div>", unsafe_allow_html=True)

    # Run the Quote Page
    quote_page()