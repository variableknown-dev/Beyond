import os
import time

from google import genai
from google.genai import types

from models.base import ModelProvider
from brain.prompt import SYSTEM_PROMPT


class GeminiProvider(ModelProvider):
    """Gemini provider with normal and streaming responses."""

    def __init__(
        self,
        model="gemini-3.7-flash",
        max_retries=2,
        retry_delay=1,
    ):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.model = model
        self.max_retries = max(0, int(max_retries))
        self.retry_delay = max(0.5, float(retry_delay))

        self.client = genai.Client(api_key=api_key)

    def _build_contents(self, messages):
        contents = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if not isinstance(content, str) or not content.strip():
                continue

            if role == "assistant":
                role = "model"
            elif role != "model":
                role = "user"

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=content)],
                )
            )

        return contents

    @staticmethod
    def _is_retryable(error):
        status_code = getattr(error, "status_code", None)

        if status_code is None:
            status_code = getattr(error, "code", None)

        if status_code is None:
            response = getattr(error, "response", None)
            status_code = getattr(response, "status_code", None)

        return status_code in (429, 500, 502, 503, 504)

    def _generate_config(self):
        return types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal",
            ),
        )

    def _generate_from_contents(self, contents):
        if not contents:
            return ""

        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=self._generate_config(),
                )

                text = getattr(response, "text", None)
                return text.strip() if isinstance(text, str) else ""

            except Exception as error:
                last_error = error

                if (
                    attempt >= self.max_retries
                    or not self._is_retryable(error)
                ):
                    break

                delay = self.retry_delay * (2 ** attempt)
                print(
                    f"Gemini temporary error; retrying in "
                    f"{delay:.1f}s "
                    f"({attempt + 1}/{self.max_retries}): {error}",
                    flush=True,
                )
                time.sleep(delay)

        raise RuntimeError(
            f"Gemini request failed after retries: {last_error}"
        ) from last_error

    def chat(self, messages):
        return self._generate_from_contents(self._build_contents(messages))

    def chat_with_image(self, messages, image_data, mime_type):
        """Answer the latest user turn with an in-memory image attachment."""
        if not messages or messages[-1].get("role") != "user":
            raise ValueError("An image must be attached to the latest user message.")

        latest_text = messages[-1].get("content", "Describe this image.")
        contents = self._build_contents(messages[:-1])
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=latest_text),
                    types.Part.from_bytes(data=image_data, mime_type=mime_type),
                ],
            )
        )
        return self._generate_from_contents(contents)

    def chat_stream(self, messages):
        contents = self._build_contents(messages)

        if not contents:
            return

        last_error = None

        for attempt in range(self.max_retries + 1):
            yielded_text = False

            try:
                stream = self.client.models.generate_content_stream(
                    model=self.model,
                    contents=contents,
                    config=self._generate_config(),
                )

                for chunk in stream:
                    text = getattr(chunk, "text", None)

                    if isinstance(text, str) and text:
                        yielded_text = True
                        yield text

                return

            except Exception as error:
                last_error = error

                # Never restart a partially delivered response:
                # doing so could duplicate text in the UI.
                if yielded_text:
                    raise

                if (
                    attempt >= self.max_retries
                    or not self._is_retryable(error)
                ):
                    break

                delay = self.retry_delay * (2 ** attempt)
                print(
                    f"Gemini streaming error; retrying in "
                    f"{delay:.1f}s "
                    f"({attempt + 1}/{self.max_retries}): {error}",
                    flush=True,
                )
                time.sleep(delay)

        raise RuntimeError(
            f"Gemini streaming request failed after retries: {last_error}"
        ) from last_error
