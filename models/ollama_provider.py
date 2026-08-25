from ollama import chat

from models.base import ModelProvider
from brain.prompt import SYSTEM_PROMPT


class OllamaProvider(ModelProvider):
    """
    Model provider for local Ollama models.
    """

    def __init__(self, model="qwen3:8b"):
        self.model = model

    def chat(self, messages):
        """
        Send messages to the selected Ollama model.

        Args:
            messages: List of conversation messages.

        Returns:
            The model's response as a string.
        """

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *messages,
            ],
        )

        return response["message"]["content"]

