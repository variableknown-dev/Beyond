from capabilities.names import BROWSER

from skills.base import Skill
from tools.browser import (
    open_website,
    search_google,
    search_youtube,
)


KNOWN_BROWSERS = {
    "firefox",
    "chrome",
    "brave",
    "edge",
}

KNOWN_SITES = {
    "youtube",
    "google",
    "github",
    "chatgpt",
    "gmail",
    "reddit",
    "stackoverflow",
}


class BrowserSkill(Skill):

    name = "Browser"

    description = "Open browsers, websites and perform searches."

    required_capabilities = {
        BROWSER,
    }

    def can_handle(self, user_input):

        command = user_input.lower().strip()

        if command.startswith("open "):

            target = command[5:].strip()

            return (
                target in KNOWN_BROWSERS
                or target in KNOWN_SITES
            )

        if command.startswith("search google for "):
            return True

        if command.startswith("search youtube for "):
            return True

        return False

    def execute(self, user_input, model_provider=None):

        command = user_input.lower().strip()

        if command.startswith("open "):

            target = command[5:].strip()

            success, message = open_website(target)

            return message

        if command.startswith("search google for "):

            query = user_input[18:].strip()

            success, message = search_google(query)

            return message

        if command.startswith("search youtube for "):

            query = user_input[19:].strip()

            success, message = search_youtube(query)

            return message

        return "I couldn't understand that browser request."
