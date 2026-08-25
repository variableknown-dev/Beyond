import sys

from platforms.linux_platform import LinuxPlatform
from platforms.windows_platform import WindowsPlatform


def detect_platform():
    """
    Detect the current operating system and return
    the appropriate platform implementation.

    Returns:
        Platform: The platform implementation for
        the current operating system.
    """

    system = sys.platform.lower()

    # -----------------------------------------
    # Linux
    # -----------------------------------------

    if system.startswith("linux"):
        return LinuxPlatform()

    # -----------------------------------------
    # Windows
    # -----------------------------------------

    if system.startswith("win"):
        return WindowsPlatform()

    # -----------------------------------------
    # macOS
    # -----------------------------------------

    if system == "darwin":
        raise NotImplementedError(
            "macOS platform support is not implemented yet."
        )

    # -----------------------------------------
    # Unknown Platform
    # -----------------------------------------

    raise RuntimeError(
        f"Unsupported platform: {sys.platform}"
    )
