import streamlit as st
import pandas as pd
import datetime
import streamlit_calendar
# Define available emojis for emotions
emotions = {
    "😃 Happy": "😃",
    "😢 Sad": "😢",
    "😟 Anxious": "😟",
    "😌 Calm": "😌",
    "🤩 Excited": "🤩",
    "😴 Tired": "😴"
    "😡 Angry": "😡",
}

# Initialize session state to store calendar data
if "calendar_data" not in st.session_state:
    st.session_state.calendar_data = {}

# Get today's date
today = datetime.date.today()
current_month = today.strftime("%B %Y")

# Sidebar for selecting an emotion
st.sidebar.title("🙂 Select an Emotion")
selected_emotion = st.sidebar.selectbox("Choose your mood:", list(emotions.keys()))
selected_emoji = emotions[selected_emotion]

# Display selected emoji
st.sidebar.write("**Click a day on the calendar to assign the selected emoji**:")
st.sidebar.markdown(f"""
    <div style="font-size: 40px; text-align: center;">
         {selected_emoji}
    </div>
""", unsafe_allow_html=True)

# Convert stored emoji data into calendar event format
calendar_events = [
    {"start": date, "title": emoji} for date, emoji in st.session_state.calendar_data.items()
]

# Display the calendar
st.title("📅 Emoji Selection Calendar")
calendar = streamlit_calendar.calendar(
    events=calendar_events,
    callbacks=["dateClick"],  # Enable dateClick event
    license_key="CC-Attribution-NonCommercial-NoDerivatives",
)

# Handle the date click event
if calendar and "dateClick" in calendar:
    clicked_date = calendar["dateClick"]["dateStr"]  # Get the clicked date (YYYY-MM-DD)
    
    # Assign the selected emoji to that date
    st.session_state.calendar_data[clicked_date] = selected_emoji

# Display assigned emotions in a table
st.subheader("📆 Your Monthly Emotion Tracker")
calendar_df = pd.DataFrame(
    [{"Date": date, "Emotion": emoji} for date, emoji in st.session_state.calendar_data.items()]
)

st.table(calendar_df)

# Reset button to clear today's emoji
if st.button("Reset Today's Mood"):
    today_str = today.strftime("%Y-%m-%d")
    if today_str in st.session_state.calendar_data:
        del st.session_state.calendar_data[today_str]
    st.experimental_rerun()