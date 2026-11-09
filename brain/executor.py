from brain.router import route
from brain.chat import ask_beyond


def execute_plan(
    tasks,
    platform=None,
    model_provider=None,
    user_location=None,
    original_request=None,
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
            user_location=user_location,
        )

        if reply is None:

            # When a compound request contains a part with no dedicated skill,
            # answer that part separately instead of silently dropping it.
            if len(tasks) > 1:
                reply = ask_beyond(
                    [{
                        "role": "user",
                        "content": (
                            "Answer the general-knowledge part below directly and substantively. "
                            "Do not greet the user or answer the live-data parts. "
                            "Use the full request only as context; answer only the specified part.\n\n"
                            f"Full request: {original_request or task.text}\n"
                            f"Part to answer: {task.text}"
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
