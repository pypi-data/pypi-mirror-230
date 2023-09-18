from __future__ import annotations

from typing import Optional, Type, Union

valid_key_types: list[Type] = [str, int, tuple, frozenset]
valid_val_types: list[Type] = [str, bytes, float, int, list, dict]
valid_tag_types: list[Type] = [str, int, float, bytes]

default_cache_dir: str = ".cache"
## Set default timeout to 24 hours
default_timeout_dict: dict[str, Union[str, int]] = {"unit": "minutes", "amount": 15}
