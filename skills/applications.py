from capabilities.names import APPLICATIONS

from skills.base import Skill
from tools.applications import open_application


KNOWN_APPS = {
    "code",
    "vscode",
    "visual studio code",
    "blender",
    "steam",
    "discord",
    "spotify",
    "unity",
    "unity hub",
    "libreoffice",
    "obs",
    "gimp",
}


class ApplicationSkill(Skill):

    name = "Applications"

    description = "Launch desktop applications."

    required_capabilities = {
        APPLICATIONS,
    }

    def can_handle(self, user_input):

        command = user_input.lower().strip()

        if not command.startswith("open "):
            return False

        app = command[5:].strip()

        return app in KNOWN_APPS

    def execute(self, user_input, model_provider=None):

        app = user_input[5:].strip()

        success, message = open_application(app)

        return message
