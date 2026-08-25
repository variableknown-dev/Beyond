from skills.base import Skill
from tools.web import search_web
from brain.chat import ask_aarya


class WebSkill(Skill):

    name = "Web"

    description = "Searches the web and summarizes results."

    required_capabilities = set()

    TRIGGERS = (
        "search ",
        "search for ",
        "search the web for ",
        "look up ",
        "lookup ",
        "find ",
        "who is ",
        "what is ",
        "what are ",
        "when is ",
        "when was ",
        "where is ",
        "why ",
        "how ",
        "latest ",
        "news ",
        "research ",
    )

    def can_handle(self, user_input):

        command = user_input.lower().strip()

        return command.startswith(self.TRIGGERS)

    def execute(self, user_input):

        success, results = search_web(user_input)

        if not success:
            return f"Web search failed:\n{results}"

        context = "Search Results:\n\n"

        for i, result in enumerate(results, start=1):

            context += (
                f"{i}.\n"
                f"Title: {result['title']}\n"
                f"Summary: {result['body']}\n"
                f"URL: {result['url']}\n\n"
            )

        messages = [
            {
                "role": "user",
                "content": (
                    f"The user asked:\n"
                    f"{user_input}\n\n"
                    f"{context}\n"
                    "Answer using ONLY these search results. "
                    "If the answer isn't present, say you couldn't find it. "
                    "At the end, briefly mention the sources you used."
                ),
            }
        ]

        return ask_aarya(messages)
