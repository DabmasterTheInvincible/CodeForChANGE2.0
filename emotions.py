import streamlit as st
import streamlit_calendar as st_cal
import datetime
import pandas as pd
from collections import Counter
def emotions():

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
    current_date = datetime.datetime.now().date().isoformat()

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

        sorted_dates = sorted(datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in dates)
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
