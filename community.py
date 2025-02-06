import streamlit as st
import pandas as pd
from datetime import datetime
import uuid  # Unique user ID generator

def community():
    # Initialize session state variables if they don't exist
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
