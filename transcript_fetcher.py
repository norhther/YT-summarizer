from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(video_id, languages=['en', 'es']):
    """
    Fetch the transcript for a YouTube video.
    :param video_id: The ID of the YouTube video
    :param languages: List of language codes to prioritize
    :return: Combined transcript as a single string
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None
