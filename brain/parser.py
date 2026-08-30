import json

from brain.chat import ask_aarya


# =========================================================
# MEMORY EXTRACTION PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are Aarya's memory extraction engine.

Your job is to decide whether something should be stored
as long-term memory.

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
# EXTRACT MEMORY
# =========================================================

def extract_memory(
    user_input,
    model_provider=None,
):
    """
    Ask the model whether the user's message contains
    useful long-term memory.

    Returns:
        dict    -> memory to save
        None    -> nothing to remember or extraction failed
    """

    try:

        # -------------------------------------------------
        # ASK MODEL
        # -------------------------------------------------

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
        )

        # -------------------------------------------------
        # HANDLE EMPTY RESPONSE
        # -------------------------------------------------

        if not response:

            print(
                "Memory extraction returned no response.",
                flush=True,
            )

            return None

        response = response.strip()

        # -------------------------------------------------
        # NOTHING TO REMEMBER
        # -------------------------------------------------

        if response.upper() == "NONE":

            return None

        # -------------------------------------------------
        # PARSE JSON
        # -------------------------------------------------

        try:

            memory = json.loads(
                response
            )

        except json.JSONDecodeError:

            print(
                "Memory extraction returned invalid JSON.",
                flush=True,
            )

            return None

        # -------------------------------------------------
        # MAKE SURE IT IS A DICTIONARY
        # -------------------------------------------------

        if not isinstance(
            memory,
            dict,
        ):

            print(
                "Memory extraction returned non-object JSON.",
                flush=True,
            )

            return None

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        required = {
            "category",
            "key",
            "value",
        }

        if not required.issubset(
            memory.keys()
        ):

            print(
                "Memory extraction JSON is missing required fields.",
                flush=True,
            )

            return None

        # -------------------------------------------------
        # VALIDATE VALUES
        # -------------------------------------------------

        if not memory["category"]:
            return None

        if not memory["key"]:
            return None

        if not memory["value"]:
            return None

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        return {
            "category": str(
                memory["category"]
            ).strip(),

            "key": str(
                memory["key"]
            ).strip(),

            "value": str(
                memory["value"]
            ).strip(),
        }

    # =====================================================
    # NEVER LET MEMORY BREAK AARYA
    # =====================================================

    except Exception as error:

        print(
            f"Memory extraction failed: {error}",
            flush=True,
        )

        return None
