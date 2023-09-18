from __future__ import annotations

import pkgutil

## Import modules with only stdlib dependencies directly
from .context_managers import (
    DictProtect,
    ListProtect,
    SQLiteConnManager,
    async_benchmark,
    benchmark,
)
from .dict_utils import debug_dict, merge_dicts, update_dict, validate_dict
from .file_utils import crawl_dir, default_json_dir, export_json, ts, list_files
from .hash_utils import get_hash_from_str
from .time_utils import (
    datetime_as_dt,
    datetime_as_str,
    default_format as default_ts_format,
    get_ts,
    twelve_hour_format as ts_twelve_hour_format,
)
from .uuid_utils import (
    UUIDLength,
    first_n_chars,
    gen_uuid,
    get_rand_uuid,
    glob_uuid_lens,
    trim_uuid,
)

## Use pkgutil to only load modules
#  if dependencies are met
if pkgutil.find_loader("diskcache"):
    from . import diskcache_utils

if pkgutil.find_loader("httpx"):
    from . import httpx_utils

if pkgutil.find_loader("loguru"):
    from . import loguru_utils

if pkgutil.find_loader("msgpack"):
    from . import msgpack_utils

## Only import fastapi utils if fastapi and uvicorn are installed
if pkgutil.find_loader("fastapi"):
    if pkgutil.find_loader("uvicorn"):
        from . import fastapi_utils

if pkgutil.find_loader("sqlalchemy"):
    from . import sqlalchemy_utils

if pkgutil.find_loader("pydantic"):
    from . import pydantic_utils
