import json
from pathlib import Path


CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_json(filename):
    """
    Loads a JSON configuration file.
    """

    path = CONFIG_DIR / filename

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
