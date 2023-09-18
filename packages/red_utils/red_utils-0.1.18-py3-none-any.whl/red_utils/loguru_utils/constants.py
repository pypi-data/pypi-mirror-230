from __future__ import annotations

from dataclasses import dataclass, field
import sys

from typing import Callable, Union

_ts: str = "[{time:YYYY-MM-DD_HH:mm:ss}]"
_level: str = "[{level}]"
_module: str = "[{module}]"
_function: str = "[{function}]"
_name: str = "[{name}]"
_line: str = "[{line}]"
_name_line: str = "[{name}:{line}]"
_module_line: str = "[{module}:{line}]"
_msg: str = "{message}"

default_fmt: str = f"{_ts} {_level} > {_name_line}: {_msg}"
default_color_fmt: str = f"<green>{_ts}</green> <level>{_level}</level> > <level>{_name_line}</level>: {_msg}"
# default_fmt: str = "[{time:YYYY-MM-DD_HH:mm:ss}] [{level}] | [{name}:{line}]: {message}"
# default_color_fmt: str = "<green>[{time:YYYY-MM-DD_HH:mm:ss}]</green> <level>[{level}]</level> | [{name}:{line}]: {message}"
default_log_dir: str = "logs"


@dataclass
class LogLevel:
    name: str = field(default=None)
    level_name: str = field(default=None)
    severity: int = field(default=None)
    method: Callable = field(default=None)


## https://loguru.readthedocs.io/en/stable/api/logger.html#levels
log_levels: list[LogLevel] = [
    LogLevel(
        **{"name": "trace", "name": "TRACE", "severity": 5, "method": "logger.trace"}
    ),
    LogLevel(
        **{"name": "debug", "name": "DEBUG", "severity": 10, "method": "logger.trace"}
    ),
    LogLevel(
        **{"name": "info", "name": "INFO", "severity": 20, "method": "logger.trace"}
    ),
    LogLevel(
        **{
            "name": "success",
            "name": "SUCCESS",
            "severity": 25,
            "method": "logger.trace",
        }
    ),
    LogLevel(
        **{
            "name": "warning",
            "name": "WARNING",
            "severity": 30,
            "method": "logger.trace",
        }
    ),
    LogLevel(
        **{"name": "error", "name": "ERROR", "severity": 40, "method": "logger.trace"}
    ),
    LogLevel(
        **{
            "name": "critical",
            "name": "CRITICAL",
            "severity": 50,
            "method": "logger.trace",
        }
    ),
]


valid_compression_strs: list[str] = [
    "gz",
    "bz2",
    "xz",
    "lzma",
    "tar",
    "tar.gz",
    "tar.bz2",
    "tar.xz",
    "zip",
]

## https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e
# uvicorn_logger_conf: dict[str, str] = {
#     "logger": {
#         "path": "/var/logs",
#         "filename": "access.log",
#         "level": "info",
#         "rotation": "20 days",
#         "retention": "1 months",
#         "format": "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> request id: {extra[request_id]} - <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
#     }
# }

## https://stackoverflow.com/a/66610100
uvicorn_log_conf = {}
# this is default (site-packages\uvicorn\main.py)
uvicorn_log_conf["log_config"] = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": "None",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO", "handlers": ["default"], "propagate": True},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
