#!/usr/bin/env python3
# -*- coding: utf-8 -*

from typing import List
from pathlib import Path

from .utils import write_file
from .model import DataStyle
from .model import ExcelConfig
from .model import BookData
from .model import DataConfig

from .excel_reader import read_excel_book


def convert_file(input_file, output_file, sheet_index=0, excel_config: ExcelConfig = None, lua_config: DataConfig = None) -> List[str]:
    """Convert Excel to lua file
    Args:
        input_file (string): 输入 Excel 文件路径
        output_file (string): 输出 lua 文件路径
        sheet_index (int, optional): excel sheet index. Defaults to 0.
        config (ExcelConfig, optional): Excel config. Defaults to None.

    Raises:
        ValueError: 输出文件路径必须是 .lua 或 .lua.txt 文件
    """
    if not (str(output_file).endswith(".lua") or str(output_file).endswith(".lua.txt")):
        raise ValueError(f"output_file must end with .lua, but: {output_file}")
    lua_config = lua_config or DataConfig()
    book_data = read_excel_book(input_file, sheet_index, excel_config)
    schema_text = _get_schema_text(book_data)
    data = book_data.data_list()
    data_text = object_to_lua_text(
        data,
        book_data.keys,
        0,
        lua_config.format_depth,
        lua_config.format_indent,
        lua_config.format_separators,
    )
    data_text = f"local {book_data.name} = {data_text}\nreturn {book_data.name}\n"
    output_text = schema_text + "\n\n" + data_text
    write_file(output_text, output_file)
    return [output_file]


def convert_text(input_file, sheet_index=0, excel_config: ExcelConfig = None, lua_config: DataConfig = None) -> str:
    lua_config = lua_config or DataConfig()
    book_data = read_excel_book(input_file, sheet_index, excel_config)
    data_text = object_to_lua_text(
        book_data,
        book_data.keys,
        0,
        lua_config.format_depth,
        lua_config.format_indent,
        lua_config.format_separators,
    )
    data_text = f"local {book_data.name} = {data_text}\nreturn {book_data.name}\n"
    return data_text


def book_to_lua_file(book_data: BookData, temp_dir, lua_config: DataConfig) -> List[Path]:
    file_list = []
    if lua_config.style == DataStyle.COLUMN.value:
        data_columns = book_data.data_columns()
        for key in data_columns:
            # data = {"data": data_columns[key]}
            data = data_columns[key]
            data_name = f"{book_data.name}_{key}"
            output_file = Path(temp_dir).joinpath(data_name).with_suffix(lua_config.suffix)
            _convert_data_to_file(output_file, book_data, data, data_name, lua_config)
            file_list.append(output_file)
    else:
        if lua_config.style == DataStyle.MAP.value:
            data = book_data.data_map()
        else:
            data = book_data.data_list()
        data_name = book_data.name
        output_file = Path(temp_dir).joinpath(data_name).with_suffix(lua_config.suffix)
        _convert_data_to_file(output_file, book_data, data, data_name, lua_config)
        file_list.append(output_file)
    return file_list


def _convert_data_to_file(output_file, book_data, data, data_name, lua_config: DataConfig):
    output_file = Path(output_file)
    data_text = object_to_lua_text(
        data,
        book_data.keys,
        0,
        lua_config.format_depth,
        lua_config.format_indent,
        lua_config.format_separators,
    )
    output_text = f"local {data_name} = {data_text}\nreturn {data_name}\n"
    if lua_config.schema == "lua":
        schema_text = _get_schema_text(book_data)
        output_text = schema_text + "\n\n" + output_text
    write_file(output_text, output_file)


def _get_schema_text(excel_data: BookData) -> str:
    data_list = []
    for key in excel_data.keys:
        data = excel_data.schema[key]
        ttype = data["type"]
        title = data["title"]
        text = f"-- [{ttype}] {title}\n    {key} = nil"
        data_list.append(text)
    data_text = "    " + ",\n    ".join(data_list)
    if len(data_list) > 0:
        data_text = data_text + ","
    data_text = f"local {excel_data.name}_type = {{\n{data_text}\n}}"
    return data_text


