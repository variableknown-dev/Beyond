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
    Main processing pipeline for Aarya.
    """

    add_message(
        "user",
        user_input,
    )

    # -----------------------------------------------------
    # LONG-TERM MEMORY
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    plan = create_plan(
        user_input
    )

    reply = execute_plan(
        plan,
        platform=platform,
    )

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
        )

        return reply

    # -----------------------------------------------------
    # MODEL RESPONSE
    # -----------------------------------------------------

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
    Streaming processing pipeline for Aarya.
    """

    add_message(
        "user",
        user_input,
    )

    # -----------------------------------------------------
    # LONG-TERM MEMORY
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    plan = create_plan(
        user_input
    )

    reply = execute_plan(
        plan,
        platform=platform,
    )

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
        )

        yield reply

        return

    # -----------------------------------------------------
    # MODEL STREAM
    # -----------------------------------------------------

    full_response = ""

    try:

        for chunk in stream_aarya(
            get_messages(),
            model_provider=model_provider,
        ):

            if chunk:

                full_response += chunk

                yield chunk

    except Exception as error:

        print(
            f"Aarya model error: {error}",
            flush=True,
        )

        yield (
            "\n\nSorry, I ran into "
            "an error while generating "
            "that response."
        )

        return

    # -----------------------------------------------------
    # SAVE COMPLETE RESPONSE
    # -----------------------------------------------------

    if full_response:

        add_message(
            "assistant",
            full_response,
        )
