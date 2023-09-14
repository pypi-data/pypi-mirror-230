#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""Convert Excel to CSV file!

Raises:
    ValueError: 如果有文件或数据错误还跑出 ValueError
"""
from utils import write_file
from excel_reader import read_excel_values
from model import ExcelConfig


def convert_file(input_file, output_file, sheet_index=0, config: ExcelConfig = None):
    """Convert Excel to CSV file
    Args:
        input_file (string): 输入 Excel 文件路径
        output_file (string): 输出 CSV 文件路径
        sheet_index (int, optional): excel sheet index. Defaults to 0.
        config (ExcelConfig, optional): Excel config. Defaults to None.

    Raises:
        ValueError: 输出文件路径必须是 .csv 文件
    """
    if not str(output_file).endswith(".csv"):
        raise ValueError(f"output_file must end with .csv, but: {output_file}")
    data_text = convert_text(input_file, sheet_index, config)
    write_file(output_file, data_text)


def convert_text(input_file, sheet_index=0, config: ExcelConfig = None):
    """Convert Excel to CSV data text

    Args:
        input_file (string): 输入 Excel 文件路径
        sheet_index (int, optional): excel sheet index. Defaults to 0.
        config (ExcelConfig, optional): Excel config. Defaults to None.

    Returns:
        string: csv 数据格式文本
    """
    values = read_excel_values(input_file, sheet_index)
    data_text = "\n".join([",".join([str(cell) for cell in row]) for row in values])
    return data_text
