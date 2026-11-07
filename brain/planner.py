import re

from brain.task import Task


def create_plan(user_input):
    """
    Very simple planner.

    Splits multiple requests into tasks.
    """

    text = re.sub(r"\s+then\s+", "|", user_input, flags=re.IGNORECASE)
    text = re.sub(r";\s*", "|", text)

    # Only treat "and" or a comma as a task boundary when the next phrase
    # clearly starts a new action. This preserves natural-language lists and
    # relationships such as "current affairs between the USA and Iran".
    action_start = (
        r"(?:please\s+)?(?:open|launch|start|search|look\s+up|lookup|find|"
        r"create|delete|read|list|move|copy|rename|calculate|compute|"
        r"explain|summarize|check|get|show|tell|play|write|send|download|"
        r"what|who|when|where|why|how)\b"
    )
    text = re.sub(
        rf"\s+and\s+(?={action_start})",
        "|",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        rf",\s*(?={action_start})",
        "|",
        text,
        flags=re.IGNORECASE,
    )

    tasks = []

    for part in text.split("|"):

        part = part.strip()

        if part:

            tasks.append(Task(part))

    return tasks
