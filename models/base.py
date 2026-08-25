from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """
    Base interface for all AI model providers.

    Every model backend used by Aarya should implement
    this interface.
    """

    @abstractmethod
    def chat(self, messages):
        """
        Send a list of messages to the model.

        Args:
            messages: List of chat messages.

        Returns:
            The model's response as a string.
        """
        pass
