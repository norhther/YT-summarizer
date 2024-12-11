import os
import streamlit as st
from dotenv import load_dotenv
from transcript_fetcher import fetch_transcript
from summarizer import summarize_text
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")
COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD", "a-very-secure-password")

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="myapp_",
    password=COOKIE_PASSWORD,
)

if not cookies.ready():
    st.stop()

def extract_video_id(youtube_url):
    from urllib.parse import urlparse, parse_qs
    try:
        parsed_url = urlparse(youtube_url.strip())
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
        else:
            return None
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")
        return None

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    remember_me = st.checkbox("Remember Me")
    login_button = st.button("Login")

    if login_button:
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state["authenticated"] = True
            if remember_me:
                expires_at = datetime.now() + timedelta(days=365)
                cookies.set("auth_token", "logged_in", expires_at=expires_at)
                cookies.save()
            st.rerun()
        else:
            st.error("Invalid username or password.")

def main_app():
    st.title("YouTube Transcript")
    st.subheader("Fetch and NLP'd transcripts from one or multiple YouTube videos")

    youtube_urls_input = st.text_area(
        "Enter YouTube Video URLs (one per line):",
        help="Paste one or more YouTube URLs, each on its own line."
    )

    default_system_prompt = "You are an assistant that summarizes text concisely and accurately."
    system_prompt = st.text_area(
        "System Prompt (Optional)",
        default_system_prompt,
        help="Influence the assistant's overall behavior."
    )

    default_user_prompt = (
        "Please summarize the following text:\n\n{text}\n\n"
        "The summary should have at least {min_tokens} tokens and no more than {max_tokens} tokens."
    )
    user_prompt_template = st.text_area(
        "User Prompt Template (Optional)",
        default_user_prompt,
        help="Customize your request. Use {text}, {min_tokens}, and {max_tokens} as placeholders."
    )

    col1, col2 = st.columns(2)
    with col1:
        min_tokens = st.number_input("Min Tokens", min_value=10, max_value=1000, value=30, step=10)
    with col2:
        max_tokens = st.number_input("Max Tokens", min_value=50, max_value=2000, value=120, step=10)

    # Checkbox to combine transcripts of ALL videos before summarizing
    use_entire_transcript = st.checkbox("Combine all transcripts into one summary", value=False)

    # Initialize session_state for caching if not present
    if "transcripts" not in st.session_state:
        st.session_state["transcripts"] = {}
    if "last_video_urls" not in st.session_state:
        st.session_state["last_video_urls"] = []

    if st.button("Summarize"):
        youtube_urls = [url.strip() for url in youtube_urls_input.splitlines() if url.strip()]

        if not youtube_urls:
            st.warning("Please enter at least one valid YouTube URL.")
            return

        # Check if URLs changed from last time
        urls_changed = (youtube_urls != st.session_state["last_video_urls"])
        st.session_state["last_video_urls"] = youtube_urls

        transcripts = []
        all_valid = True

        # Only fetch if needed
        for url in youtube_urls:
            video_id = extract_video_id(url)
            if not video_id:
                st.error(f"Invalid YouTube URL: {url}")
                all_valid = False
                break

            # Check if transcript is cached
            if video_id in st.session_state["transcripts"] and not urls_changed:
                # Use cached transcript
                transcripts.append(st.session_state["transcripts"][video_id])
            else:
                # Need to fetch transcript (either not cached or URLs changed)
                with st.spinner(f"Fetching transcript for {url}..."):
                    transcript = fetch_transcript(video_id)
                if not transcript:
                    st.error(f"Failed to fetch transcript for {url}. Check if the video is valid or has a transcript.")
                    all_valid = False
                    break
                else:
                    st.success(f"Transcript fetched successfully for {url}!")
                    st.session_state["transcripts"][video_id] = transcript
                    transcripts.append(transcript)

        if not all_valid:
            return

        if use_entire_transcript:
            combined_transcript = "\n\n".join(transcripts)
            with st.spinner("Summarizing all transcripts together..."):
                summary = summarize_text(
                    transcript=combined_transcript,
                    system_prompt=system_prompt,
                    user_prompt_template=user_prompt_template,
                    min_tokens=min_tokens,
                    max_tokens=max_tokens,
                )
            st.markdown("### Combined Answer for All Videos")
            st.write(summary)
        else:
            # Summarize each transcript individually
            for url, transcript in zip(youtube_urls, transcripts):
                with st.spinner(f"Summarizing transcript for {url}..."):
                    summary = summarize_text(
                        transcript=transcript,
                        system_prompt=system_prompt,
                        user_prompt_template=user_prompt_template,
                        min_tokens=min_tokens,
                        max_tokens=max_tokens,
                    )
                st.markdown(f"### Answer for {url}")
                st.write(summary)

# Check authentication from cookie
if "authenticated" not in st.session_state:
    if "auth_token" in cookies and cookies["auth_token"] == "logged_in":
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    main_app()
