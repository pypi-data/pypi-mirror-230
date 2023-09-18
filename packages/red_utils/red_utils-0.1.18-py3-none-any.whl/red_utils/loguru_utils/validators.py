"""Loguru validators.

Pass objects, strings, bools, etc for evaluation.

Each validator checks for existence (unless none_ok=True),
then type, then value (if a list of allowed values is passed).
"""
from __future__ import annotations

from . import (
    default_color_fmt,
    default_fmt,
    default_log_dir,
    log_levels,
    valid_compression_strs,
)

from loguru import logger

def validate_logger(_logger: logger = None, none_ok: bool = False) -> logger:
    """Validate a loguru.Logger object."""
    if none_ok:
        return _logger
    elif not _logger:
        raise ValueError("Missing loguru Logger object to validate")

    if not isinstance(_logger, type(logger)):
        raise TypeError(
            f"Invalid type for logger: {type(_logger)}. Must be type(Logger)"
        )

    return _logger


def validate_compression_str(string: str = None, none_ok: bool = True) -> str:
    if none_ok:
        return string
    elif not string:
        raise ValueError("Missing a compression string to validate")

    if not isinstance(string, str):
        raise TypeError(f"Invalid type for string: ({type(string)}). Must be type(str)")

    if string not in valid_compression_strs:
        raise ValueError(
            f"Invalid compression type: [{type(string)}]. Must be one of {valid_compression_strs}"
        )

    return string


def validate_level(level: str = None, none_ok: bool = False) -> str:
    if none_ok:
        return level
    elif not level:
        raise ValueError("Missing a log level string to evaluate.")

    if not isinstance(level, str):
        raise TypeError(f"Invalid level type: [{type(level)}]")

    try:
        for _level in log_levels:
            if not level == _level.name or not level == _level.level_name:
                pass
            else:
                return _level

    except ValueError as exc:
        raise ValueError(f"Unhandled exception validating log level. Details: {exc}")
