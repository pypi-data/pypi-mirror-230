from __future__ import annotations

def validate_dict(_dict: dict[str, str] = None) -> dict[str, str]:
    if not _dict:
        raise ValueError("Missing dict to evaluate")

    if not isinstance(_dict, dict):
        raise TypeError(
            f"Invalid type for input _dict: ({type(_dict)}). Must be dict[str, str]"
        )

    return _dict
