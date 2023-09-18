"""Extras for diskcache_utils.

Separates some functions/classes from the main diskcache_utils to shorten
length of individual scripts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Type, Union

from . import (
    default_cache_dir,
    default_timeout_dict,
    valid_key_types,
    valid_tag_types,
    valid_val_types,
)
from .validators import (
    validate_cache,
    validate_expire,
    validate_key,
    validate_read,
    validate_retry,
    validate_tag,
    validate_tags,
    validate_val,
)

import diskcache

from diskcache import Cache

def convert_to_seconds(unit: str = None, amount: int = None) -> int:
    ## Allowed strings for conversion
    valid_time_units: list[int] = ["seconds", "hours", "minutes", "days", "weeks"]

    if not unit:
        raise ValueError(f"Missing unit. Must be one of {valid_time_units}")

    if not isinstance(unit, str):
        raise TypeError(f"Invalid type for unit: {type(unit)}. Must be str")

    if unit not in valid_time_units:
        raise TypeError(f"Invalid unit: {unit}. Must be one of {valid_time_units}")

    if not amount:
        raise ValueError("Missing amount of unit, i.e. 3 days")

    if not isinstance(amount, int):
        raise TypeError(
            f"Invalid type for amount: ({type(amount)}). Must be of type int"
        )

    match unit:
        case "weeks":
            _amount: int = amount * 7 * 24 * 60 * 60
        case "days":
            _amount: int = amount * 24 * 60 * 60
        case "hours":
            _amount: int = amount * 60 * 60
        case "minutes":
            _amount: int = amount * 60
        case "seconds":
            _amount: int = amount
        case _:
            raise ValueError(f"Invalid input for unit: {unit}")

    return _amount


def new_cache(
    cache_dir: str = default_cache_dir,
    cache_conf: dict = None,
    index: bool = True,
) -> diskcache.core.Cache:
    """Prepare and return a diskcache.Cache object."""
    if not cache_dir:
        raise ValueError("Missing cache directory")

    if not isinstance(cache_dir, Union[str, Path]):
        raise TypeError(f"cache_dir must be of type str or Path, not {type(cache_dir)}")

    if not cache_conf:
        raise ValueError(f"Missing cache")

    if not isinstance(cache_conf, dict):
        raise TypeError(
            f"Invalid type for [cache_conf]: ({type(cache_conf)}). Must be of type dict."
        )

    try:
        # _cache: diskcache.core.Cache = Cache(directory=cache_dir)
        _cache: diskcache.core.Cache = Cache(**cache_conf)

        if index:
            manage_cache_tag_index(cache=_cache)

        return _cache

    except Exception as exc:
        raise Exception(f"Unhandled exception creating cache. Details: {exc}")


def clear_cache(cache: Cache = None) -> bool:
    validate_cache(cache)

    try:
        with cache as ref:
            ref.clear()

            return True

    except Exception as exc:
        raise Exception(
            f"Unhandled exception clearing cache at {cache.directory}. Details: {exc}"
        )


def check_cache_key_exists(key: str = None, cache: diskcache.core.Cache = None) -> bool:
    """Check if a key exists in a cache."""
    ## Key validation
    validate_key(key=key)
    validate_cache(cache=cache)

    ## Check if key exists in cache
    if key in cache:
        return True
    else:
        return False


def manage_cache_tag_index(operation: str = "create", cache: Cache = None) -> None:
    valid_operations: list[str] = ["create", "delete"]

    validate_cache(cache=cache)

    if not operation:
        raise Exception(f"Operation cannot be None.")

    try:
        match operation:
            case "create":
                if cache.tag_index == 0:
                    cache.create_tag_index()
                else:
                    pass

            case "delete":
                if cache.tag_index == 1:
                    cache.drop_tag_index()
                else:
                    pass

            case _:
                raise ValueError(
                    f"Invalid operation: {operation}. Must be one of {valid_operations}"
                )

    except Exception as exc:
        raise Exception(f"Unhandled exception configuring tag_index. Details: {exc}")


def set_val(
    key: valid_key_types = None,
    val: valid_val_types = None,
    expire: int = None,
    read: bool = False,
    tag: str = None,
    retry: bool = False,
    cache: Cache = None,
) -> None:
    """Set a key value pair in the cache.

    Handles optional properties like expiration, tag, retry, etc.
    """
    validate_key(key)
    validate_val(val)
    validate_expire(expire, none_ok=True)
    validate_read(read, none_ok=True)
    validate_tag(tag=tag, none_ok=True)
    validate_retry(retry=retry, none_ok=True)
    validate_cache(cache=cache)

    try:
        with cache as ref:
            ref.set(key=key, value=val, expire=expire, read=read, tag=tag, retry=retry)

    except Exception as exc:
        raise Exception(
            f"Unhandled exception setting key/value pair for key: [{key}]. Details: {exc}"
        )


def set_expire(
    key: str = None, cache: Cache = None, expire: int = None
) -> Union[dict[str, str], None]:
    validate_key(key)
    validate_cache(cache)
    validate_expire(expire)

    if not check_cache_key_exists(key=key, cache=cache):
        return {
            "warning": f"Cache item with key [{key}] does not exist in cache at {cache.directory}/"
        }

    try:
        with cache as ref:
            ref.touch(key, expire=expire)

    except Exception as exc:
        raise Exception(
            f"Unhandled exception setting expiration of {expire} on key [{key}] in cache at {cache.directory}/. Details: {exc}"
        )


def get_val(key: str = None, cache: Cache = None, tags: list[str] = None):
    """Search for a key in a given cache.

    Pass a diskcache.Cache object for cache, and a key (and optionally a list of tags).
    Function will search the cache and return a value if found, or a structured
    error dict describing the lack of key.
    """
    validate_key(key)
    validate_cache(cache)
    validate_tags(tags)

    try:
        if check_cache_key_exists(key=key, cache=cache):
            try:
                with cache as ref:
                    _val = ref.get(key=key)

                    return _val

            except Exception as exc:
                raise Exception(
                    f"Unhandled exception retrieving value of key [{key}]. Details: {exc}"
                )

        else:
            return {
                "error": "Key not found in cache",
                "details": {"key": key, "cache_dir": cache.directory},
            }

    except Exception as exc:
        return {
            "error": "Error searching for key in cache",
            "details": {"exception": exc},
        }


def delete_val(
    key: valid_key_types = None, cache: Cache = None, tag: str = None
) -> tuple:
    validate_key(key)
    validate_cache(cache)
    validate_tag(tag)

    try:
        with cache as ref:
            _delete = ref.pop(key=key, tag=tag)

            return _delete

    except Exception as exc:
        raise Exception(
            f"Unhandled exception deleting key {key} from cache at {cache.directory}/. Details: {exc}"
        )


def get_cache_size(cache: Cache = None) -> dict[str, int]:
    validate_cache(cache=cache)

    try:
        cache_size: int = cache.volume()

    except Exception as exc:
        raise Exception(f"Unhandled exception getting cache size. Details: {exc}")

    return {"unit": "bytes", "size": cache_size}


def check_cache(cache: Cache = None):
    validate_cache(cache=cache)

    try:
        warnings = cache.check()

        return warnings

    except Exception as exc:
        raise Exception(
            f"Unhandled exception checking cache for warnings. Details: {exc}"
        )
