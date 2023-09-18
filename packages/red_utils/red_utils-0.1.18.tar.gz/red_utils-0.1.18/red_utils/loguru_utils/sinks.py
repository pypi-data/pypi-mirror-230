from __future__ import annotations

import sys

from .constants import default_color_fmt, default_fmt, default_log_dir

## stderr, no color
default_stderr_sink: dict = {
    "sink": sys.stderr,
    "colorize": False,
    "format": default_fmt,
    "level": "DEBUG",
}

## stderr, colorized
default_stderr_color_sink: dict = {
    "sink": sys.stderr,
    "colorize": True,
    "format": default_color_fmt,
    "level": "DEBUG",
}

## stdout, no color
default_stdout_sink: dict = {
    "sink": sys.stdout,
    "colorize": False,
    "format": default_fmt,
    "level": "DEBUG",
}

## stdout, colorized
default_stdout_color_sink: dict = {
    "sink": sys.stdout,
    "colorize": True,
    "format": default_color_fmt,
    "level": "DEBUG",
}

## logs/app.log file
default_app_log_file_sink: dict = {
    "sink": f"{default_log_dir}/app.log",
    "colorize": True,
    "retention": 3,
    "rotation": "5 MB",
    "format": default_fmt,
    "level": "DEBUG",
    "enqueue": True,
}

## logs/error.log file
default_error_log_file_sink: dict = {
    "sink": f"{default_log_dir}/error.log",
    "colorize": True,
    "retention": 3,
    "rotation": "5 MB",
    "format": default_fmt,
    "level": "ERROR",
    "enqueue": True,
}

## logs/trace.log file
default_trace_log_file_sink: dict = {
    "sink": f"{default_log_dir}/trace.log",
    "colorize": True,
    "retention": 3,
    "rotation": "5MB",
    "format": default_fmt,
    "level": "TRACE",
    "filter": "TRACE",
    "backtrace": True,
    "diagnose": True,
    "enqueue": True,
}


default_sinks: list[dict] = [
    default_stderr_color_sink,
    default_app_log_file_sink,
    default_error_log_file_sink,
    default_trace_log_file_sink,
]
