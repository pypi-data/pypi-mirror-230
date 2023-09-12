#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""utils
"""
import traceback
from pathlib import Path


def log_info(*args: object):
    print(*args, flush=True)


def log_warning(message):
    print("\033[1;33m" + str(message) + "\033[0m")


def log_error(message):
    if isinstance(message, Exception):
        trace_stack = "".join(traceback.format_exception(message))
        message = str(message)
        message += "\n"
        message += trace_stack
    print("\033[1;31m" + str(message) + "\033[0m")


def print_line(title: str = None, max_length: int = 120):
    if title is None:
        print("*" * max_length, flush=True)
    else:
        print((f" {str(title)} ").center(max_length, "*"), flush=True)


def read_file(input_path, encoding="utf-8"):
    input_path = Path(input_path)
    if input_path.exists():
        return input_path.read_text(encoding=encoding)
    return None


def write_file(data_text, output_path, encoding="utf-8"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes(data_text, encoding=encoding))
