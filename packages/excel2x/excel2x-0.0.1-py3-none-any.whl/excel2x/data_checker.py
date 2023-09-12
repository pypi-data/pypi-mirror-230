#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""数据检查器
"""


class DataChecker:
    def __init__(self):
        pass

    def do_check(self, book_data: dict) -> (bool, str):
        """检查数据

        Args:
            book_data (dict): book_data

        Returns:
            (bool, str): (True, ok) 或 (False, 数据异常原因)
        """
        if book_data is None:
            return False, ""
        return True, "ok"