def object_to_lua_text(obj: object, sort_keys: List[str], depth: int, max_depth: int, indent=4, separators=(", ", " = ")) -> str:
    """Python 对象转换成 Lua table 文本

    Args:
        obj (str): Python 对象
        depth (str): 格式化 lua 当前层级
        max_depth (str): 格式化 lua 最大深度
        indent (int, optional): 格式化 lua 缩进字符数. Defaults to 4.
        separators (tuple, optional): 格式化 lua 分割符号，逗号和等号. Defaults to (", ", " = ").

    Returns:
        str: Lua table 文本
    """
    if isinstance(obj, list):
        data_list = []
        for item in obj:
            data_list.append(object_to_lua_text(item, sort_keys, depth + 1, max_depth, indent, separators))
        if len(data_list) > 0:
            comma, indent1, indent2 = _getLineBreakIndent(depth + 1, max_depth, indent, separators)
            text = comma.join([str(x) for x in data_list])
            if depth == 0:
                text = text + ","
            text = f"{{{indent1}{text}{indent2}}}"
            return text
        return "{}"
    elif isinstance(obj, dict):
        _keys = sort_keys
        for key in sort_keys:
            if not key in obj:
                _keys = obj.keys()
                break
        data_list = []
        for key in _keys:
            value_str = object_to_lua_text(obj[key], sort_keys, depth + 1, max_depth, indent, separators)
            data_list.append(f'["{key}"]{separators[1]}{value_str}')
        if len(data_list) > 0:
            comma, indent1, indent2 = _getLineBreakIndent(depth + 1, max_depth, indent, separators)
            text = comma.join([str(x) for x in data_list])
            text = f"{{{indent1}{text}{indent2}}}"
            return text
        return "{}"
    elif isinstance(obj, str):
        return f'"{obj}"'
    return str(obj)


# def object_to_lua_text_list(obj, depth, max_depth, indent=4, separators=(", ", " = ")):
#     """Python 对象转换成 Lua table 文本

#     Args:
#         obj (_type_): _description_
#         depth (_type_): _description_
#         max_depth (_type_): _description_
#         indent (int, optional): _description_. Defaults to 4.
#         separators (tuple, optional): _description_. Defaults to (", ", " = ").

#     Returns:
#         _type_: _description_
#     """
#     indent_str = _getIndent(depth, max_depth, indent)
#     if isinstance(obj, list):
#         data_list = []
#         indent_str2 = _getIndent(depth + 1, max_depth, indent)
#         for item in obj:
#             data_list.append(indent_str2 + object_to_lua_text_list(item, depth + 1, max_depth, indent, separators))
#         if len(data_list) > 0:
#             data_start = "{"
#             date_end = "}"
#             if depth < max_depth:
#                 data_start = "{\n"
#                 date_end = "\n" + indent_str + "}"
#                 data_text = (separators[0].rstrip() + "\n").join(data_list)
#             else:
#                 data_text = (separators[0]).join(data_list)
#             data_text = f"{data_start}{data_text}{date_end}"
#         else:
#             data_text = "{}"
#         return data_text
#     elif isinstance(obj, dict):
#         data_list = []
#         indent_str2 = _getIndent(depth + 1, max_depth, indent)
#         for key in obj.keys():
#             value_str = object_to_lua_text_list(obj[key], depth + 1, max_depth, indent, separators)
#             data_list.append(indent_str2 + f'["{key}"]{separators[1]}{value_str}')
#         if len(data_list) > 0:
#             data_start = "{"
#             date_end = "}"
#             if depth < max_depth:
#                 data_start = "{\n"
#                 date_end = "\n" + indent_str + "}"
#                 data_text = (separators[0].rstrip() + "\n").join(data_list)
#             else:
#                 data_text = (separators[0]).join(data_list)
#             data_text = f"{data_start}{data_text}{date_end}"
#         else:
#             data_text = "{}"
#         return data_text
#     elif isinstance(obj, str):
#         return f'"{obj}"'
#     return str(obj)


def _getIndent(depth, max_depth, indent):
    if depth <= max_depth:
        return " " * indent * depth
    return ""


def _getLineBreakIndent(depth, max_depth, indent, separators):
    if depth <= max_depth:
        indent1 = "\n" + " " * indent * depth
        indent2 = "\n" + " " * indent * (depth - 1)
        comma_indent = str(separators[0]).rstrip() + indent1
    else:
        indent1 = ""
        indent2 = ""
        comma_indent = str(separators[0])
    return comma_indent, indent1, indent2
