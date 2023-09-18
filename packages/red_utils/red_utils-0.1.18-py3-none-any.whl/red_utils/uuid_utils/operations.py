"""Utility functions for generating a UUID.

Can generate a UUID as a uuid.UUID, str, or hex (UUID without '-' characters).

Allows trimming a number of characters from the end of a UUID string,
as well as returning the first n number of characters.

NOTE: A UUID string is 36 characters (32 characters as hex).

"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union
import uuid

from .constants import UUIDLength
from .validators import validate_characters, validate_trim

## Instantiated UUIDLength class
glob_uuid_lens: UUIDLength = UUIDLength()


def gen_uuid(as_hex: bool = False) -> Union[str, uuid.UUID]:
    """Return a UUID.

    Nested function to simply return a UUID object.
    """
    if as_hex:
        hex_uuid = uuid.uuid4().hex

        ## Returns a str
        return hex_uuid

    _uuid: uuid.UUID = uuid.uuid4()

    ## Returns a UUID
    return _uuid


def trim_uuid(trim: int = 0, in_uuid: str = uuid.uuid4(), as_hex: bool = False) -> str:
    """Trim UUID string, removing n characters from end of string (where n is value of trim)."""
    ## Set max character count
    ## Attempt to convert inputs value to integer
    if not isinstance(trim, int):
        trim = int(trim)

    if as_hex:
        _max = glob_uuid_lens.hex - 1
    else:
        _max = glob_uuid_lens.standard - 1

    ## Validate trim/characters
    if trim < 0 or trim > _max:
        raise ValueError(
            f"Invalid trim length: {trim}. Must be greater than 0 and less than {_max} ({_max -1})."
        )

    ## Trim n characters from end of string
    _uuid: str = str(in_uuid)[:-trim]

    return _uuid


def first_n_chars(first_n: int = 36, in_uuid: str = uuid.uuid4(), as_hex: bool = False):
    """Return first n characters of UUID string (where n is first_n)."""
    if not isinstance(first_n, int):
        first_n = int(first_n)

    if as_hex:
        _max = glob_uuid_lens.hex - 1
    else:
        _max = glob_uuid_lens.standard - 1

    if first_n < 0 or first_n > _max:
        raise ValueError(
            f"Invalid number of UUID characters requested: {first_n}. Must be greater than 0 and less than or equal to {_max}."
        )

    ## Return first n characters from beginning of string
    _uuid: str = str(in_uuid)[0:first_n]

    return _uuid


def get_rand_uuid(
    trim: int = 0, characters: int = 0, as_str: bool = True, as_hex: bool = False
) -> Union[str, uuid.UUID]:
    """Return a UUID.

    Pass a trim value to remove n characters from end of string.
    Pass a characters value to return first n characters from beginning of string.
    Pass as_hex to get UUID as a hexadecimal (32 chars).

    Function reacts to inputs, and guards against returning an invalid UUID.
    """
    if isinstance(trim, int) and isinstance(characters, int):
        if trim > 0 and characters > 0:
            raise ValueError(
                "Cannot pass both a trim value and a characters value, please use one or the other."
            )
    elif not isinstance(trim, int) and isinstance(characters, int):
        raise ValueError("Trim value must be an int")
    elif isinstance(trim, int) and not isinstance(characters, int):
        raise ValueError("Characters value must be an int")
    else:
        raise ValueError("Trim and Characters values must be int")

    ## Generate a UUID. Returns a 36 char string, or 32 char if as_hex is set
    _uuid: uuid.UUID = gen_uuid(as_hex=as_hex)

    # if as_hex:
    trim = validate_trim(trim_in=trim, as_hex=as_hex)

    if characters > 0:
        characters = validate_characters(characters_in=characters, as_hex=as_hex)

    if trim:
        _uuid: str = trim_uuid(trim=trim, in_uuid=_uuid, as_hex=as_hex)

    if characters:
        _uuid: str = first_n_chars(first_n=characters, in_uuid=_uuid, as_hex=as_hex)

    ## If as_str was passed, convert UUID to string
    if as_str:
        _uuid: str = str(_uuid)

    return _uuid


if __name__ == "__main__":
    """
    If this script is run directly, run a series of test UUIDs.
    """

    def debug_print_test(test_input: dict[str, Union[str, uuid.UUID]] = None) -> None:
        """Debug print a UUID generator test."""
        if not test_input:
            raise ValueError("Missing input to test.")

        if not isinstance(test_input, dict):
            raise TypeError("Test input must be a dict.")

        if test_input["valid"]:
            _valid: str = "VALID"
        else:
            _valid: str = "INVALID"

        print(f"[{_valid}] {test_input['description']}: {test_input['value']}")

    valid_trim: int = 12
    invalid_trim: int = 37
    valid_chars: int = 12
    invalid_chars: int = 36
    valid_hex_chars: int = 12
    invalid_hex_chars: int = 36
    valid_hex_trim: int = 12
    invalid_hex_trim: int = 36

    ## Simple UUID
    simple_uuid = {
        "valid": True,
        "description": "Simple UUID",
        "value": get_rand_uuid(),
    }

    ## Valid trimmed UUID
    valid_trimmed_uuid = {
        "valid": True,
        "description": f"Valid trimmed ({valid_trim}) UUID",
        "value": get_rand_uuid(trim=valid_trim),
    }

    ## Invalid trimmed UUID
    try:
        invalid_trimmed_uuid = {
            "valid": True,
            "description": f"Valid trimmed UUID (-{invalid_trim})",
            "value": get_rand_uuid(trim=37),
        }
    except Exception as exc:
        # print(f"[ERROR]: {exc}")
        invalid_trimmed_uuid = {
            "valid": False,
            "description": "Invalid trimmed UUID",
            "value": exc,
        }

    ## Valid first 12 characters
    valid_first_n = {
        "valid": True,
        "description": f"Valid first {valid_trim} characters.",
        "value": get_rand_uuid(characters=valid_trim),
    }

    ## Invalid first 12 characters
    try:
        invalid_first_n = {
            "valid": True,
            "description": f"Valid trimmed UUID (-{invalid_chars})",
            "value": get_rand_uuid(characters=invalid_chars),
        }
    except Exception as exc:
        # print(f"[ERROR]: {exc}")
        invalid_first_n = invalid_first_n = {
            "valid": False,
            "description": f"Invalid first {invalid_chars} UUID",
            "value": exc,
        }

    ## Simple hex UUID
    simple_hex_uuid: str = {
        "valid": True,
        "description": "Valid UUID hex.",
        "value": get_rand_uuid(as_hex=True),
    }

    ## Valid hex trim
    valid_trimmed_hex = {
        "valid": True,
        "description": f"Valid trimmed UUID (-{valid_hex_trim}).",
        "value": get_rand_uuid(as_hex=True, trim=valid_hex_trim),
    }

    ## Invalid trimmed hex
    try:
        invalid_trimmed_hex = {
            "valid": True,
            "description": f"Valid trimmed UUID (-{invalid_hex_trim}).",
            "value": get_rand_uuid(as_hex=True, trim=invalid_hex_trim),
        }
    except Exception as exc:
        # print(f"[ERROR]: {exc}")
        invalid_trimmed_hex = {
            "valid": False,
            "description": f"Invalid trimmed UUID hex (-{invalid_hex_trim})",
            "value": exc,
        }

    ## Valid first 12 hex characters
    valid_first_n_hex = {
        "valid": True,
        "description": f"Valid first {valid_hex_trim} characters of UUID hex.",
        "value": get_rand_uuid(characters=valid_hex_trim, as_hex=True),
    }

    ## Invalid first 12 hex characters
    try:
        invalid_first_n_hex = {
            "valid": True,
            "description": f"Valid first {invalid_hex_chars} characters of UUID hex.",
            "value": get_rand_uuid(characters=invalid_hex_chars),
        }
    except Exception as exc:
        # print(f"[ERROR]: {exc}")
        invalid_first_n_hex = {
            "valid": False,
            "description": f"Invalid first {invalid_chars} of UUID hex",
            "value": exc,
        }

    debug_prints: list[dict[str, Union[str, uuid.UUID]]] = [
        simple_uuid,
        valid_trimmed_uuid,
        invalid_trimmed_uuid,
        valid_first_n,
        invalid_first_n,
        simple_hex_uuid,
        valid_trimmed_hex,
        invalid_trimmed_hex,
        valid_first_n_hex,
        invalid_first_n_hex,
    ]

    for _test in debug_prints:
        debug_print_test(test_input=_test)
