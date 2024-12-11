import os
import streamlit as st
from dotenv import load_dotenv
from transcript_fetcher import fetch_transcript


# Load environment variables
load_dotenv()
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Function to extract video ID
def extract_video_id(youtube_url):
    from urllib.parse import urlparse, parse_qs
    try:
        parsed_url = urlparse(youtube_url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
        else:
            return None
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")
        return None

# Authentication logic
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid username or password.")

# Main application after login
def main_app():
    from summarizer import summarize_text
    # from melo_module import generate_audio
    st.title("YouTube Transcript Summarizer")
    st.subheader("Fetch, summarize YouTube transcripts")

    # Input for YouTube video URL
    youtube_url = st.text_input("Enter YouTube Video URL:", help="Paste the full YouTube video URL here.")

    # Optional system prompt customization
    default_system_prompt = "You are an assistant that summarizes text concisely."
    system_prompt = st.text_area("System Prompt (Optional)", default_system_prompt, help="Modify the agent's behavior.")

    # Custom min and max lengths
    col1, col2 = st.columns(2)
    with col1:
        min_length = st.number_input("Min Length", min_value=10, max_value=10000, value=300, step=100)
    with col2:
        max_length = st.number_input("Max Length", min_value=20, max_value=10000, value=500, step=100)

    # Checkbox for audio generation
    # generate_audio_checkbox = st.checkbox("Generate audio for the summary")

    # Button to fetch and summarize
    if st.button("Summarize"):
        if youtube_url:
            # Extract video ID
            video_id = extract_video_id(youtube_url)
            if video_id:
                with st.spinner("Fetching transcript..."):
                    transcript = fetch_transcript(video_id)

                if transcript:
                    st.success("Transcript fetched successfully!")
                    with st.spinner("Summarizing..."):
                        summary = summarize_text(transcript, min_length=min_length, max_length=max_length, system_prompt=system_prompt)

                    st.subheader("Summary:")
                    st.write(summary)
                else:
                    st.error("Failed to fetch transcript. Please check the video URL or language availability.")
            else:
                st.error("Invalid YouTube URL. Please provide a valid link.")
        else:
            st.warning("Please enter a valid YouTube Video URL.")


# Main execution logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    main_app()
