import streamlit as st
from quote import quote
from sleep import sleep
from medit import medit
from emotions import emotions
from chatbot import chatbot


# Custom CSS for styling the widgets
st.markdown("""
    <style>
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }
        .widget {
            width: 250px;
            height: 100px;
            background-color: #f4f4f4;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: 0.3s;
        }
        .widget:hover {
            background-color: #e0e0e0;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "home"

# Function to handle page navigation
def set_page(page):
    st.session_state["selected_page"] = page

# Display homepage if no selection is made
if st.session_state["selected_page"] == "home":
    st.title("🌟 Welcome to MindMate 🌟")
    quote_page()  # Display Quote of the Day

    # Display clickable widgets
    st.markdown('<div class="container">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💤 Sleep Tracker"):
            set_page("sleep")
    
    with col2:
        if st.button("🧘 Meditation & Journaling"):
            set_page("meditation")

    with col3:
        if st.button("📅 Emotion Tracker"):
            set_page("emotions")
    
    col4, col5 = st.columns(2)
    
    with col4:
        if st.button("🧠 MindMate Dashboard"):
            set_page("mindmate")

    st.markdown('</div>', unsafe_allow_html=True)

# Route to the selected page
if st.session_state["selected_page"] == "sleep":
    sleep_tracker()

elif st.session_state["selected_page"] == "meditation":
    meditation_page()

elif st.session_state["selected_page"] == "emotions":
    emotions_page()

elif st.session_state["selected_page"] == "mindmate":
    chatbot()
