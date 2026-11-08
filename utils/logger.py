from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "beyond.log"


def log(category, message):
    """
    Writes a timestamped log entry.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(
            f"[{timestamp}] [{category}] {message}\n"
        )
