from ollama import chat


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

Your job is to classify the user's request into EXACTLY ONE of these intents:

{", ".join(INTENTS)}

Rules:

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

Do not explain.
Do not use punctuation.
Do not use markdown.
"""


def classify_intent(user_input):

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
    )

    intent = response["message"]["content"].strip().lower()

    if intent not in INTENTS:
        return "chat"

    return intent
