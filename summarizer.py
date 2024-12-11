import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

client = OpenAI(
  api_key=os.environ['TOKEN'],
)

def summarize_text(text, min_length=30, max_length=120, system_prompt="You are an assistant that summarizes text concisely."):
    """
    Summarize text using OpenAI's GPT model.
    :param text: The text to summarize
    :param min_length: Minimum length of the summary
    :param max_length: Maximum length of the summary
    :param system_prompt: The system message to guide the summarizer's behavior
    :return: Summary as a string
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following text in a concise manner, in the language of the text, "
                               f"with a minimum of {min_length} words and a maximum of {max_length} words:\n\n{text}",
                },
            ],
            max_tokens=max_length * 2,  # Token approximation for words
        )
        # Extract the summary from the response
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"An error occurred: {str(e)}"
