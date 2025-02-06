import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
from supabase import create_client, Client

# Supabase credentials (replace with your values)
SUPABASE_URL = "https://hjcwijsywehnuojrjdps.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqY3dpanN5d2VobnVvanJqZHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3Nzg4MjQsImV4cCI6MjA1NDM1NDgyNH0.rVyVwhjEsXQ7V9ntWgx1hHDjQOxq4SJaWHDPONBfjP4"

def sleep():
    # Connect to Supabase
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