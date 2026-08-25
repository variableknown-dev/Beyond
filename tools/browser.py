import shutil
import subprocess
import webbrowser
from urllib.parse import quote_plus


WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
    "gmail": "https://mail.google.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
}

BROWSERS = {
    "firefox": "firefox",
    "chrome": "google-chrome",
    "brave": "brave-browser",
    "edge": "microsoft-edge",
}


def open_website(name):
    """
    Opens either a browser application or a known website.
    """

    target = name.lower().strip()

    # Open browser application
    if target in BROWSERS:

        executable = BROWSERS[target]

        if shutil.which(executable) is None:
            return False, f"{target.title()} is not installed."

        subprocess.Popen([executable])

        return True, f"Opening {target.title()}..."

    # Open known website
    if target in WEBSITES:

        webbrowser.open(WEBSITES[target])

        return True, f"Opening {target.title()}..."

    return False, f"I don't know '{name}'."


def search_google(query):
    """
    Searches Google.
    """

    url = f"https://www.google.com/search?q={quote_plus(query)}"

    webbrowser.open(url)

    return True, f"Searching Google for '{query}'..."


def search_youtube(query):
    """
    Searches YouTube.
    """

    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"

    webbrowser.open(url)

    return True, f"Searching YouTube for '{query}'..."
