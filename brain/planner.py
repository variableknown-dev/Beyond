from brain.task import Task


def create_plan(user_input):
    """
    Very simple planner.

    Splits multiple requests into tasks.
    """

    separators = [
        " and ",
        " then ",
        ","
    ]

    text = user_input

    for sep in separators:

        text = text.replace(sep, "|")

    tasks = []

    for part in text.split("|"):

        part = part.strip()

        if part:

            tasks.append(Task(part))

    return tasks
