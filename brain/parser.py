import json

from brain.chat import ask_aarya


SYSTEM_PROMPT = """
You are Aarya's memory extraction engine.

Your job is to decide whether something should be stored as long-term memory.

Only store facts that are likely to remain useful.

Allowed categories:

preference
location
project
person
fact
other

If nothing should be remembered, reply EXACTLY:

NONE

Otherwise reply ONLY valid JSON.

Example:

{
    "category": "preference",
    "key": "browser",
    "value": "Firefox"
}

Rules:

- Reply ONLY JSON.
- No markdown.
- No explanation.
- No extra text.
- Keys should be lowercase_with_underscores.
"""


# =========================================================
# MEMORY DETECTION
# =========================================================

def looks_like_memory(user_input):
    """
    Quickly determine whether a message is likely
    to contain information worth remembering.

    This check is intentionally local so ordinary
    conversations do not require an additional
    Gemini request.
    """

    text = user_input.lower().strip()

    triggers = [
        "remember that",
        "remember this",
        "don't forget",
        "do not forget",
        "my favorite",
        "my favourite",
        "my preferred",
        "i prefer",
        "i like",
        "i love",
        "i live in",
        "my name is",
        "my project is",
    ]

    return any(
        trigger in text
        for trigger in triggers
    )


# =========================================================
# MEMORY EXTRACTION
# =========================================================

def extract_memory(
    user_input,
    model_provider,
):
    """
    Extract long-term memory from a message.

    Gemini is only contacted when the message looks
    like it may actually contain a memory.
    """

    if not looks_like_memory(
        user_input
    ):
        return None

    response = ask_aarya(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        model_provider=model_provider,
    ).strip()

    if response.upper() == "NONE":
        return None

    try:

        memory = json.loads(
            response
        )

        required = {
            "category",
            "key",
            "value",
        }

        if not required.issubset(
            memory.keys()
        ):
            return None

        return memory

    except Exception:

        return None
