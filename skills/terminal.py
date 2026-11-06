from capabilities.names import TERMINAL

from skills.base import Skill
from tools.terminal import run_command


class TerminalSkill(Skill):

    name = "Terminal"

    description = "Runs safe terminal commands."

    required_capabilities = {
        TERMINAL,
    }

    def can_handle(self, user_input):

        command = user_input.lower().strip()

        return command.startswith("run ")

    def execute(self, user_input, model_provider=None):

        command = user_input[4:].strip()

        success, message = run_command(command)

        return message
