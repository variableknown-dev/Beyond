from collections import deque

# Keeps the last 20 messages
conversation = deque(maxlen=20)


def add_message(role, content):
    """
    Adds a message to the conversation history.
    """

    conversation.append({
        "role": role,
        "content": content
    })


def get_messages():
    """
    Returns the conversation history.
    """

    return list(conversation)


def clear():
    """
    Clears the conversation.
    """

    conversation.clear()
