from brain.planner import create_plan
from brain.executor import execute_plan
from brain.chat import ask_aarya, stream_aarya
from brain.context import add_message, get_messages

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
    """

    add_message(
        "user",
        user_input,
    )

    memory = extract_memory(
        user_input
    )

    if memory is not None:

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
        )

    plan = create_plan(
        user_input
    )

    reply = execute_plan(
        plan,
        platform=platform,
    )

    if reply.strip():

        add_message(
            "assistant",
            reply,
        )

        return reply

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

    Skills are still executed normally.

    Model-generated responses are streamed to the caller.
    """

    add_message(
        "user",
        user_input,
    )

    # ---------------------------------------------------------
    # LONG-TERM MEMORY
    # ---------------------------------------------------------

    memory = extract_memory(
        user_input
    )

    if memory is not None:

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
        )

    # ---------------------------------------------------------
    # SKILLS
    # ---------------------------------------------------------

    plan = create_plan(
        user_input
    )

    reply = execute_plan(
        plan,
        platform=platform,
    )

    if reply.strip():

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
