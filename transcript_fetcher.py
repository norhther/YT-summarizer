from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def fetch_transcript(video_id, languages=['en', 'es'], cookies=None):
    """
    Fetch the transcript for a YouTube video using youtube-transcript-api.
    :param video_id: The ID of the YouTube video
    :param languages: List of language codes to prioritize
    :param cookies: Path to a cookies file (for age-restricted videos)
    :return: Combined transcript as a single string or None if unavailable
    """
    try:
        # Fetch the transcript for the video
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages, cookies=cookies)

        # Use a formatter for cleaner output
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)

        return formatted_transcript

    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

