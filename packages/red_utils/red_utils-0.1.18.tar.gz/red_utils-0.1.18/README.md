# red-utils

**Important**: This is my first Python package. I'm experimenting with CI/CD and Pypi. This library is most likely not useful to anyone else.

# Description

## [Project Home - Github Repository](https://github.com/redjax/red-utils)


A collection of utility scripts/functions that I use frequently. Includes helper functions/default variables for libraries like `loguru`, `diskcache`, and `msgpack`.

# Installation

## Pip

`pip install red-utils`

## PDM

`pdm add red-utils`

# Modules

## dict_utils

**Description**: Helper functions to assist repetitive `dict`-related operations.

**Examples**:

- `dict_utils.debug_dict()`
  -  loops a dictionary, recursively printing a nested dict's keys, values, and value types.
- `dict_utils.merge_dicts()`
  - Takes 2 `dict` objects and merges them.
- `dict_utils.update_dict()`
  - Takes 2 dict objects, updates the values of the first dict with values from the second.

## diskcache_utils

**Description**: Helper utilities for the [DiskCache](https://grantjenks.com/docs/diskcache/) package. `DiskCache` creates a local cache DB (a SQLite database), where you can write/read key/value pairs. It's sort of like a local redis, and is very useful while developing.

This module simplifies creating a cache by exposing the configuration options I normally use when creating a `diskcache.Cache` instance.

**Examples**: *WIP*

## fastapi_utils

**Description**: Helper utilities for [FastAPI](https://fastapi.tiangolo.com) and [Uvicorn](https://fastapi.tiangolo.com/deployment/manually/). Includes utilities to override `FastAPI`'s HTTP logging, a `healthcheck` endpoint router that can be simply added to existing APIs to create a healthcheck, functions for configuring `fastapi.APIRouter` instances, and more.

**Examples**: *WIP*

## hash_utils

**Description**: Utility wrapper functions for stdlib's `hashlib`.

**Examples**:

- `hash_utils.get_hash_from_str()`
  - Get a simple `md5` hash from an input string
  - ```
    in = "this is an example string"

    ## Value will be an md5 hash of the input string
    hash = hash_utils.get_hash_from_str(input_str=in)
    ```

## httpx_utils

**Description**: *WIP*

**Examples**: *WIP*

## loguru_utils

**Description**: *WIP*

**Examples**: *WIP*

## msgpack_utils

**Description**: *WIP*

**Examples**: *WIP*

## uuid_utils

**Description**: *WIP*

**Examples**: *WIP*

# Development

*WIP*

# context managers

Use context managers as `with` statements. Example:

```
## Time a function
with benchmark("some description"):
  some_func()
```

Protect a list during modifications:

```
with ListProtect([0, 1, "2", False]) as copy:
  copy.append("another value")

## Protect from errors during modification
#  Skips overwriting original list when errors occur
with ListProtect([0, 1, "2", False]) as copy:
  cause_error = 1 / 0
```

## benchmarks

**Description**: Benchmark a function call with `context_managers.benchmark`, and async functions with `context_managers.async_benchmark`. Each benchmark accepts a description (`str` type), and prints execution time formatted as `description: x.xxxs`

**Examples**:

```
from red_utils.context_managers import benchmark
import random

with benchmark("Example: sleep for 2 second") as b:
    val = random.randint(10000, 100000)

    while val >= 0:
      val -= 1
```

## protect

**Description**: *WIP*

**Examples**:

- `ListProtect`: Protects a list by modifying a copy, and only returning the updated list if no errors occur.

``` 
ex_list = [1, 2, 3]

## Protects from a ZeroDivision error
with ListProtect(ex_list) as copy:
    copy.append(1 / 0)

print(f"List: {ex_list}")
```

- `DictProtect`: Protects a dict by modifying a copy, and only returning the updated dict if no errors occur.

```
ex_dict = {"example": "value"}

## Protects from a ZeroDivision error
with DictProtect(ex_dict) as copy:
    copy["example"] = 1 / 0

print(f"Dict: {ex_dict}")
```
