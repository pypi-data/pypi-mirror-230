#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""utils
"""
import traceback
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


_log_level = LogLevel.INFO


def set_log_level(log_level: int | str):
    if isinstance(log_level, int):
        _log_level = LogLevel(log_level)
    else:
        name_lower = str(log_level).lower()
        for item in LogLevel:
            if str(item.name).lower() == name_lower:
                _log_level = item
                break


def log_debug(*values: object):
    if _log_level.value <= LogLevel.DEBUG.value:
        print(*values, flush=True)


def log_info(*values: object):
    if _log_level.value <= LogLevel.INFO.value:
        print(*values, flush=True)


def log_warning(message):
    if _log_level.value <= LogLevel.WARN.value:
        print("\033[1;33m" + str(message) + "\033[0m", flush=True)


def log_error(message):
    if isinstance(message, Exception):
        trace_stack = "".join(traceback.format_exception(message))
        message = str(message)
        message += "\n"
        message += trace_stack
    print("\033[1;31m" + str(message) + "\033[0m", flush=True)


def print_line(title: str = None, max_length: int = 120):
    if title is None:
        log_info("*" * max_length)
    else:
        log_info((f" {str(title)} ").center(max_length, "*"))


def read_file(input_path, encoding="utf-8"):
    input_path = Path(input_path)
    if input_path.exists():
        return input_path.read_text(encoding=encoding)
    return None


def write_file(output_path, data_text, encoding="utf-8"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(data_text, encoding=encoding))
