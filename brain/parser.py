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


def extract_memory(
    user_input,
    model_provider=None,
):

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

        memory = json.loads(response)

        required = {
            "category",
            "key",
            "value",
        }

        if not required.issubset(memory.keys()):
            return None

        return memory

    except Exception:

        return None
