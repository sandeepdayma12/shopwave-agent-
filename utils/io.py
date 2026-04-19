import json
from pathlib import Path
from typing import Any


def load_json(filepath: str | Path) -> Any:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
