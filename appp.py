import streamlit as st
import requests
from datetime import datetime
import streamlit as st
import time

# Function to fetch Quote of the Day from an API
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
    
    col4, col5, col6, col7, col8 = st.columns(5)
    with col4:
        if st.button("🤖 MindMate", use_container_width=True):
            st.session_state.page = "MindMate"

    with col5:
        if st.button("😎 Emotion Tracker", use_container_width=True):
            st.session_state.page = "Emotion Tracker"

    with col6:
        if st.button("😴 Sleep Tracker", use_container_width=True):
            st.session_state.page = "Sleep Tracker"

    with col7:
        if st.button("🧘 Self-Care", use_container_width=True):
            st.session_state.page = "Self-Care"
    
    with col8:
        if st.button("🤝 Community", use_container_width=True):
            st.session_state.page = "Community"
    
    if st.session_state.page == "MindMate":
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="center-text">✨ Guided Meditation</h1>', unsafe_allow_html=True)
        st.markdown('<p class="center-text">Follow the breathing animation and let your mind find peace...</p>', unsafe_allow_html=True)

        # Display Heart Animation
        st.markdown('<div class="heart-container"><div class="heart"></div></div>', unsafe_allow_html=True)

        # Breathing Instructions
        st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin: 20px 0;'>
                <h3 style='color: #FF69B4; margin-bottom: 15px;'>🌬️ Breathing Guide</h3>
        """, unsafe_allow_html=True)

        meditation_steps = [
            "👉 Inhale deeply for **4 seconds**... (Heart expands)",
            "😌 Hold your breath for **4 seconds**... (Heart at full size)",
            "💨 Slowly exhale for **6 seconds**... (Heart shrinks back)",
            "🌊 Imagine yourself in a peaceful place...",
            "🔄 Repeat this cycle for **5 minutes**..."
        ]

        for step in meditation_steps:
            st.markdown(f"<p style='color: #ffffff; margin: 10px 0;'>{step}</p>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Audio player
        st.write("🎵 Background Music")
        try:
            st.audio("relaxing-music-with-echo-bell-high-frequency-284495.mp3", format="audio/mp3")
        except:
            st.warning("⚠️ Please ensure the audio file is in the same directory as your script")

    elif st.session_state.page == "Journaling":
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="center-text">📖 Daily Journal</h1>', unsafe_allow_html=True)
        st.markdown('<p class="center-text">Release your thoughts and feelings into words...</p>', unsafe_allow_html=True)

        journal_entry = st.text_area("How are you feeling today?", 
                                placeholder="Write here...",
                                height=300)

        if st.button("💫 Save Entry"):
            try:
                with open("journal_entries.txt", "a") as f:
                    f.write(journal_entry + "\n")
                st.markdown('<div class="success-message">✨ Your thoughts have been saved...</div>', unsafe_allow_html=True)
            except:
                st.error("Unable to save entry. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.page == "Music Therapy":
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="center-text">🎵 Music Therapy</h1>', unsafe_allow_html=True)
        st.markdown('<p class="center-text">Let the healing power of music calm your mind...</p>', unsafe_allow_html=True)

        st.video("https://youtu.be/8lLkH0khhr8?si=WdXt76KpfEm0uTNG")

        st.write("🎵 Upload Your Calming Music")
        uploaded_file = st.file_uploader("Choose a file", type=["mp3"])

        if uploaded_file is not None:
            st.audio(uploaded_file, format="audio/mp3")
        
        st.markdown('</div>', unsafe_allow_html=True)

quote_page()    
    # Set page config
st.set_page_config(page_title="MindMate AI - Guided Self-Care", layout="wide")

# Inject Custom CSS for Styling
st.markdown("""
    <style>
        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
        }

        /* Content Styling */
        .content-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }

        .center-text {
            text-align: center;
            color: #ffffff;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        /* Heart Animation */
        @keyframes breathe {
            0% { transform: scale(1) rotate(-45deg); opacity: 0.8; filter: hue-rotate(0deg); }
            50% { transform: scale(1.4) rotate(-45deg); opacity: 1; filter: hue-rotate(30deg); }
            100% { transform: scale(1) rotate(-45deg); opacity: 0.8; filter: hue-rotate(0deg); }
        }

        .heart-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            position: relative;
            perspective: 1000px;
        }

        .heart {
            width: 150px;
            height: 150px;
            background: linear-gradient(45deg, #FF69B4, #FF1493);
            position: absolute;
            transform-style: preserve-3d;
            animation: breathe 6s infinite ease-in-out;
            box-shadow: 
                0 0 60px rgba(255, 105, 180, 0.6),
                0 0 100px rgba(255, 20, 147, 0.4);
        }

        .heart:before, .heart:after {
            content: "";
            width: 150px;
            height: 150px;
            background: linear-gradient(45deg, #FF69B4, #FF1493);
            border-radius: 50%;
            position: absolute;
            box-shadow: 0 0 40px rgba(255, 105, 180, 0.5);
        }

        .heart:before {
            top: -75px;
            left: 0;
        }

        .heart:after {
            left: 75px;
            top: 0;
        }

        /* Form Elements */
        .stTextArea textarea {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white;
            padding: 15px;
        }

        /* Success Message */
        .success-message {
            background: rgba(46, 213, 115, 0.1);
            border: 1px solid rgba(46, 213, 115, 0.2);
            border-radius: 10px;
            padding: 15px;
            color: #2ed573;
            text-align: center;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Meditation"

# Top Navigation Menu using Streamlit columns
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧘 Meditation", use_container_width=True):
        st.session_state.page = "Meditation"

with col2:
    if st.button("📖 Journaling", use_container_width=True):
        st.session_state.page = "Journaling"

with col3:
    if st.button("🎵 Music Therapy", use_container_width=True):
        st.session_state.page = "Music Therapy"

# Content Sections
if st.session_state.page == "Meditation":
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="center-text">✨ Guided Meditation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center-text">Follow the breathing animation and let your mind find peace...</p>', unsafe_allow_html=True)

    # Display Heart Animation
    st.markdown('<div class="heart-container"><div class="heart"></div></div>', unsafe_allow_html=True)

    # Breathing Instructions
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin: 20px 0;'>
            <h3 style='color: #FF69B4; margin-bottom: 15px;'>🌬️ Breathing Guide</h3>
    """, unsafe_allow_html=True)

    meditation_steps = [
        "👉 Inhale deeply for **4 seconds**... (Heart expands)",
        "😌 Hold your breath for **4 seconds**... (Heart at full size)",
        "💨 Slowly exhale for **6 seconds**... (Heart shrinks back)",
        "🌊 Imagine yourself in a peaceful place...",
        "🔄 Repeat this cycle for **5 minutes**..."
    ]

    for step in meditation_steps:
        st.markdown(f"<p style='color: #ffffff; margin: 10px 0;'>{step}</p>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Audio player
    st.write("🎵 Background Music")
    try:
        st.audio("relaxing-music-with-echo-bell-high-frequency-284495.mp3", format="audio/mp3")
    except:
        st.warning("⚠️ Please ensure the audio file is in the same directory as your script")

elif st.session_state.page == "Journaling":
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="center-text">📖 Daily Journal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center-text">Release your thoughts and feelings into words...</p>', unsafe_allow_html=True)

    journal_entry = st.text_area("How are you feeling today?", 
                               placeholder="Write here...",
                               height=300)

    if st.button("💫 Save Entry"):
        try:
            with open("journal_entries.txt", "a") as f:
                f.write(journal_entry + "\n")
            st.markdown('<div class="success-message">✨ Your thoughts have been saved...</div>', unsafe_allow_html=True)
        except:
            st.error("Unable to save entry. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Music Therapy":
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="center-text">🎵 Music Therapy</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center-text">Let the healing power of music calm your mind...</p>', unsafe_allow_html=True)

    st.video("https://youtu.be/8lLkH0khhr8?si=WdXt76KpfEm0uTNG")

    st.write("🎵 Upload Your Calming Music")
    uploaded_file = st.file_uploader("Choose a file", type=["mp3"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
    
    st.markdown('</div>', unsafe_allow_html=True)