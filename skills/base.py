from abc import ABC, abstractmethod


class Skill(ABC):
    """
    Base class for every Kashvi skill.
    """

    name = ""

    description = ""

    # Capabilities required by this skill
    required_capabilities = set()

    @abstractmethod
    def can_handle(self, user_input):
        pass

    @abstractmethod
    def execute(self, user_input):
        pass
