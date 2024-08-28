# api_calls.py
import openai
from error_handling import handle_error, CustomAPIError


def initialize_openai_client(api_key):
    try:
        openai.api_key = api_key
        return openai
    except Exception as e:
        handle_error(CustomAPIError(f"Failed to initialize OpenAI client: {str(e)}"))
        raise


def translate_text(client, text):
    try:
        response = client.Completion.create(
            model="text-davinci-003", prompt=text, max_tokens=1000
        )
        return response.choices[0].text.strip()
    except Exception as e:
        handle_error(CustomAPIError(f"API Request failed: {str(e)}"))
        raise
