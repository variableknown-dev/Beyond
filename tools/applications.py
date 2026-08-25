import subprocess


APPLICATIONS = {
    "firefox": "firefox",
    "vscode": "code",
    "code": "code",
    "terminal": "gnome-terminal",
    "files": "nautilus",
}


def open_application(name):

    app = APPLICATIONS.get(name.lower())

    if app is None:
        return False, f"I don't know how to open '{name}'."

    try:

        subprocess.Popen([app])

        return True, f"Opening {name}..."

    except Exception as e:

        return False, str(e)
