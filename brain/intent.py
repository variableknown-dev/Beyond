INTENTS = [
    "chat",
    "web",
    "browser",
    "application",
    "terminal",
    "filesystem",
]


SYSTEM_PROMPT = f"""
You are an intent classifier for an AI desktop assistant.

Classify the user's request into EXACTLY ONE intent.

Available intents:

{", ".join(INTENTS)}

chat
- General conversation
- General knowledge
- Coding questions
- Math
- Science
- Explanations

web
- Current events
- Latest news
- Recent information
- Anything requiring internet access

browser
- Open websites
- Google searches
- YouTube searches

application
- Open desktop applications

terminal
- Execute shell commands

filesystem
- Create
- Delete
- Read
- List
- Move
- Copy
- Rename
files or folders.

Reply with ONLY the intent.

No explanation.
No punctuation.
No markdown.
"""


def classify_intent(
    user_input,
    model_provider,
):
    """
    Classify a request using the active model provider.
    """

    response = model_provider.chat(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ]
    )

    intent = response.strip().lower()

    if intent not in INTENTS:

        return "chat"

    return intent
