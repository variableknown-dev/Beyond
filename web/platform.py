from capabilities.names import (
    CHAT,
    MEMORY,
    WEB,
    VISION,
)

from platforms.base import Platform


class WebPlatform(Platform):
    """
    Platform implementation for Aarya's web version.

    Only web-safe capabilities are exposed here.
    """

    def __init__(self):
        super().__init__()

        self.capabilities = {
            CHAT,
            MEMORY,
            WEB,
            VISION,
        }

    @property
    def name(self):
        return "web"
