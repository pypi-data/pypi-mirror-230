#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""数据类型生成器
"""

import json


class TypeGenerator:
    def __init__(self, language):
        self._language = language

    @property
    def language(self) -> str:
        """获取生成器语言类型

        Returns:
            str: C#、Java、Lua、TypeScript 等等
        """
        return self._language

    def generate(self, schema: dict) -> str:
        """生成数据类型定义 schema

        Args:
            schema (dict): 类型定义 schema

        Returns:
            str: 类型定义类或接口文本
        """
        data_text = json.dumps(schema, indent=4, ensure_ascii=False)
        return data_text


class LuaTypeGenerator(TypeGenerator):
    def __init__(self):
        super().__init__("Lua")

    def generate(self, schema: dict) -> str:
        data_text = ""
        return data_text


class JavaBeanGenerator(TypeGenerator):
    def __init__(self):
        super().__init__("Java")

    def generate(self, schema: dict) -> str:
        data_text = ""
        return data_text


class TsTypeGenerator(TypeGenerator):
    def __init__(self):
        super().__init__("TypeScript")

    def generate(self, schema: dict) -> str:
        data_text = ""
        return data_text
