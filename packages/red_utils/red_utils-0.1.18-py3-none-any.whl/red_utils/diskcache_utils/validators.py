from __future__ import annotations

from pathlib import Path
from typing import Optional, Type, Union

from . import valid_key_types, valid_tag_types, valid_val_types

import diskcache

from diskcache import Cache

def validate_key(key: valid_key_types = None, none_ok: bool = False) -> Union[str, int]:
    """Validate input diskcache key.

    Supported key types:
    - int
    - str
    """
    ## Evaluate key existence
    if not key:
        if none_ok:
            return key

        else:
            raise ValueError("Missing key to evaluate")

    ## Key exists, validate type
    if type(key) not in valid_key_types:
        raise TypeError(
            f"Invalid type for key: ({type(key)}). Must be one of {valid_key_types}"
        )

    return key


def validate_val(
    val: valid_val_types = None, none_ok: bool = False
) -> Union[str, bytes, float, int]:
    """Validate input diskcache value.

    Supported value types:
    - int
    - str

    """
    if not val:
        if none_ok:
            return val
        else:
            raise ValueError("Missing value to evaluate")

    if type(val) not in valid_val_types:
        raise TypeError(
            f"Invalid type for val: ({type(val)}). Must be one of {valid_val_types}"
        )

    return val


def validate_expire(expire: int = None, none_ok: bool = False) -> int:
    """Validate input diskcache expiration time.

    Only int types allowed. Expiration time is in seconds.
    """
    ## Evaluate var existence
    if not expire:
        if none_ok:
            return expire
        else:
            raise ValueError("Missing expire value to evaluate")

    ## Evaluate var type
    if not isinstance(expire, int):
        try:
            expire: int = int(expire)

            return expire

        except Exception as exc:
            raise TypeError(
                f"Expire value is not of type int. Conversion to int failed. Details: {exc}"
            )


def validate_read(read: bool = None, none_ok: bool = True) -> bool:
    """Validate input diskcache read value.

    Read is a bool that enables/disables reading input as a file.
    Docs: https://grantjenks.com/docs/diskcache/tutorial.html#cache

    Only int types allowed. Expiration time is in seconds.

    """
    ## Evaluate var existence
    if not read:
        if none_ok:
            return read
        else:
            raise ValueError("Missing read bool to evaluate")

    ## Evaluate var type
    if not isinstance(read, bool):
        try:
            read: bool = bool(read)

        except Exception as exc:
            raise TypeError(
                f"Read value is not of type bool. Conversion to bool failed. Details: {exc}"
            )


def validate_tags(
    tags: list[valid_tag_types] = None, none_ok: bool = True
) -> list[valid_tag_types]:
    if not tags:
        if none_ok:
            return tags
        else:
            raise ValueError("Missing tags list")

    if not isinstance(tags, list):
        raise TypeError(f"Input must be a list of strings, not {type(tags)}")

    for _tag in tags:
        if type(_tag) not in valid_tag_types:
            raise TypeError(
                f"Invalid type for tag [{_tag}]: {type(_tag)}. Must be one of {valid_tag_types}"
            )

    return tags


def validate_tag(tag: valid_tag_types = None, none_ok: bool = True) -> str:
    """Validate input diskcache tag.

    A tag is an optional user-defined string that groups cache entries.
    """
    ## Evaluate var existence
    if not tag:
        if none_ok:
            return tag
        else:
            raise ValueError("Missing tag to evaluate")

    ## Evaluate var type
    if type(tag) not in valid_tag_types:
        raise TypeError(
            f"Invalid type for tag [{tag}]: {type(tag)}. Must be one of {valid_tag_types}"
        )

    if not isinstance(tag, str):
        try:
            tag: str = str(tag)

        except Exception as exc:
            raise TypeError(
                f"tag value is not of type str. Conversion to str failed. Details: {exc}"
            )

    return tag


def validate_retry(retry: bool = None, none_ok: bool = True) -> bool:
    """Validate input diskcache retry.

    Determines whether or not cache will retry on failure before exiting.
    """
    ## Evaluate var existence
    if not retry:
        if none_ok:
            return retry
        else:
            raise ValueError("Missing retry to evaluate")

    ## Evaluate var type
    if not isinstance(retry, str):
        try:
            retry: str = str(retry)

        except Exception as exc:
            raise TypeError(
                f"Retry value is not of type str. Conversion to str failed. Details: {exc}"
            )


def validate_cache(cache: Cache = None, none_ok: bool = True) -> diskcache.core.Cache:
    """Validate a DiskCache cache object.

    Checks for existence and correct type.
    """
    ## Check existence
    if cache is None:
        if not none_ok:
            raise ValueError("Missing diskcache.Cache object to perform lookup against")

    else:
        ## Only validate an existing cache
        if not isinstance(cache, Cache):
            raise TypeError(f"Cache must be of type diskcache.Cache, not {type(cache)}")

    return cache
