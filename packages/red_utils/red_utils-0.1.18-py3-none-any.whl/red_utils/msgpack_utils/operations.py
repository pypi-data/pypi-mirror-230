from __future__ import annotations

from pathlib import Path
from typing import Union
from uuid import uuid4

from . import default_serialize_dir

import msgpack

def ensure_path(dir: Union[str, Path] = None) -> bool:
    """Ensure a directory path exists.

    Returns a bool
    """
    if not dir:
        raise ValueError("Missing input directory to validate")

    if not isinstance(dir, Path) and not isinstance(dir, str):
        raise TypeError(
            f"Invalid type for property [dir]: ({type(dir)}). Must be of type str or Path"
        )

    if isinstance(dir, str):
        dir = Path(dir)

    if not dir.exists():
        try:
            dir.mkdir(parents=True, exist_ok=True)
        except FileExistsError as f_exc:
            return True
        except PermissionError as perm_exc:
            return False
        except Exception as exc:
            raise Exception(
                {
                    "success": False,
                    "error": f"Unhandled exception creating dir: [{dir}].",
                    "details": exc,
                }
            )

    else:
        return True


def msgpack_serialize(_json: dict = None) -> dict[str, Union[bool, str, bytes, None]]:
    """Serialize a Python dict to a msgpack string.

    Return object will be a dict with 2 keys, 'success' and 'detail.'
    Success is a bool indicator of serialize success.
    Detail contains the 'message' key with the bytestring, as well as other
        optional details to be returned.
    """
    if not _json:
        raise ValueError("Missing Python dict data to serialize")

    try:
        packed = msgpack.packb(_json)

        print(f"Packed message type ({type(packed)})")

        return_obj = {"success": True, "detail": {"message": packed}}

    except Exception as exc:
        return_obj = {"success": False, "detail": {"message": f"{exc}"}}

    return return_obj


def msgpack_serialize_file(
    _json: dict = None, output_dir: str = default_serialize_dir, filename: str = None
) -> dict[str, Union[bool, str, dict[str, Union[str, dict]]]]:
    """Serialize a Python dict to a msgpack file.

    Accepts a dict input, with an optional output_dir and filename. Serialize the
    msgpack data to file at output_dir/filename.

    Return object will be a dict with 2 keys, 'success' and 'detail.'
    Success is a bool indicator of serialize success.
    Detail contains the 'message' key with the bytestring, as well as other
        optional details to be returned.
    """
    if not _json:
        raise ValueError("Missing Python dict data to serialize")

    if not filename:
        # log.debug(f"Missing filename. Generating a random filename.")

        filename = str(uuid4())

    if filename.endswith(".msgpack"):
        filename.replace(".msgpack", "")
    else:
        filename = f"{filename}.msgpack"

    dir_exist = ensure_path(output_dir)

    filename = f"{output_dir}/{filename}"

    if _json:
        try:
            with open(f"{filename}", "wb") as outfile:
                packed = msgpack.packb(_json)
                outfile.write(packed)

            return_obj = {
                "success": True,
                "detail": {"message": f"Data serialized to file {filename}"},
            }

        except Exception as exc:
            return_obj = {"success": False, "detail": {"message": f"{exc}"}}

    return return_obj


def msgpack_deserialize_file(
    filename: str = None,
) -> dict[str, Union[bool, str, dict[str, Union[str, dict]]]]:
    """Load serialized msgpack string from a file and return.

    Return object will be a dict with 2 keys, 'success' and 'detail.'
    Success is a bool indicator of serialize success.
    Detail contains the 'message' key with the bytestring, as well as other
        optional details to be returned.
    """
    if not filename:
        raise ValueError("Must pass a file name/path to deserialize")

    if not Path(filename).exists():
        raise FileNotFoundError(f"Could not find file: {filename}")

    try:
        with open(f"{filename}", "rb") as infile:
            in_bytes = infile.read()
            unpacked = msgpack.unpackb(in_bytes)

        return_obj = {
            "success": True,
            "detail": {
                "message": f"Data deserialized from file {filename}",
                "unpacked": unpacked,
            },
        }

    except Exception as exc:
        # log.error({"exception": "Unhandled exception reading msgpack."}, exc_info=True)

        return_obj = {"success": False, "detail": {"message": f"{exc}"}}

    return return_obj


def msgpack_deserialize(
    packed_str: bytes = None,
) -> dict[str, Union[bool, str, dict[str, Union[str, dict]]]]:
    """Load serialized msgpack string.

    Returns a dict with
    """
    if not packed_str:
        raise ValueError("Must pass a bytestring to deserialize")

    if not isinstance(packed_str, bytes):
        raise TypeError(
            f"Invalid type for [packed_str]: ({type(packed_str)}). Must be of type bytestring"
        )

    try:
        unpacked = msgpack.unpackb(packed_str)

        return_obj = {
            "success": True,
            "detail": {
                "message": unpacked,
            },
        }

    except Exception as exc:
        # log.error({"exception": "Unhandled exception reading msgpack."}, exc_info=True)

        return_obj = {"success": False, "detail": {"message": f"{exc}"}}

    return return_obj
