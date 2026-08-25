from abc import ABC

class Platform(ABC):
    """
    Base platform implementation.

    Platforms expose capabilities instead of hardcoded methods.
    """

    def __init__(self):
        self.capabilities = set()

    @property
    def name(self):
        raise NotImplementedError

    def has_capability(self, capability):
        return capability in self.capabilities
