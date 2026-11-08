import re

from brain.task import Task
from brain.skill_loader import load_skills


def _normalize_compound_fragment(fragment):
    """Turn short coordinated feature names into routable questions."""

    fragment = fragment.strip(" \t\r\n,.;")
    if re.match(r"^(?:the\s+)?time\b", fragment, re.IGNORECASE):
        return re.sub(r"^(?:the\s+)?time\b", "what time", fragment, count=1, flags=re.IGNORECASE)
    if re.match(r"^(?:the\s+)?date\b", fragment, re.IGNORECASE):
        return re.sub(r"^(?:the\s+)?date\b", "what is today's date", fragment, count=1, flags=re.IGNORECASE)
    return fragment


def _is_skill_request(text, skills):
    return any(skill.can_handle(text) for skill in skills)


def _split_supported_compounds(text, skills):
    """Split coordinated clauses only when each side has a matching skill."""

    fragments = re.split(r"\s+and\s+|,\s*", text, flags=re.IGNORECASE)
    if len(fragments) == 1:
        return [text.strip()]

    result = []
    for fragment in fragments:
        fragment = _normalize_compound_fragment(fragment)
        if not result:
            result.append(fragment)
            continue

        previous = result[-1]
        if _is_skill_request(previous, skills) and _is_skill_request(fragment, skills):
            result.append(fragment)
        else:
            result[-1] = f"{previous} and {fragment}"
    return result


def _share_location_context(parts):
    """Carry a single shared place onto earlier weather/time/date requests."""

    locations = set()
    for part in parts:
        match = re.search(r"\b(?:in|at|near)\s+(.+?)\s*[?.!,;]*$", part, re.IGNORECASE)
        if not match:
            continue
        location = re.sub(
            r"\b(?:right now|today|tomorrow|currently)\b",
            "", match.group(1), flags=re.IGNORECASE,
        ).strip(" ,")
        if location:
            locations.add(location)

    if len(locations) != 1:
        return parts

    location = next(iter(locations))
    shared_place_topics = re.compile(r"\b(?:weather|forecast|time|date|temperature)\b", re.IGNORECASE)
    updated = []
    for part in parts:
        has_place = re.search(r"\b(?:in|at|near)\s+", part, re.IGNORECASE)
        if shared_place_topics.search(part) and not has_place:
            part = f"{part} in {location}"
        updated.append(part)
    return updated


def create_plan(user_input):
    """
    Very simple planner.

    Splits multiple requests into tasks.
    """

    text = re.sub(
        r"^\s*(?:hi|hey|ok|okay)[, ]+",
        "",
        user_input,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s+then\s+", "|", text, flags=re.IGNORECASE)
    text = re.sub(r";\s*", "|", text)

    # Only treat "and" or a comma as a task boundary when the next phrase
    # clearly starts a new action. This preserves natural-language lists and
    # relationships such as "current affairs between the USA and Iran".
    action_start = (
        r"(?:please\s+)?(?:open|launch|start|search|look\s+up|lookup|find|"
        r"create|delete|read|list|move|copy|rename|calculate|compute|"
        r"explain|summarize|check|get|show|tell|give|make|also|play|write|send|download|"
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
            compound_parts = _split_supported_compounds(part, load_skills())
            compound_parts = _share_location_context(compound_parts)
            tasks.extend(Task(compound_part) for compound_part in compound_parts if compound_part)

    return tasks
