from __future__ import annotations

from typing import Any

from .validators import validate_dict

def debug_dict(in_dict: dict = None) -> None:
    """Debug print a dict by looping overkeys and printing.

    If type of key is also dict, re-run the loop on that key and continue.
    """
    validate_dict(in_dict)

    try:
        for k in in_dict.keys():
            if not isinstance(in_dict[k], dict):
                print(f"Key [{k}]:\n\tType: {type(in_dict[k])}\n\tValue: {in_dict[k]}")
            else:
                print(f"Key [{k}] is type dict. Looping over sub-dict")
                debug_dict(in_dict=in_dict[k])

                continue

    except Exception as exc:
        raise Exception(
            f"Unhandled exception looping dict. Errored on key {k}. Details: {exc}"
        )


def merge_dicts(
    original_dict: dict[str, Any] = None,
    update_vals: dict[str, Any] = None,
) -> dict[str, str]:
    """Merge dicts into new dict."""
    validate_dict(original_dict)
    validate_dict(update_vals)

    try:
        _new: dict = {**update_vals, **original_dict}

    except Exception as exc:
        raise Exception(f"Unhandled exception merging dicts. Details: {exc}")

    return _new


def update_dict(
    original_dict: dict[str, Any] = None,
    update_vals: dict[str, Any] = None,
) -> dict[str, str]:
    """Update a dict with values from a second dict.

    Args:
    ----
        original_dict: The original dictionary to be updated.
        update_vals: The dict with values with which to update the original dict.
    """
    validate_dict(original_dict)
    validate_dict(update_vals)

    try:
        ## Create a copy of original_dict to update
        new_dict: dict[str, str] = original_dict.copy()
        ## Update new_dict with update_vals dict
        new_dict.update(update_vals)

        return new_dict

    except Exception as exc:
        raise Exception(f"Unhandled exception updating dict. Details: {exc}")
