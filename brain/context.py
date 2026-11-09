from collections import OrderedDict, deque
from threading import RLock


# The local CLI keeps one default conversation. Web conversations are keyed by
# their server-issued session cookie and never use this shared default.
conversation = deque(maxlen=20)
_conversations = OrderedDict()
_conversation_lock = RLock()
_MAX_WEB_CONVERSATIONS = 2048


def _get_conversation(session_id=None):
    if session_id is None:
        return conversation

    key = str(session_id)
    with _conversation_lock:
        messages = _conversations.get(key)
        if messages is None:
            messages = deque(maxlen=20)
            _conversations[key] = messages

        _conversations.move_to_end(key)
        while len(_conversations) > _MAX_WEB_CONVERSATIONS:
            _conversations.popitem(last=False)

        return messages


def add_message(role, content, session_id=None):
    """Add a message to the selected conversation."""

    messages = _get_conversation(session_id)
    with _conversation_lock:
        messages.append({"role": role, "content": content})


def get_messages(session_id=None):
    """Return a snapshot of the selected conversation."""

    messages = _get_conversation(session_id)
    with _conversation_lock:
        return list(messages)


def clear(session_id=None):
    """Clear one conversation, or the local CLI conversation by default."""

    if session_id is None:
        with _conversation_lock:
            conversation.clear()
        return

    with _conversation_lock:
        _conversations.pop(str(session_id), None)
