from brain.router import route
from brain.chat import ask_beyond


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
            Current Beyond platform.

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

            # When a compound request contains a part with no dedicated skill,
            # answer that part separately instead of silently dropping it.
            if len(tasks) > 1:
                reply = ask_beyond(
                    [{
                        "role": "user",
                        "content": (
                            "Answer only this part of the user's multi-part request. "
                            "Do not repeat or answer the other parts:\n"
                            f"{task.text}"
                        ),
                    }],
                    model_provider=model_provider,
                )

            if not reply:
                task.success = False
                task.completed = True
                task.result = ""
                continue

            task.success = True
            task.completed = True
            task.result = reply
            replies.append(reply)
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
