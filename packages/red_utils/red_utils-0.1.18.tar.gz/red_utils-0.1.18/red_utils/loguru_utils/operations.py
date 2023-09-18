from __future__ import annotations

import datetime
import io

from logging import Handler
from pathlib import Path
import sys
from typing import Callable, Coroutine, Union

from .constants import default_color_fmt, default_fmt
from .sinks import (
    default_app_log_file_sink,
    default_error_log_file_sink,
    default_stderr_color_sink,
    default_stderr_sink,
    default_stdout_color_sink,
    default_stdout_sink,
    default_trace_log_file_sink,
)
from .validators import validate_compression_str, validate_level, validate_logger

from loguru import logger

def add_sink(
    _logger: logger = None,
    sink: Union[str, Path, io.TextIOWrapper, Handler, Callable, Coroutine] = None,
    level: Union[int, str] | None = "INFO",
    format: Union[str, Callable] = default_fmt,
    color_format: Union[str, Callable] = default_color_fmt,
    filter: Union[str, Callable, dict] = None,
    colorize: bool | None = False,
    serialize: bool | None = False,
    backtrace: bool | None = False,
    diagnose: bool | None = False,
    enqueue: bool | None = False,
    catch: bool | None = False,
    rotation: Union[int, datetime.time, datetime.timedelta, str, Callable] = None,
    retention: Union[int, datetime.timedelta, str, Callable] = None,
    compression: Union[str, Callable] = None,
) -> logger:
    """Add a sink to a Loguru logger.

    Description:
        Helper function for adding a sink to a Loguru logger.
        Can be called without arguments to use a default instance.

    Loguru Documentation Page Links:
        - sinks: https://loguru.readthedocs.io/en/stable/api/logger.html#sink
        - file sink config: https://loguru.readthedocs.io/en/stable/api/logger.html#file
    """
    ## Validate inputs
    validate_logger(_logger)
    validate_compression_str(compression, none_ok=True)
    validate_level(level=level)

    if not sink:
        sink: io.TextIOWrapper = sys.stderr

    match colorize:
        case True:
            fmt = color_format
        case False:
            fmt = format

    _logger.add(
        sink=sink,
        level=level,
        format=fmt,
        filter=filter,
        colorize=colorize,
        serialize=serialize,
        backtrace=backtrace,
        diagnose=diagnose,
        enqueue=enqueue,
        catch=catch,
    )

    return _logger


def init_logger(
    sinks: list[dict] = [
        default_stderr_color_sink,
        default_app_log_file_sink,
        default_error_log_file_sink,
        default_trace_log_file_sink,
    ]
):
    logger.remove()

    for sink in sinks:
        logger.add(**sink)
