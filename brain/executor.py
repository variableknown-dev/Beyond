from brain.router import route


def execute_plan(
    tasks,
    platform=None,
    model_provider=None,
):
    """
    Execute each task in order.

    Args:
        tasks:
            List of Task objects.

        platform:
            Current Kashvi platform.

        model_provider:
            Provider used to summarize web search results.
    """

    replies = []

    for task in tasks:

        reply = route(
            task.text,
            platform=platform,
            model_provider=model_provider,
        )

        if reply is None:

            task.success = False
            task.completed = True
            task.result = ""

            continue

        task.success = True
        task.completed = True
        task.result = reply

        replies.append(
            reply
        )

    return "\n\n".join(
        replies
    )
