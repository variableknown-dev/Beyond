import shlex
import subprocess


SAFE_COMMANDS = {

    # File & Directory
    "pwd",
    "ls",
    "cd",
    "mkdir",
    "touch",
    "cat",
    "cp",
    "mv",

    # System Information
    "whoami",
    "date",
    "uptime",
    "hostname",
    "uname",
    "df",
    "free",
    "lscpu",
    "lsblk",
    "lspci",

    # Development
    "git",
    "python",
    "python3",
    "pip",
    "pip3",

    # AI
    "ollama",

    # Networking
    "ping",
    "curl",
    "wget",
}


def run_command(command):
    """
    Runs a safe terminal command and returns its output.
    """

    command = command.strip()

    if not command:
        return False, "No command provided."

    try:
        command_args = shlex.split(command)
    except ValueError:
        return False, "The command contains invalid quoting."

    if not command_args:
        return False, "No command provided."

    first_word = command_args[0]

    if first_word not in SAFE_COMMANDS:
        return False, (
            f"'{first_word}' isn't allowed yet.\n"
            "Kashvi currently blocks commands that haven't been approved."
        )

    try:
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = ""

        if result.stdout:
            output += result.stdout

        if result.stderr:
            if output:
                output += "\n"
            output += result.stderr

        output = output.strip()

        if not output:
            output = "Command completed successfully."

        if result.returncode == 0:
            return True, output
        else:
            return False, output

    except subprocess.TimeoutExpired:
        return False, "The command timed out after 60 seconds."

    except Exception as e:
        return False, str(e)
