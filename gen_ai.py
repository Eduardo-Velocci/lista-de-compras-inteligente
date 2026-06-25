# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types


def generate(prompt, img, img_mime):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3.1-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type=img_mime,
                    data=img,
                ),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="MINIMAL",
        ),
        response_mime_type="application/json",
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return response

if __name__ == "__main__":
    generate()


