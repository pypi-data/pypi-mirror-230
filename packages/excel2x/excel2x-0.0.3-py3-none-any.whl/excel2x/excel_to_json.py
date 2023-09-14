#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""Convert Excel to json

"""
import json
from pathlib import Path
from typing import List
from .utils import write_file
from .model import ExcelConfig
from .model import DataConfig
from .model import BookData
from .model import DataStyle
from .excel_reader import read_excel_book


def convert_file(input_file, output_file, sheet_index=0, config: ExcelConfig = None):
    if not str(output_file).endswith(".json"):
        raise ValueError(f"output_file must end with .json, but: {output_file}")
    book_data = read_excel_book(input_file, sheet_index, config)
    data_text = json.dumps(book_data, ensure_ascii=False, indent=4, separators=(", ", ": "))
    write_file(data_text, output_file)


def convert_text(input_file, sheet_index=0, config: ExcelConfig = None) -> str:
    book_data = read_excel_book(input_file, sheet_index, config)
    data_text = json.dumps(book_data, ensure_ascii=False, indent=None)
    return data_text


def book_to_json(book_data: BookData, temp_dir: str, output_config: DataConfig = None) -> List[str]:
    output_config = output_config or DataConfig()
    file_list = []
    if output_config.style == DataStyle.COLUMN.value:
        data_columns = book_data.data_columns()
        for key in data_columns:
            # data = {"data": data_columns[key]}
            data = data_columns[key]
            data_name = f"{book_data.name}_{key}"
            output_file = Path(temp_dir).joinpath(data_name).with_suffix(output_config.suffix)
            _convert_data_to_file(output_file, data, output_config)
            file_list.append(output_file)
    else:
        if output_config.style == DataStyle.MAP.value:
            data = book_data.data_map()
        else:
            data = {"data": book_data.data_list()}
        data_name = book_data.name
        output_file = Path(temp_dir).joinpath(data_name).with_suffix(output_config.suffix)
        _convert_data_to_file(output_file, data, output_config)
        file_list.append(output_file)
    return file_list


def _convert_data_to_file(output_file, data, output_config: DataConfig):
    output_file = Path(output_file)
    data_text = json.dumps(data, ensure_ascii=False, indent=output_config.format_indent, separators=output_config.format_separators)
    write_file(data_text, output_file)
