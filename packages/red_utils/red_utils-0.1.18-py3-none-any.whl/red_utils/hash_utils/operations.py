from __future__ import annotations

import hashlib

def get_hash_from_str(input_str: str = None, encoding: str = "utf-8") -> str:
    if not input_str:
        raise ValueError("Missing input string")

    if not encoding:
        raise ValueError("Missing encoding")

    if not isinstance(input_str, str):
        try:
            input_str: str = str(input_str)

        except Exception as exc:
            raise Exception(
                f"Unhandled exception converting input string ({type(input_str)}) to str()"
            )

    try:
        hash = hashlib.md5(input_str.encode(encoding)).hexdigest()

    except Exception as exc:
        raise Exception(
            f"Unhandled exception converting string to hash. Details: {exc}"
        )

    return hash


if __name__ == "__main__":
    print(f"Hashlib demo start")

    _str: str = "This is a test string to be hashed. It has alphanumeric characters like 'a' and 3, and special characters!"

    hashed = get_hash_from_str(input_str=_str)
    print(f"Hashed ({type(hashed)}): {hashed}")
