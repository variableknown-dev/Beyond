from brain.process import (
    process,
    process_stream,
)

from brain.memory import init_memory

from platforms.detector import detect_platform


class Kashvi:
    """
    Main interface to the Kashvi AI assistant.

    The model provider and platform are injected,
    allowing different Kashvi installations to use
    different models and capabilities.
    """

    def __init__(
        self,
        platform=None,
        model_provider=None,
    ):

        # =====================================================
        # INITIALIZE MEMORY
        # =====================================================

        init_memory()

        # =====================================================
        # DETECT PLATFORM
        # =====================================================

        if platform is None:

            platform = detect_platform()

        self.platform = platform

        # =====================================================
        # MODEL PROVIDER
        # =====================================================

        self.model_provider = model_provider

    # =========================================================
    # NORMAL CHAT
    # =========================================================

    def chat(
        self,
        user_input: str,
    ) -> str:
        """
        Send a message and receive the complete response.
        """

        user_input = user_input.strip()

        if not user_input:

            return ""

        return process(
            user_input,
            platform=self.platform,
            model_provider=self.model_provider,
        )

    # =========================================================
    # STREAMING CHAT
    # =========================================================

    def chat_stream(
        self,
        user_input: str,
    ):
        """
        Send a message and stream the response.
        """

        user_input = user_input.strip()

        if not user_input:

            return

        yield from process_stream(
            user_input,
            platform=self.platform,
            model_provider=self.model_provider,
        )
