#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from .main import create_proj_config
from .main import convert_config
from . import __version__


def main():
    """命令行执行"""
    print(f"Welcome to excel2x: v{__version__}")
    print(">>")
    parser = argparse.ArgumentParser(description="转换 Excel 配置表")
    parser.add_argument("-V", "--version", action="version", version=__version__, help="Display version")
    parser.add_argument("--config", dest="config", required=True, help="目标项目 config.json 配置文件")
    # 转换 Excel 参数
    group = parser.add_argument_group("convert config")
    group.add_argument("--group", dest="group", default="", help="转换分组, 多个用逗号隔开, 默认全部")
    group.add_argument("--include", dest="include", default="", help="筛选文件名称, 多个用逗号隔开, 默认全部")
    group.add_argument("--output", action="store_true", help="是否复制到目标目录")
    group.add_argument("--log", dest="log", default="info", choices=["debug", "info", "warn", "error"], type=str.lower, help="log 信息级别")
    # 生成项目配置参数
    group = parser.add_argument_group("create project config")
    group.add_argument("--create", action="store_true", help="创建项目配置")
    group.add_argument("--name", dest="name", default="project_name", help="项目名称")

    # 解析参数
    args = parser.parse_args()
    print("args: ", args.__dict__)
    if args.create is True:
        # 创建项目配置
        create_proj_config(args.config, args.name)
    else:
        # 开始转换
        convert_config(
            args.config,
            args.group,
            args.include,
            args.output is True,
            args.log,
        )


if __name__ == "__main__":
    main()
