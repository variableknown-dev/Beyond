from models.ollama_provider import OllamaProvider


# =========================================================
# DEFAULT MODEL
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
    Send a conversation to the selected model provider.

    If no provider is supplied, Aarya falls back to
    the local Ollama provider.
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
    Stream a conversation from the selected model provider.
    """

    if model_provider is None:
        model_provider = DEFAULT_MODEL

    if not hasattr(
        model_provider,
        "chat_stream",
    ):

        # Fallback for providers that don't support
        # streaming yet.

        yield model_provider.chat(
            messages
        )

        return

    yield from model_provider.chat_stream(
        messages
    )
