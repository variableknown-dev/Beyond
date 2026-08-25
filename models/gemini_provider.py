import os

from google import genai
from google.genai import types

from models.base import ModelProvider
from brain.prompt import SYSTEM_PROMPT


class GeminiProvider(ModelProvider):
    """
    Model provider for Google's Gemini API.

    Supports both:
        - normal complete responses
        - streaming responses
    """

    def __init__(self, model="gemini-3.7-flash"):

        self.model = model

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    # =========================================================
    # BUILD CONTENTS
    # =========================================================

    def _build_contents(self, messages):

        contents = []

        for message in messages:

            role = message.get(
                "role",
                "user",
            )

            content = message.get(
                "content",
                "",
            )

            if not content:
                continue

            if role == "assistant":
                role = "model"

            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part.from_text(
                            text=content
                        )
                    ],
                )
            )

        return contents

    # =========================================================
    # NORMAL CHAT
    # =========================================================

    def chat(self, messages):

        contents = self._build_contents(
            messages
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        return response.text

    # =========================================================
    # STREAMING CHAT
    # =========================================================

    def chat_stream(self, messages):

        contents = self._build_contents(
            messages
        )

        response_stream = (
            self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
        )

        for chunk in response_stream:

            text = getattr(
                chunk,
                "text",
                None,
            )

            if text:
                yield text
