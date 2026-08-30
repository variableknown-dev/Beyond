import os
import time

from google import genai
from google.genai import types

from models.base import ModelProvider
from brain.prompt import SYSTEM_PROMPT


class GeminiProvider(ModelProvider):
    """
    Gemini model provider.

    Supports:
        - normal responses
        - streaming responses
        - automatic retry for temporary 503/429 errors
    """

    def __init__(
        self,
        model="gemini-3.7-flash",
        max_retries=3,
        retry_delay=3,
    ):

        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

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
    # CHECK RETRYABLE ERROR
    # =========================================================

    def _is_retryable(self, error):

        status_code = getattr(
            error,
            "status_code",
            None,
        )

        if status_code is None:
            status_code = getattr(
                error,
                "code",
                None,
            )

        return status_code in (
            429,
            500,
            502,
            503,
            504,
        )

    # =========================================================
    # NORMAL CHAT
    # =========================================================

    def chat(self, messages):

        contents = self._build_contents(
            messages
        )

        last_error = None


