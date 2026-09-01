import re

from brain.memory import remember


# =========================================================
# MEMORY EXTRACTION
# =========================================================

def extract_memory(user_input):
    """
    Extract obvious long-term memories without calling
    an AI model.

    Returns:
        dict | None
    """

    if not user_input:
        return None

    text = user_input.strip()

    if not text:
        return None

    lower = text.lower()

    # -----------------------------------------------------
    # Explicit "remember" requests
    # -----------------------------------------------------

    if lower.startswith("remember that "):
        content = text[13:].strip()

    elif lower.startswith("remember "):
        content = text[9:].strip()

    else:
        return None

    if not content:
        return None

    # -----------------------------------------------------
    # "my favorite X is Y"
    # -----------------------------------------------------

    match = re.match(
        r"my\s+favorite\s+(.+?)\s+is\s+(.+)",
        content,
        re.IGNORECASE,
    )

    if match:

        key = match.group(1).strip()
        value = match.group(2).strip()

        key = key.lower().replace(" ", "_")

        return {
            "category": "preference",
            "key": key,
            "value": value,
        }

    # -----------------------------------------------------
    # "I prefer X"
    # -----------------------------------------------------

    match = re.match(
        r"i\s+prefer\s+(.+)",
        content,
        re.IGNORECASE,
    )

    if match:

        value = match.group(1).strip()

        return {
            "category": "preference",
            "key": "preference",
            "value": value,
        }

    # -----------------------------------------------------
    # "I like X"
    # -----------------------------------------------------

    match = re.match(
        r"i\s+like\s+(.+)",
        content,
        re.IGNORECASE,
    )

    if match:

        value = match.group(1).strip()

        return {
            "category": "preference",
            "key": "likes",
            "value": value,
        }

    # -----------------------------------------------------
    # "my X is Y"
    # -----------------------------------------------------

    match = re.match(
        r"my\s+(.+?)\s+is\s+(.+)",
        content,
        re.IGNORECASE,
    )

    if match:

        key = match.group(1).strip()
        value = match.group(2).strip()

        key = key.lower().replace(" ", "_")

        return {
            "category": "fact",
            "key": key,
            "value": value,
        }

    # -----------------------------------------------------
    # "I am X"
    # -----------------------------------------------------

    match = re.match(
        r"i\s+am\s+(.+)",
        content,
        re.IGNORECASE,
    )

    if match:

        value = match.group(1).strip()

        return {
            "category": "fact",
            "key": "user_description",
            "value": value,
        }

    # -----------------------------------------------------
    # Nothing recognized
    # -----------------------------------------------------

    return None
