from brain.planner import create_plan
from brain.executor import execute_plan
from brain.chat import ask_beyond, stream_beyond
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
    session_id=None,
):

    add_message(
        "user",
        user_input,
        session_id=session_id,
    )

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    memory = extract_memory(
        user_input
    )

    if memory is not None:

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
            session_id=session_id or "local",
        )

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    plan = create_plan(
        user_input,
        history=get_messages(session_id=session_id),
    )

    reply = execute_plan(
        plan,
        platform=platform,
        model_provider=model_provider,
    )

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
            session_id=session_id,
        )

        return reply

    # -----------------------------------------------------
    # NORMAL MODEL CHAT
    # -----------------------------------------------------

    reply = ask_beyond(
        get_messages(session_id=session_id),
        model_provider=model_provider,
    )

    if not reply:
        reply = "Sorry, I didn't receive a response."

    add_message(
        "assistant",
        reply,
        session_id=session_id,
    )

    return reply


# =========================================================
# STREAMING PROCESSING
# =========================================================

def process_stream(
    user_input,
    platform=None,
    model_provider=None,
    session_id=None,
):

    add_message(
        "user",
        user_input,
        session_id=session_id,
    )

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    memory = extract_memory(
        user_input
    )

    if memory is not None:

        remember(
            memory["category"],
            memory["key"],
            memory["value"],
            session_id=session_id or "local",
        )

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    plan = create_plan(
        user_input,
        history=get_messages(session_id=session_id),
    )

    reply = execute_plan(
        plan,
        platform=platform,
        model_provider=model_provider,
    )

    if reply and reply.strip():

        add_message(
            "assistant",
            reply,
            session_id=session_id,
        )

        yield reply

        return

    # -----------------------------------------------------
    # STREAM MODEL RESPONSE
    # -----------------------------------------------------

    response_chunks = []

    try:

        for chunk in stream_beyond(
            get_messages(session_id=session_id),
            model_provider=model_provider,
        ):

            if not chunk:
                continue

            response_chunks.append(chunk)
            yield chunk

    except Exception as error:

        print(
            f"Beyond streaming error: {error}",
            flush=True,
        )

        if "503" in str(error) or "unavailable" in str(error).lower():
            yield (
                "\n\nGemini is temporarily busy. "
                "Please wait a moment and try again."
            )
        else:
            yield (
                "\n\nSorry, I ran into an error "
                "while generating that response."
            )

        return

    # -----------------------------------------------------
    # SAVE RESPONSE
    # -----------------------------------------------------

    if response_chunks:

        add_message(
            "assistant",
            "".join(response_chunks),
            session_id=session_id,
        )
