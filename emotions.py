import streamlit as st
import streamlit_calendar as st_cal
import datetime
import pandas as pd
from collections import Counter

# Set page config to dark theme
st.set_page_config(page_title="Emoji Calendar", layout="wide")

# Updated CSS focusing on emoji display
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
    
    /* Make emoji larger */
    .fc-event-title {
        font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
        font-size: 40px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Button styling */
    .emoji-button {
        background-color: #2D2D2D;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 15px;
        margin: 5px;
        cursor: pointer;
        font-size: 48px !important;
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
current_date = datetime.datetime.now().date().isoformat()

# Create emoji buttons
st.write("### How are you feeling today?")
cols = st.columns(len(emoji_meanings))
for idx, (emoji, meaning) in enumerate(emoji_meanings.items()):
    with cols[idx]:
        if st.button(emoji, key=f"emoji_{idx}", help=meaning):
            st.session_state.calendar_data[current_date] = emoji
            st.rerun()

# Convert stored emojis to calendar events
events = [
    {
        "title": emoji,
        "start": date,
        "allDay": True,
        "display": "block",
        "backgroundColor": "transparent",
        "textColor": "#FFFFFF",
        "className": "emoji-event"
    }
    for date, emoji in st.session_state.calendar_data.items()
]

# Display calendar
st_cal.calendar(events=events, options=calendar_options)

# Weekly Analysis
if st.session_state.calendar_data:
    st.write("### Weekly Mood Analysis")
    
    # Convert data to DataFrame
    df = pd.DataFrame([
        {"date": date, "mood": emoji, "mood_name": emoji_meanings[emoji]}
        for date, emoji in st.session_state.calendar_data.items()
    ])
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.isocalendar().week
    
    # Get current week
    current_week = datetime.datetime.now().isocalendar()[1]
    
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