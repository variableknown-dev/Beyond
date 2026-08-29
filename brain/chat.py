from models.ollama_provider import OllamaProvider


# =========================================================
# DEFAULT LOCAL MODEL
# =========================================================

DEFAULT_MODEL = OllamaProvider(
    model="qwen3:8b"
)


# =========================================================
# NORMAL CHAT
# =========================================================

def ask_aarya(
    messages,
    model_provider=None,
):
    """
    Send messages to the selected model provider.

    If no provider is supplied, use local Ollama.
    """

    if model_provider is None:

        model_provider = DEFAULT_MODEL

    return model_provider.chat(
        messages
    )


# =========================================================
# STREAMING CHAT
# =========================================================

def stream_aarya(
    messages,
    model_provider=None,
):
    """
    Stream messages from the selected model provider.
    """

    if model_provider is None:

        model_provider = DEFAULT_MODEL

    # ---------------------------------------------------------
    # Provider supports streaming
    # ---------------------------------------------------------

    if hasattr(
        model_provider,
        "chat_stream",
    ):

        yield from model_provider.chat_stream(
            messages
        )

        return

    # ---------------------------------------------------------
    # Provider does not support streaming
    # ---------------------------------------------------------

    response = model_provider.chat(
        messages
    )

    if response:

        yield response
