from openai import OpenAI
import requests


def translate_chinese_phrases(text_holder_path, client):
    """Translates the Chinese text stored in the text holder file."""
    with open(text_holder_path, "r", encoding="utf-8") as holder:
        content = holder.read().strip()

    print(f"\nSending the following text to the API for translation:\n{content}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Adjust model as needed
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional translator with expertise in translating video game localization files. "
                    "You are given text extracted from .YML from a Crusader Kings 3 or even a mod for the game."
                    "Translate only the Chinese text into English while preserving the identifiers and formatting."
                ),
            },
            {"role": "user", "content": content},
        ],
    )

    translated_content = response.choices[0].message.content.strip()

    print(f"\nReceived the following translated content:\n{translated_content}")

    translated_holder_path = f"{text_holder_path}_translated.txt"
    with open(translated_holder_path, "w", encoding="utf-8") as translated_holder:
        translated_holder.write(translated_content)

    return translated_holder_path


import requests


def generic_openai_api_call(
    model, endpoint, payload, client, max_tokens=None, **kwargs
):
    """
    A generic function to handle OpenAI API calls.

    Args:
    - model (str): The model to use (e.g., 'gpt-4', 'gpt-3.5-turbo').
    - endpoint (str): The API endpoint to call (e.g., '/v1/chat/completions').
    - payload (dict): The payload for the API call (e.g., messages for chat completions).
    - client: The OpenAI API client initialized with the API key.
    - max_tokens (int, optional): The maximum number of tokens to generate.
    - **kwargs: Additional parameters like stop sequences, temperature, etc.

    Returns:
    - dict: The API response.
    """
    try:
        # Prepare the payload with the model and max_tokens
        payload.update({"model": model, "max_tokens": max_tokens})

        # Add any additional parameters from kwargs to the payload
        payload.update(kwargs)

        # Perform the API call
        headers = {"Authorization": f"Bearer {client.api_key}"}
        response = requests.post(endpoint, json=payload, headers=headers)

        # Check for errors in the response
        response.raise_for_status()

        # Return the response as a JSON object
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {str(e)}")
        raise


def batch_openai_api_call(
    input_file_path, model, endpoint, client, completion_window="24h", **kwargs
):
    """
    A function to handle OpenAI Batch API calls.

    Args:
    - input_file_path (str): Path to the input JSONL file.
    - model (str): The model to use for batch processing.
    - endpoint (str): The API endpoint to call (e.g., '/v1/chat/completions').
    - client: The OpenAI API client initialized with the API key.
    - completion_window (str): The batch processing time window (default is 24 hours).
    - **kwargs: Additional parameters like metadata, etc.

    Returns:
    - dict: The Batch API response.
    """
    try:
        # Upload the batch input file
        batch_input_file = client.files.create(
            file=open(input_file_path, "rb"), purpose="batch"
        )

        # Create the batch
        batch_response = client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint=endpoint,
            completion_window=completion_window,
            **kwargs,
        )

        # Return the batch response
        return batch_response

    except requests.exceptions.RequestException as e:
        print(f"Batch API Request failed: {str(e)}")
        raise


# this is nothing
