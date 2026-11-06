from capabilities.names import VISION

from skills.base import Skill
from tools.vision import analyze_image


class VisionSkill(Skill):

    name = "Vision"

    description = "Analyzes and understands images."

    required_capabilities = {
        VISION,
    }

    def can_handle(self, user_input):

        command = user_input.lower().strip()

        vision_commands = [
            "describe image ",
            "analyze image ",
            "analyze screenshot ",
            "describe screenshot ",
            "what is in ",
            "what's in ",
        ]

        return any(
            command.startswith(prefix)
            for prefix in vision_commands
        )

    def execute(self, user_input, model_provider=None):

        command = user_input.strip()

        lower_command = command.lower()

        if lower_command.startswith("describe image "):

            image_path = command[len("describe image "):].strip()

            prompt = "Describe this image in detail."

        elif lower_command.startswith("analyze image "):

            image_path = command[len("analyze image "):].strip()

            prompt = "Analyze this image and explain what you see."

        elif lower_command.startswith("analyze screenshot "):

            image_path = command[len("analyze screenshot "):].strip()

            prompt = (
                "Analyze this screenshot carefully. "
                "Explain what is visible and identify any "
                "errors, warnings, or important information."
            )

        elif lower_command.startswith("describe screenshot "):

            image_path = command[len("describe screenshot "):].strip()

            prompt = "Describe what is visible in this screenshot."

        elif lower_command.startswith("what is in "):

            image_path = command[len("what is in "):].strip()

            prompt = "Describe everything important visible in this image."

        elif lower_command.startswith("what's in "):

            image_path = command[len("what's in "):].strip()

            prompt = "Describe everything important visible in this image."

        else:

            return "I couldn't understand that image request."

        success, message = analyze_image(
            image_path,
            prompt,
        )

        return message
