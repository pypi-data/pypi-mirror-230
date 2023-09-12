#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""Convert Excel config to X
"""
import os
import sys
import json
import argparse
from typing import List
from pathlib import Path

from excel2x.utils import log_error
from excel2x.utils import log_info
from excel2x.utils import print_line
from excel2x.utils import read_file
from excel2x.utils import write_file

from excel2x.model import OutputConfig
from excel2x.excel_to_lua import book_to_lua_file
from excel2x.excel_to_json import book_to_json
from excel2x.excel_reader import read_excel_book


def read_config(config_path: str) -> dict:
    """读取项目配置

    Args:
        config_path (str): 项目配置 json 路径

    Returns:
        dict: 项目配置 json dict 对象
    """
    config_path = Path(str(config_path))
    if config_path.exists() and config_path.suffix == ".json":
        config_text = read_file(config_path)
        proj_config = json.loads(config_text)
        is_check_ok = True
        for key in ["name", "root_dir", "config_dir", "output_dir", "client_dir", "groups", "option_template"]:
            if key not in proj_config:
                log_error(f"config 缺少配置: {key}")
                is_check_ok = False
        if is_check_ok:
            return proj_config

    log_error(f"config 路径不存在或不是 json 格式：{config_path.resolve()}")
    workspace = os.path.dirname(__file__)
    temp_config_path = Path(workspace).joinpath("config_template.json")
    log_error("请参考 config 模板:")
    config_text = read_file(temp_config_path)
    log_info(config_text)
    sys.exit(1)


def create_proj_config(proj_config_path: str | Path, proj_name: str = "proj_name"):
    """根据模板 config_template.json 选择创建标准项目配置

    Args:
        proj_dir (str | Path): 项目路径/config.json
        proj_name (str): 项目名称

    Raises:
        FileNotFoundError: 找不到项目路径，请先创建项目
    """
    proj_config_path = str(proj_config_path)
    if not proj_config_path.endswith(".json"):
        # 配置文件需要是 json 文件
        raise ValueError("配置文件需要是 json 文件, 例如：项目路径/config.json")

    if not Path(proj_config_path).parent.exists():
        # 项目路径不存在
        raise FileNotFoundError("project_dir not found! Please create a project first!")

    workspace = os.path.dirname(__file__)
    temp_config_path = Path(workspace).joinpath("config_template.json")
    log_error("请参考 config 模板:")
    config_text = read_file(temp_config_path)
    proj_config = json.loads(config_text)
    proj_config["name"] = str(proj_name)
    config_text2 = json.dumps(proj_config, indent=4, ensure_ascii=False)
    write_file(proj_config_path, config_text2)


def is_excel(file_name: str) -> bool:
    """判断文件名是否 Excel 文件

    Args:
        file_name (str): Excel 文件名

    Returns:
        bool: 是否是 Excel 文件
    """
    if not file_name.startswith("~") and not file_name.startswith(".") and (file_name.endswith(".xls") or file_name.endswith(".xlsx")):
        return True
    return False


def convert_config(config_path: str, include_groups="", include_names="", is_copy=False):
    """开始转换 Excel to X

    Args:
        config_path (str): 项目配置路径 xxx.json
        group (str, optional): 筛选分组，默认全部.
        include (str, optional): 筛选文件名，默认全部.
        is_copy (bool, optional): 是否复制到 client_dir 路径. Defaults to False.
    """
    try:
        print_line("convert_config")
        log_info("config".ljust(10), ":", config_path)
        log_info("groups".ljust(10), ":", include_groups)
        log_info("includes".ljust(10), ":", include_names)
        log_info("is_copy".ljust(10), ":", is_copy)
        proj_config = read_config(config_path)
        target_name = proj_config["name"]
        root_dir = Path(config_path).parent.joinpath(proj_config["root_dir"])
        print_line("Project")
        log_info("name".ljust(10), ":", target_name)
        log_info("root_dir".ljust(10), ":", root_dir.resolve())
        os.chdir(root_dir)
        print_line()
        select_group_dict = {name.lower(): True for name in (include_groups or "").split(",") if len(name) > 0}
        select_name_dict = {name.lower(): True for name in (include_names or "").split(",") if len(name) > 0}

        config_dir = root_dir.joinpath(proj_config["config_dir"])
        output_dir = root_dir.joinpath(proj_config["output_dir"])
        client_dir = root_dir.joinpath(proj_config["client_dir"])
        groups = proj_config["groups"]
        option_template: dict = proj_config["option_template"]
        for option in option_template.values():
            if "output_dir" in option:
                option["output_dir"] = str(root_dir.joinpath(option["output_dir"]))
            else:
                option["output_dir"] = str(output_dir)
            if "copy_to_dir" in option:
                option["copy_to_dir"] = str(option["copy_to_dir"]).replace("{client_dir}", str(client_dir))

        group_iterdir = sorted([x for x in config_dir.iterdir() if x.is_dir()])
        for item in group_iterdir:
            # group 名称
            group_name = item.stem
            array = group_name.split("_")
            # group 基本名
            group_base = array[0]
            # group 变体名
            # group_variant = array[1] if len(array) > 1 else ""
            if group_base not in groups:
                # 找不到 group: {group_base} 配置!
                continue
            if len(select_group_dict) > 0 and group_name.lower() not in select_group_dict:
                # 未选中 group
                continue
            print_line("Convert group: " + group_name)
            option_list = groups[group_base]
            file_iterdir = sorted([x for x in item.iterdir() if is_excel(x.name) and (len(select_name_dict) == 0 or x.stem.lower() in select_name_dict)])
            for excel_file in file_iterdir:
                log_info(f">> Convert: {excel_file.relative_to(root_dir)}")
                book_data = read_excel_book(excel_file)
                for option_key in option_list:
                    if option_key in option_template:
                        try:
                            option = option_template[option_key]
                            log_info("·· Option:", option_key)
                            out_files = _convert_one(book_data, option, group_name)
                            if is_copy:
                                copy_to_dir = Path(option["copy_to_dir"]).joinpath(group_base)
                                for item in out_files:
                                    copy_to = copy_to_dir.joinpath(item.name)
                                    log_info(f"·· Copy to: {copy_to}")
                        except Exception as err:
                            log_error(err)
                    else:
                        log_error(f"找不到配置模板: {option_key}, 请先在 option_template 中添加!")
        print_line()

    except Exception as e:
        log_error(e)
    finally:
        print_line()
        log_info("Have a nice day!")


def _convert_one(book_data, option, group_name: str) -> List[Path]:
    output_dir2 = Path(option["output_dir"]).joinpath(group_name)
    output_config = OutputConfig(option)
    if option["data_type"] == "lua":
        out_files = book_to_lua_file(book_data, output_dir2, output_config)
    else:
        log_error("xx ")
        log_info(option)
        out_files = book_to_json(book_data, output_dir2, output_config)
    log_info("·· \033[1;32mSuccess\033[0m:", "\n".ljust(13).join([str(x) for x in out_files]))
    return out_files


if __name__ == "__main__":
    log_info("Welcome to excel2x!")
    log_info(">>")
    parser = argparse.ArgumentParser(description="转换 Excel 配置表")
    parser.add_argument("--config", dest="config", required=True, help="目标项目 config.json 配置文件")
    parser.add_argument("--group", dest="group", default="", help="转换分组, 多个用逗号隔开, 默认全部")
    parser.add_argument("--include", dest="include", default="", help="筛选文件名称, 多个用逗号隔开, 默认全部")
    parser.add_argument("--copy", action="store_true", help="是否复制到 Client 目录？")
    parser.add_argument("--create", action="store_true", help="创建是项目配置？")
    parser.add_argument("--name", dest="name", default="project_name", help="项目名称")
    # 解析参数
    args = parser.parse_args()
    log_info("args: ", args.__dict__)
    if args.create:
        # 创建项目配置
        create_proj_config(args.config, args.name)
    else:
        # 开始转换
        convert_config(args.config, args.group, args.include, args.copy is True)
