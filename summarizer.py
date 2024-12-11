import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

client = OpenAI(
    api_key=os.environ['TOKEN'],
)

def summarize_text(transcript, system_prompt, user_prompt_template, min_tokens=10, max_tokens=500):
    """
    Summarize text using OpenAI's GPT model.
    :param transcript: The transcript text (or placeholder if not used)
    :param system_prompt: The system message to guide the summarizer's behavior
    :param user_prompt_template: A template for the user prompt, including placeholders for dynamic content
    :param min_tokens: Minimum number of tokens for the summary
    :param max_tokens: Maximum number of tokens for the summary
    :return: Summary as a string
    """
    try:
        user_prompt = user_prompt_template.format(
            text=transcript,
            min_tokens=min_tokens,
            max_tokens=max_tokens
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,  # Limit output tokens
        )

        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"An error occurred: {str(e)}"
