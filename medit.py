import streamlit as st
import time

# Set page config
st.set_page_config(page_title="MindMate AI - Guided Self-Care", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to:", ["Meditation", "Journaling", "Music Therapy"])

# 1️⃣ Meditation Section
if option == "Meditation":

    # Fixed Heart Animation
    heart_animation = """
            <style>
            @keyframes breathe {
                0% { transform: scale(1); opacity: 0.8; }
                25% { transform: scale(1.2); opacity: 1; }
                50% { transform: scale(1.4); opacity: 1.2; }
                75% { transform: scale(1.2); opacity: 1; }
                100% { transform: scale(1); opacity: 0.8; }
            }

            .heart-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 300px;
                position: relative;
            }

            .heart {
                width: 100px;
                height: 100px;
                background: linear-gradient(45deg, #FF69B4, #FF1493);
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%); /* Removed rotate(-45deg) */
                animation: breathe 6s infinite ease-in-out;
                box-shadow: 0 0 30px rgba(255, 105, 180, 0.5);
}


            .heart:before, .heart:after {
                content: "";
                width: 100px;
                height: 100px;
                background: linear-gradient(45deg, #FF69B4, #FF1493);
                border-radius: 50%;
                position: absolute;
            }

            .heart:before {
                top: -50px;
                left: 0;
            }

            .heart:after {
                left: 50px;
                top: 0;
            }

            </style>
    """

    st.markdown(heart_animation, unsafe_allow_html=True)

    # Title
    st.title("🧘 Guided Meditation")
    st.write("Follow the animation and breathe deeply.")

    # Display Heart Animation
    st.markdown('<div class="heart-container"><div class="heart"></div></div>', unsafe_allow_html=True)

    # Breathing Instructions
    st.subheader("🌬️ Breathing Instructions")

    meditation_steps = [
        "👉 Inhale deeply for **4 seconds**... (Heart expands)",
        "😌 Hold your breath for **4 seconds**... (Heart at full size)",
        "💨 Slowly exhale for **6 seconds**... (Heart shrinks back)",
        "🌊 Imagine yourself in a peaceful place...",
        "🔄 Repeat this cycle for **5 minutes**..."
    ]

    for step in meditation_steps:
        st.write(step)
        time.sleep(4)

    # Optional Background Music
    st.audio(r"C:\Users\akshi\Downloads\relaxing-music-with-echo-bell-high-frequency-284495.mp3", format="audio/mp3")

# 2️⃣ Journaling Section
elif option == "Journaling":
    st.header("📖 Daily Journal")
    st.write("Write down your thoughts and feelings.")

    # Text input for journaling
    journal_entry = st.text_area("How are you feeling today?", placeholder="Write here...")

    # Save the entry (optional: can be connected to a database)
    if st.button("Save Entry"):
        with open("journal_entries.txt", "a") as f:
            f.write(journal_entry + "\n")
        st.success("Journal entry saved!")

# 3️⃣ Music Therapy Section
elif option == "Music Therapy":
    st.header("🎵 Music Therapy")
    st.write("Relax with calming music.")

    # Embed a YouTube video for calming music
    st.video("https://www.youtube.com/watch?v=1ZYbU82GVz4")  # Replace with your preferred link

    # Option to upload custom music
    st.write("Upload your favorite relaxing music:")
    uploaded_file = st.file_uploader("Choose a file", type=["mp3"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mp3")
