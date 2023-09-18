from __future__ import annotations

from datetime import datetime

default_json_dir: str = "data/json"


def ts():
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    return now
