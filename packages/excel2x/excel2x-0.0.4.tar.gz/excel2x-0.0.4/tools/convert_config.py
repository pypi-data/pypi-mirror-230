#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""转换当前目录下的配置 config.json
"""
import os
import io
import sys
import colorama

from excel2x.main import convert_config

colorama.init(autoreset=True)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


if __name__ == "__main__":
    try:
        config_path = os.path.join(os.getcwd(), "config.json")
        # 工作目录
        convert_config(config_path)
    except Exception as e:
        print(e)
    input("Press Enter to continue...")
