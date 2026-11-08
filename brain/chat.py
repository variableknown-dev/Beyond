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

def ask_beyond(
    messages,
    model_provider=None,
):

    if model_provider is None:
        model_provider = DEFAULT_MODEL

    return model_provider.chat(
        messages
    )


# =========================================================
# STREAMING CHAT
# =========================================================

def stream_beyond(
    messages,
    model_provider=None,
):

    if model_provider is None:
        model_provider = DEFAULT_MODEL

    if not hasattr(
        model_provider,
        "chat_stream",
    ):

        yield model_provider.chat(
            messages
        )

        return

    yield from model_provider.chat_stream(
        messages
    )
