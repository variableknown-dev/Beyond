from brain.process import process, process_stream
from brain.memory import init_memory

from platforms.detector import detect_platform


class Aarya:
    """
    Main interface to the Aarya AI assistant.

    The model provider and platform can both be injected,
    allowing different Aarya installations to use different
    models and capabilities.
    """

    def __init__(
        self,
        platform=None,
        model_provider=None,
    ):

        # -----------------------------------------
        # Initialize local memory
        # -----------------------------------------

        init_memory()

        # -----------------------------------------
        # Detect platform
        # -----------------------------------------

        if platform is None:
            platform = detect_platform()

        self.platform = platform

        # -----------------------------------------
        # Model provider
        # -----------------------------------------

        self.model_provider = model_provider

    # =========================================================
    # NORMAL CHAT
    # =========================================================

    def chat(
        self,
        user_input: str,
    ) -> str:
        """
        Send a message to Aarya and receive the
        complete response at once.
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
        Send a message to Aarya and stream the response
        as it is generated.

        This is intended for the web interface and other
        clients that support streaming responses.
        """

        user_input = user_input.strip()

        if not user_input:
            return

        yield from process_stream(
            user_input,
            platform=self.platform,
            model_provider=self.model_provider,
        )
