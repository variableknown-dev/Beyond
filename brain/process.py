from brain.planner import create_plan
from brain.executor import execute_plan

from brain.chat import (
    ask_aarya,
    stream_aarya,
)

from brain.context import (
    add_message,
    get_messages,
)

from brain.parser import extract_memory
from brain.memory import remember


# =========================================================
# NORMAL PROCESSING
# =========================================================

def process(
    user_input,
    platform=None,
    model_provider=None,
):
    """
    Main entry point for Aarya.

    The selected model provider is passed through
    the entire processing pipeline.
    """

    # ---------------------------------------------------------
    # ADD USER MESSAGE
    # ---------------------------------------------------------

    add_message(
        "user",
        user_input,
    )

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    memory = extract_memory(
        user_input,
        model_provider=model_provider,
    )

    if memory is not None:

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
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
    # SKILL RESPONSE
    # ---------------------------------------------------------

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
        )

        return reply

    # ---------------------------------------------------------
    # MODEL RESPONSE
    # ---------------------------------------------------------

    reply = ask_aarya(
        get_messages(),
        model_provider=model_provider,
    )

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
    Streaming version of Aarya's processing pipeline.

    The selected model provider is passed through
    memory extraction and model generation.
    """

    # ---------------------------------------------------------
    # ADD USER MESSAGE
    # ---------------------------------------------------------

    add_message(
        "user",
        user_input,
    )

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    memory = extract_memory(
        user_input,
        model_provider=model_provider,
    )

    if memory is not None:

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
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
    # SKILL RESPONSE
    # ---------------------------------------------------------

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
        )

        yield reply

        return

    # ---------------------------------------------------------
    # MODEL STREAM
    # ---------------------------------------------------------

    full_response = ""

    for chunk in stream_aarya(
        get_messages(),
        model_provider=model_provider,
    ):

        if not chunk:
            continue

        full_response += chunk

        yield chunk

    # ---------------------------------------------------------
    # SAVE COMPLETE RESPONSE
    # ---------------------------------------------------------

    if full_response:

        add_message(
            "assistant",
            full_response,
        )
