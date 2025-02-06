import streamlit as st
from supabase import create_client, Client
import nltk
import pickle
import json
import random
import numpy as np
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import datetime
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter
import requests
import uuid
import time
import streamlit_calendar as st_cal
import matplotlib.pyplot as plt
import seaborn as sns

# Supabase configuration
SUPABASE_URL = "https://hjcwijsywehnuojrjdps.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqY3dpanN5d2VobnVvanJqZHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3Nzg4MjQsImV4cCI6MjA1NDM1NDgyNH0.rVyVwhjEsXQ7V9ntWgx1hHDjQOxq4SJaWHDPONBfjP4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize NLTK
nltk.download('punkt_tab')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

def init_session_state():
    """Initialize all session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'posts' not in st.session_state:
        st.session_state.posts = pd.DataFrame(columns=['user_id', 'content', 'timestamp', 'likes', 'dislikes', 'liked_users', 'disliked_users', 'comments'])
    if 'calendar_data' not in st.session_state:
        st.session_state.calendar_data = {}
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

def apply_custom_styles():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #ffffff;
            }
            .main {
                color: white;
            }
            .stButton>button {
                background-color: #6C63FF !important;
                color: white !important;
                border-radius: 10px !important;
                padding: 10px 20px;
                margin: 5px;
                border: none;
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
            .quote-container {
                background-color: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .quote-text {
                font-size: 24px;
                font-style: italic;
                margin-bottom: 10px;
            }
            .quote-author {
                font-size: 18px;
                text-align: right;
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

def login_required(func):
    """Decorator to check if user is logged in"""
    def wrapper(*args, **kwargs):
        if "user" not in st.session_state or st.session_state.user is None:
            show_message("Please log in first.", "error")
            st.session_state.page = "login"
            st.rerun()
        else:
            return func(*args, **kwargs)
    return wrapper

# Authentication Pages
def login_page():
    st.title("🔑 Login to MindMate")
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")
    
    if st.button("Login"):
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                st.session_state.user = response.user
                show_message("Login Successful!", "success")
                st.session_state.page = "dashboard"
                st.rerun()
        except Exception as e:
            show_message(f"Login failed: {str(e)}", "error")

def signup_page():
    st.title("📝 Create an Account")
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")
    
    if st.button("Sign Up"):
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                show_message("Account created! Please check your email to confirm.", "success")
                st.session_state.page = "login"
                st.rerun()
        except Exception as e:
            show_message(f"Sign-up failed: {str(e)}", "error")

# Feature Pages
@login_required
def chatbot_page():
    nltk.download('punkt_tab')
    nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()

    # Load model and necessary files
    model = load_model("model.h5")
    intents = json.loads(open("intents.json").read())
    words = pickle.load(open("texts.pkl", "rb"))
    classes = pickle.load(open("labels.pkl", "rb"))

    # Function to clean and preprocess user input
    def clean_up_sentence(sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    # Convert sentence to bag of words
    def bow(sentence, words, show_details=True):
        sentence_words = clean_up_sentence(sentence)
        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
        return np.array(bag)

    # Predict class from model
    def predict_class(sentence, model):
        p = bow(sentence, words, show_details=False)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        return return_list

    # Get chatbot response
    def get_response(ints, intents_json):
        if ints:
            tag = ints[0]["intent"]
            for intent in intents_json["intents"]:
                if intent["tag"] == tag:
                    return random.choice(intent["responses"])
        return "I'm here for you. How can I help?"

    # Streamlit App Interface
    st.title("🧠 Mental Health Chatbot")
    st.write("Chat with me! I'm here to listen.")

    # Chat UI
    user_input = st.text_input("You:", "")

    if st.button("Send"):
        if user_input:
            intent_prediction = predict_class(user_input, model)
            chatbot_response = get_response(intent_prediction, intents)
            st.text_area("Chatbot:", chatbot_response, height=100, disabled=True)
        else:
            st.warning("Please enter a message.")

    st.write("🩵 Remember, I'm just a chatbot. If you're struggling, consider seeking professional help.")

@login_required
def community_page():
    st.title("📢 Community Feed")
    
    if 'posts' not in st.session_state:
        st.session_state.posts = pd.DataFrame(columns=['user_id', 'content', 'timestamp', 'likes', 'dislikes', 'liked_users', 'disliked_users', 'comments'])
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())  # Unique user identifier per session

    st.title("📢 Anonymous Social Media Feed")

    # Create a new post
    st.subheader("Create New Post")
    new_post = st.text_area("What's on your mind?")
    if st.button("Post"):
        new_post_df = pd.DataFrame({
            'user_id': [st.session_state.user_id],  # Save user ID for each post
            'content': [new_post],
            'timestamp': [datetime.now()],
            'likes': [0],
            'dislikes': [0],
            'liked_users': [[]],  # List to store users who liked the post
            'disliked_users': [[]],  # List to store users who disliked the post
            'comments': [[]]  # List to store comments
        })
        st.session_state.posts = pd.concat([st.session_state.posts, new_post_df], ignore_index=True)
        st.success("Post created successfully!")
        st.rerun()

    # Display all posts
    st.subheader("📌 Posts Feed")
    if not st.session_state.posts.empty:
        for idx, post in st.session_state.posts.iloc[::-1].iterrows():
            with st.container():
                st.markdown("---")
                st.write(f"**User {post['user_id'][:8]}**")  # Display shortened user ID
                st.write(post['content'])
                st.write(f"📅 Posted at: {post['timestamp']}")

                user_id = st.session_state.user_id  # Current session's user ID
                liked_users = post['liked_users']
                disliked_users = post['disliked_users']
                comments = post['comments']

                # Check if user has liked or disliked the post
                has_liked = user_id in liked_users
                has_disliked = user_id in disliked_users

                col1, col2 = st.columns([1, 1])
                with col1:
                    like_label = f"👍 {post['likes']}" if not has_liked else "✅ Liked"
                    if st.button(like_label, key=f"like_{idx}"):
                        if has_liked:  
                            # Remove like
                            st.session_state.posts.at[idx, 'likes'] -= 1
                            st.session_state.posts.at[idx, 'liked_users'].remove(user_id)
                        else:
                            # Add like & remove dislike if exists
                            st.session_state.posts.at[idx, 'likes'] += 1
                            st.session_state.posts.at[idx, 'liked_users'].append(user_id)
                            if has_disliked:
                                st.session_state.posts.at[idx, 'dislikes'] -= 1
                                st.session_state.posts.at[idx, 'disliked_users'].remove(user_id)
                        st.rerun()

                with col2:
                    dislike_label = f"👎 {post['dislikes']}" if not has_disliked else "❌ Disliked"
                    if st.button(dislike_label, key=f"dislike_{idx}"):
                        if has_disliked:
                            # Remove dislike
                            st.session_state.posts.at[idx, 'dislikes'] -= 1
                            st.session_state.posts.at[idx, 'disliked_users'].remove(user_id)
                        else:
                            # Add dislike & remove like if exists
                            st.session_state.posts.at[idx, 'dislikes'] += 1
                            st.session_state.posts.at[idx, 'disliked_users'].append(user_id)
                            if has_liked:
                                st.session_state.posts.at[idx, 'likes'] -= 1
                                st.session_state.posts.at[idx, 'liked_users'].remove(user_id)
                        st.rerun()

                # Comments Section
                st.write("💬 **Comments:**")
                if comments:
                    for comment in comments:
                        st.write(f"🗨️ {comment}")

                # Add a new comment
                new_comment = st.text_input(f"Write a comment...", key=f"comment_input_{idx}")
                if st.button("Comment", key=f"comment_button_{idx}"):
                    if new_comment:
                        st.session_state.posts.at[idx, 'comments'].append(f"User {user_id[:8]}: {new_comment}")
                        st.rerun()

    else:
        st.info("No posts yet. Be the first to share something!")

    # Custom CSS for styling
    st.markdown("""
        <style>
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
        }
        .stTextInput input, .stTextArea textarea {
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        </style>
        """, unsafe_allow_html=True)

@login_required
def emotions_page():
    # Updated CSS focusing on larger emoji display and improved calendar styling
    st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: white;
        }

        /* Calendar container */
        div.calendar {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 20px;
        }

        /* Remove all event styling */
        .fc-event {
            background: none !important;
            border: none !important;
            margin: 0 !important;
        }

        /* Center the emoji in the cell */
        .fc-daygrid-day-frame {
            height: 150px !important;
            position: relative !important;
        }

        .fc-daygrid-day-events {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin-top: 0 !important;
        }

        .fc-daygrid-event-harness {
            width: 100% !important;
            height: 100% !important;
        }

        /* Make emojis much larger */
        .fc-event-title {
            font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
            font-size: 60px !important;  /* Increased font size for larger emojis */
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 0 !important;
            margin: 0 !important;
            flex-direction: column;
            text-align: center;
        }

        /* Button styling for emojis */
        .emoji-button {
            background-color: #2D2D2D;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 20px;
            margin: 10px;
            cursor: pointer;
            font-size: 60px !important;  /* Increased emoji size */
        }

        .emoji-button:hover {
            background-color: #404040;
        }

        /* Center date numbers */
        .fc-daygrid-day-top {
            justify-content: center !important;
            padding-top: 5px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Calendar configuration
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth"
        },
        "selectable": False,
        "initialView": "dayGridMonth",
        "themeSystem": "bootstrap5",
        "height": 900,
        "bootstrapTheme": {
            "bg": "#1E1E1E",
            "fg": "#FFFFFF",
            "primary": "#3788d8",
            "border": "#404040"
        },
        "dayMaxEvents": 1,
        "displayEventTime": False,
        "eventDisplay": "block"
    }

    # Initialize session state
    if 'calendar_data' not in st.session_state:
        st.session_state.calendar_data = {}

    # Title
    st.title("📅 Daily Mood Tracker")

    # Define emojis with their meanings
    emoji_meanings = {
        "😃": "Happy",
        "😕": "Confused",
        "🙁": "Sad",
        "😌": "Relaxed",
        "🤩": "Excited",
        "😴": "Tired",
        "😠": "Angry"
    }

    # Get current date
    current_date = datetime.now().date().isoformat()

    # Create emoji buttons
    st.write("### How are you feeling today?")
    cols = st.columns(len(emoji_meanings))
    for idx, (emoji, meaning) in enumerate(emoji_meanings.items()):
        with cols[idx]:
            if st.button(emoji, key=f"emoji_{idx}", help=meaning):
                st.session_state.calendar_data[current_date] = (emoji, meaning)  # Store both emoji and meaning
                st.rerun()

    # Convert stored emojis to calendar events with both emoji and emotion name
    events = [
        {
            "title": f"{emoji} {meaning}",
            "start": date,
            "allDay": True,
            "display": "block",
            "backgroundColor": "transparent",
            "textColor": "#FFFFFF",
            "className": "emoji-event"
        }
        for date, (emoji, meaning) in st.session_state.calendar_data.items()
    ]

    # Display calendar
    st_cal.calendar(events=events, options=calendar_options)

    # Function to calculate streaks
    def calculate_streaks(dates):
        if not dates:
            return 0, 0  # No streaks

        sorted_dates = sorted(datetime.strptime(date, "%Y-%m-%d").date() for date in dates)
        current_streak, max_streak = 1, 1
        longest_streak = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return current_streak, longest_streak

    # Get streak counts
    dates_logged = list(st.session_state.calendar_data.keys())
    current_streak, max_streak = calculate_streaks(dates_logged)

    # Display streak information
    st.subheader("🔥 Streak Tracker")
    st.write(f"**Current Streak:** {current_streak} days")
    st.write(f"**Longest Streak:** {max_streak} days")

    # Award badges based on streaks
    streak_badge = ""
    if current_streak >= 1:
        streak_badge = "🏅 **Streak Beginner** (Day 1)"
    elif max_streak >= 14:
        streak_badge = "🏆 **Streak Legend** (14+ days)"
    elif max_streak >= 7:
        streak_badge = "💪 **Streak Master** (7+ days)"
    elif max_streak >= 3:
        streak_badge = "🔥 **Streak Beginner** (3+ days)"

    if streak_badge:
        st.success(f"🎉 You earned a badge: {streak_badge}")

    # Weekly Analysis
    if st.session_state.calendar_data:
        st.write("### Weekly Mood Analysis")
        
        # Convert data to DataFrame
        df = pd.DataFrame([{"date": date, "mood": emoji, "mood_name": meaning} for date, (emoji, meaning) in st.session_state.calendar_data.items()])
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.isocalendar().week
        
        # Get current week
        current_week = datetime.now().isocalendar()[1]
        
        # Filter for current week
        current_week_moods = df[df['week'] == current_week]
        
        if not current_week_moods.empty:
            # Count moods for the week
            mood_counts = current_week_moods['mood_name'].value_counts()
            
            # Display weekly summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### This Week's Mood Distribution")
                for mood, count in mood_counts.items():
                    st.write(f"{mood}: {count} days")
            
            with col2:
                # Generate mood insights
                primary_mood = mood_counts.index[0]
                st.write("#### Weekly Insights")
                st.write(f"Most frequent mood: {primary_mood}")
                
                # Generate recommendations based on mood patterns
                if primary_mood in ["Sad", "Angry", "Confused"]:
                    st.write("💭 Consider taking some time for self-care and relaxation")
                elif primary_mood in ["Happy", "Excited"]:
                    st.write("💭 Great week! Keep maintaining these positive vibes")
                elif primary_mood == "Tired":
                    st.write("💭 You might need more rest. Try to get more sleep this week")
                elif primary_mood == "Relaxed":
                    st.write("💭 Good balance! Keep maintaining this peaceful state")

    # Reset today's mood button
    if st.button("Reset Today's Mood"):
        if current_date in st.session_state.calendar_data:
            del st.session_state.calendar_data[current_date]
            st.rerun()


@login_required
def meditation_page():
    st.title("🧘 Meditation")
    st.write("Follow the breathing pattern...")
    
    st.markdown("""<style>
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
    </style>""", unsafe_allow_html=True)

    
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="center-text">✨ Guided Meditation</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center-text">Follow the breathing animation and let your mind find peace...</p>', unsafe_allow_html=True)

        # Display Heart Animation
    st.markdown('<div class="heart-container"><div class="heart"></div></div>', unsafe_allow_html=True)

        # Breathing Instructions
    st.markdown("""<div style='background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin: 20px 0;'>
                <h3 style='color: #FF69B4; margin-bottom: 15px;'>🌬️ Breathing Guide</h3>""", unsafe_allow_html=True)
    meditation_steps = ["👉 Inhale deeply for 4 seconds... (Heart expands)","😌 Hold your breath for 4 seconds... (Heart at full size)",
            "💨 Slowly exhale for 6 seconds... (Heart shrinks back)",
            "🌊 Imagine yourself in a peaceful place...",
            "🔄 Repeat this cycle for 5 minutes..."
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

def journal_page():
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
def music_page():
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="center-text">🎵 Music Therapy</h1>', unsafe_allow_html=True)
    st.markdown('<p class="center-text">Let the healing power of music calm your mind...</p>', unsafe_allow_html=True)

    st.video("https://youtu.be/8lLkH0khhr8?si=WdXt76KpfEm0uTNG")
    st.write("🎵 Upload Your Calming Music")
    uploaded_file = st.file_uploader("Choose a file", type=["mp3"])
    if uploaded_file is not None:
       st.audio(uploaded_file, format="audio/mp3")
    st.markdown('</div>', unsafe_allow_html=True)
def quote_page():
    st.title("🌟 Quote of the Day")
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            quote_data = response.json()[0]
            st.markdown(
                f"""
                <div class="quote-container">
                    <div class="quote-text">"{quote_data['q']}"</div>
                    <div class="quote-author">- {quote_data['a']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.markdown(
            """
            <div class="quote-container">
                <div class="quote-text">"Stay positive, work hard, and make it happen."</div>
                <div class="quote-author">- Unknown</div>
            </div>
            """,
            unsafe_allow_html=True
        )
def sleep_page():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Function to calculate sleep duration
    def calculate_sleep_duration(start_time, end_time):
        if end_time < start_time:
            end_time += timedelta(days=1)  # Adjust for overnight sleep
        return (end_time - start_time).seconds / 3600  # Convert to hours

    # Function to give sleep advice
    def get_sleep_advice(hours):
        if hours < 5:
            return "😴 You slept too little. Try to get at least 7-9 hours."
        elif 5 <= hours < 7:
            return "🌙 Your sleep is a bit short. Consider sleeping earlier."
        elif 7 <= hours <= 9:
            return "✨ Great! You're getting a healthy amount of sleep."
        else:
            return "💤 You might be oversleeping. Try maintaining a consistent schedule."

    # Function to validate if the selected wake-up time is the next day
    def validate_date_and_times(selected_date, sleep_start_time, sleep_end_time):
        # Get current date and time
        current_date = datetime.today().date()
        
        # Convert selected sleep start and end time to datetime
        sleep_start_datetime = datetime.combine(selected_date, datetime.strptime(sleep_start_time, "%H:%M").time())
        sleep_end_datetime = datetime.combine(selected_date, datetime.strptime(sleep_end_time, "%H:%M").time())

        # Adjust end time if it happens after midnight (next day)
        if sleep_end_datetime <= sleep_start_datetime:
            sleep_end_datetime += timedelta(days=1)

        return True

    # UI Styling
    
    st.markdown("""
        <style>
            .stApp {background-color: #1E1E2F; color: white; text-align: center;}
            .sleep-container {padding: 20px; border-radius: 10px; background: #29293D;}
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
                cursor: pointer;
            }
            .stButton>button:hover {
                background-color: #45a049;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🌙 Sleep Cycle Tracker")
    st.markdown("Track your sleep duration and get personalized insights.")

    # Dropdown options for selecting sleep times
    times = [f"{hour:02}:{minute:02}" for hour in range(24) for minute in (0, 30)]

    # Sleep input fields
    st.subheader("Enter Your Sleep Details")

    # Set max_date to today to prevent future date selection
    max_date = datetime.today().date()
    min_date = max_date - timedelta(days=30)  # Allow selection up to 30 days in the past
    date = st.date_input(
        "Select Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD"
    )

    # Default indices for sleep times (10:30 PM and 6:30 AM)
    default_sleep_index = times.index("22:30") if "22:30" in times else 0
    default_wake_index = times.index("06:30") if "06:30" in times else 0

    sleep_start = st.selectbox("Select sleep start time:", times, index=default_sleep_index)
    sleep_end = st.selectbox("Select wake-up time:", times, index=default_wake_index)

    # Process sleep analysis with validation
    if st.button("Analyze Sleep"):
        with st.spinner("Analyzing your sleep cycle..."):
            time.sleep(1)  # Reduced animation time

        if validate_date_and_times(date, sleep_start, sleep_end):
            start_datetime = datetime.strptime(sleep_start, "%H:%M")
            end_datetime = datetime.strptime(sleep_end, "%H:%M")

            # Ensure that end time is not earlier than start time (same day)
            if end_datetime <= start_datetime:
                sleep_hours = calculate_sleep_duration(start_datetime, end_datetime)
            else:
                sleep_hours = (end_datetime - start_datetime).seconds / 3600

            # Insert data into Supabase
            data = {
                "user_id": "test_user",  # Replace with actual authentication if needed
                "date": date.strftime("%Y-%m-%d"),
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
            }

            try:
                supabase.table("sleep_data").insert(data).execute()
                
                # Display results
                st.success(f"You slept for *{sleep_hours:.1f}* hours.")
                st.markdown(f"<div class='sleep-container'><h3>{get_sleep_advice(sleep_hours)}</h3></div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error saving data: {str(e)}")

    # Weekly Sleep Analysis Section
    if st.button("View Weekly Sleep Analysis"):
        st.subheader("📊 Weekly Sleep Analysis")

        try:
            # Fetch last 7 days' data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=6)
            
            response = supabase.table("sleep_data").select("*")\
                .gte("date", start_date.strftime("%Y-%m-%d"))\
                .lte("date", end_date.strftime("%Y-%m-%d"))\
                .execute()

            if response.data:
                df = pd.DataFrame(response.data)
                
                # Convert date strings to datetime objects
                df["date"] = pd.to_datetime(df["date"])
                
                # Sort by date in ascending order
                df = df.sort_values("date")

                # Convert sleep_start & sleep_end to datetime for calculations
                df["sleep_start"] = pd.to_datetime(df["sleep_start"], format="%H:%M:%S", errors="coerce").dt.time
                df["sleep_end"] = pd.to_datetime(df["sleep_end"], format="%H:%M:%S", errors="coerce").dt.time

                df["sleep_hours"] = df.apply(lambda row: calculate_sleep_duration(
                    datetime.combine(datetime.today(), row["sleep_start"]),
                    datetime.combine(datetime.today(), row["sleep_end"])
                ), axis=1)

                # Plot sleep trends with improved formatting
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.lineplot(data=df, x="date", y="sleep_hours", marker="o", ax=ax)
                
                # Improve x-axis formatting
                ax.set_xlabel("Date")
                ax.set_ylabel("Hours Slept")
                plt.title("Your Sleep Duration Over the Last 7 Days")
                
                # Rotate date labels for better readability
                plt.xticks(rotation=45)
                
                # Format dates as 'MMM DD' (e.g., 'Feb 06')
                ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d'))
                
                # Set y-axis limits for better visualization
                ax.set_ylim(0, max(df["sleep_hours"]) + 1)
                
                # Add grid for better readability
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
                
                st.pyplot(fig)

                # Calculate and display statistics
                avg_sleep = df["sleep_hours"].mean()
                st.markdown(f"### 💤 Average Sleep Duration: *{avg_sleep:.1f} hours*")
                
                # Weekly insights
                min_sleep = df["sleep_hours"].min()
                max_sleep = df["sleep_hours"].max()
                sleep_consistency = df["sleep_hours"].std()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Shortest Sleep", f"{min_sleep:.1f} hrs")
                with col2:
                    st.metric("Longest Sleep", f"{max_sleep:.1f} hrs")
                with col3:
                    st.metric("Sleep Consistency", f"±{sleep_consistency:.1f} hrs")

                # Provide personalized insights
                if avg_sleep < 6:
                    st.warning("📉 Your average sleep is below recommended levels. Try to get more rest!")
                elif avg_sleep > 9:
                    st.warning("⚠️ You're sleeping more than average. Consider adjusting your schedule.")
                else:
                    st.success("🎯 Great job! Your sleep duration is within the healthy range.")

                if sleep_consistency > 2:
                    st.warning("🔄 Your sleep schedule is quite irregular. Try to maintain consistent sleep times.")
                else:
                    st.success("✨ You're maintaining a consistent sleep schedule!")

            else:
                st.info("No sleep data found for the past week. Start logging your sleep to see trends!")
                
        except Exception as e:
            st.error(f"Error analyzing sleep data: {str(e)}")


@login_required
def dashboard():
    st.title("🎉 Welcome to MindMate!")
    st.write(f"Hello, {st.session_state.user.email}")
    
    # Dashboard navigation
    features = {
        "Chatbot": chatbot_page,
        "Community": community_page,
        "Mood Tracker": emotions_page,
        "Meditation": meditation_page,
        "Music Therapy": music_page,
        "Journalling": journal_page,
        "Daily Quote": quote_page,
        "Sleep Cycle": sleep_page,
    }
    
    selected_feature = st.sidebar.selectbox("Navigate to:", list(features.keys()))
    features[selected_feature]()

def main():
    st.set_page_config(page_title="MindMate", layout="wide")
    init_session_state()
    apply_custom_styles()
    
    # Sidebar navigation when logged in
    if st.session_state.user:
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
    
    # Main navigation
    pages = {
        "home": lambda: st.title("🧠 Welcome to MindMate"),
        "login": login_page,
        "signup": signup_page,
        "dashboard": dashboard
    }
    
    if st.session_state.page in pages:
        pages[st.session_state.page]()
    
    # Show login/signup buttons on home page
    if st.session_state.page == "home":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                st.session_state.page = "login"
                st.rerun()
        with col2:
            if st.button("Sign Up"):
                st.session_state.page = "signup"
                st.rerun()

if __name__ == "__main__":

    main()