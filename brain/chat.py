# =========================================================
# MODEL CHAT HELPERS
# =========================================================

def ask_aarya(
    messages,
    model_provider,
):
    """
    Send a conversation to the selected model provider.

    A model provider must be explicitly supplied.
    This prevents the hosted version of Aarya from
    accidentally trying to use local Ollama.
    """

    if model_provider is None:
        raise RuntimeError(
            "Aarya requires a model provider."
        )

    return model_provider.chat(
        messages
    )


# =========================================================
# STREAMING CHAT
# =========================================================

def stream_aarya(
    messages,
    model_provider,
):
    """
    Stream a conversation from the selected model provider.
    """

    if model_provider is None:
        raise RuntimeError(
            "Aarya requires a model provider."
        )

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
