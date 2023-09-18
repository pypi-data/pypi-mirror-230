from __future__ import annotations

from fastapi import Request
from loguru import logger as log

async def logging_dependency(request: Request) -> None:
    """https://stackoverflow.com/a/63413392."""
    # log.debug(f"{request.method} {request.url}")

    _params = []
    _headers = []

    # log.debug(f"Params:")
    for name, value in request.path_params.items():
        # log.debug(f"\t{name}: {value}")
        _params.append({name: value})

    # log.debug(f"Headers:")
    for name, value in request.headers.items():
        # log.debug(f"\t{name}: {value}")
        _headers.append({name: value})

    req_log: dict = {
        "method": request.method,
        "url": request.url,
        "params": _params,
        "headers": _headers,
    }

    log.debug(req_log)
