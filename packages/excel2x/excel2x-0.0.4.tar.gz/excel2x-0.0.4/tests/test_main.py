#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import pathlib

root_dir = pathlib.Path(__file__).absolute().parent.parent
sys.path.insert(0, str(root_dir.joinpath("src")))


# using pytest
def test_main():
    import excel2x

    print(excel2x._version__)
