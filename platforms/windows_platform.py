from platforms.base import Platform
from platform_services.filesystem import FileSystem

from capabilities.names import (
    CHAT,
    MEMORY,
    FILESYSTEM,
    TERMINAL,
    APPLICATIONS,
    WEB,
    BROWSER,
    VISION,
)


class WindowsPlatform(Platform):

    def __init__(self):
        super().__init__()

        self.filesystem = FileSystem()

        self.capabilities = {
            CHAT,
            MEMORY,
            FILESYSTEM,
            TERMINAL,
            APPLICATIONS,
            WEB,
            BROWSER,
            VISION,
        }

    @property
    def name(self):
        return "windows"
