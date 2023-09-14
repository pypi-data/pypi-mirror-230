#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""utils
"""

from enum import Enum


class DataStyle(Enum):
    LIST = "list"
    MAP = "map"
    COLUMN = "column"


class DataConfig(dict):
    def __init__(
        self,
        option: dict = None,
        data_type="json",
        suffix=".json",
        style="list",
        schema="",
        indent=4,
        max_depth=1,
        separators=(", ", " = "),
    ):
        self.data_type = data_type
        self.suffix = suffix
        self.style = style
        self.schema = schema
        self.format_indent = indent
        self.format_depth = max_depth
        self.format_separators = separators

        if option is not None:
            # 解析参数
            for key in ["data_type", "suffix", "style", "schema", "format_indent", "format_depth", "format_separators"]:
                value1 = getattr(self, key)
                value2 = option.get(key)
                if value2 is not None and isinstance(value2, type(value1)):
                    setattr(self, key, value2)


# Excel 配置
class ExcelConfig:
    def __init__(self, title_line=1, type_line=2, key_line=3, value_line=4):
        # excel 表数据
        self.sheet_index = 0
        self.title_line = title_line
        self.type_line = type_line
        self.key_line = key_line
        self.value_line = value_line


# Excel 表数据
class BookData(dict):
    def __init__(self, name, schema, keys, values):
        self.name = name
        self.schema = schema
        self.keys = keys
        self.values = values

    def data_list(self):
        return [dict(zip(self.keys, row)) for row in self.values]

    def data_map(self, primary_key="key"):
        if primary_key in self.schema:
            data_map = {}
            for row in self.values:
                data = dict(zip(self.keys, row))
                data_map[str(data[primary_key])] = data
            return data_map
        raise ValueError(f"{self.name} 没有主键 {primary_key}")

    def data_columns(self):
        data_split = {}
        for i, key in enumerate(self.keys):
            data_split[key] = []
            for row in self.values:
                value = row[i]
                data_split[key].append(value)
        return data_split
