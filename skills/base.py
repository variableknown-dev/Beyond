from abc import ABC, abstractmethod


class Skill(ABC):
    """
    Base class for every Beyond skill.
    """

    name = ""

    description = ""

    # Capabilities required by this skill
    required_capabilities = set()
    supports_location = False

    @abstractmethod
    def can_handle(self, user_input):
        pass

    @abstractmethod
    def execute(self, user_input, model_provider=None):
        pass
