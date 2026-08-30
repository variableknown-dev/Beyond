from brain.planner import create_plan
from brain.executor import execute_plan
from brain.chat import ask_aarya, stream_aarya
from brain.context import add_message, get_messages

from brain.parser import extract_memory
from brain.memory import remember


# =========================================================
# MEMORY TRIGGER
# =========================================================

MEMORY_TRIGGERS = (
    "remember that",
    "remember this",
    "remember",
    "don't forget",
    "dont forget",
    "my name is",
    "my favorite",
    "my favourite",
    "i prefer",
    "i like",
    "i don't like",
    "i dont like",
    "i hate",
    "i love",
    "i use",
    "i am using",
    "i'm using",
    "i live",
    "i'm from",
    "im from",
)


def should_extract_memory(user_input: str) -> bool:
    """
    Only run the memory extraction model when the user
    appears to be giving Aarya something worth remembering.

    This prevents an unnecessary AI request on normal
    messages such as:
        "hello"
        "how are you?"
        "explain photosynthesis"
    """

    text = user_input.lower().strip()

    return any(
        trigger in text
        for trigger in MEMORY_TRIGGERS
    )


# =========================================================
# MEMORY
# =========================================================

def handle_memory(
    user_input,
    model_provider=None,
):
    """
    Extract and save long-term memory only when appropriate.

    The model provider is passed through so Render uses Gemini
    instead of accidentally falling back to local Ollama.
    """

    if not should_extract_memory(user_input):
        return

    try:

        memory = extract_memory(
            user_input,
            model_provider=model_provider,
        )

        if memory is None:
            return

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
        )

        print(
            f"[MEMORY] Saved: "
            f"{memory['category']} / "
            f"{memory['key']} = "
            f"{memory['value']}"
        )

    except Exception as error:

        # Memory failure should NEVER prevent Aarya
        # from answering the user's actual message.

        print(
            f"[MEMORY] Memory extraction failed: {error}"
        )


# =========================================================
# NORMAL PROCESSING
# =========================================================

def process(
    user_input,
    platform=None,
    model_provider=None,
):
    """
    Main processing pipeline for Aarya.
    """

    user_input = user_input.strip()

    if not user_input:
        return ""

    # ---------------------------------------------------------
    # SAVE USER MESSAGE
    # ---------------------------------------------------------

    add_message(
        "user",
        user_input,
    )

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    handle_memory(
        user_input,
        model_provider=model_provider,
    )

    # ---------------------------------------------------------
    # CREATE PLAN
    # ---------------------------------------------------------

    plan = create_plan(
        user_input
    )

    # ---------------------------------------------------------
    # EXECUTE SKILLS
    # ---------------------------------------------------------

    reply = execute_plan(
        plan,
        platform=platform,
    )

    # ---------------------------------------------------------
    # SKILL HANDLED REQUEST
    # ---------------------------------------------------------

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
        )

        return reply

    # ---------------------------------------------------------
    # NORMAL AI CHAT
    # ---------------------------------------------------------

    reply = ask_aarya(
        get_messages(),
        model_provider=model_provider,
    )

    if reply is None:
        reply = ""

    reply = str(reply)

    # ---------------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # ---------------------------------------------------------

    if reply.strip():

        add_message(
            "assistant",
            reply,
        )

    return reply


# =========================================================
# STREAMING PROCESSING
# =========================================================

def process_stream(
    user_input,
    platform=None,
    model_provider=None,
):
    """
    Streaming processing pipeline.

    Memory and skills are handled first.
    If no skill handles the request, Gemini's response
    is streamed directly to the web interface.
    """

    user_input = user_input.strip()

    if not user_input:
        return

    # ---------------------------------------------------------
    # SAVE USER MESSAGE
    # ---------------------------------------------------------

    add_message(
        "user",
        user_input,
    )

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    handle_memory(
        user_input,
        model_provider=model_provider,
    )

    # ---------------------------------------------------------
    # CREATE PLAN
    # ---------------------------------------------------------

    plan = create_plan(
        user_input
    )

    # ---------------------------------------------------------
    # EXECUTE SKILLS
    # ---------------------------------------------------------

    reply = execute_plan(
        plan,
        platform=platform,
    )

    # ---------------------------------------------------------
    # SKILL HANDLED REQUEST
    # ---------------------------------------------------------

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
        )

        yield reply

        return

    # ---------------------------------------------------------
    # STREAM GEMINI RESPONSE
    # ---------------------------------------------------------

    full_response = ""

    try:

        for chunk in stream_aarya(
            get_messages(),
            model_provider=model_provider,
        ):

            if not chunk:
                continue

            full_response += chunk

            yield chunk

    except Exception as error:

        print(
            f"[AARYA] Streaming error: {error}"
        )

        # Only send an error if nothing has already
        # been generated.

        if not full_response:

            yield (
                "Sorry, I ran into an error "
                "while generating that response."
            )

        return

    # ---------------------------------------------------------
    # SAVE COMPLETE RESPONSE
    # ---------------------------------------------------------

    if full_response.strip():

        add_message(
            "assistant",
            full_response,
        )
