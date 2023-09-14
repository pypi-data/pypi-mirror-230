#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import pathlib

root_dir = pathlib.Path(__file__).absolute().parent.parent
sys.path.insert(0, str(root_dir.joinpath("src")))


from excel2x.cli import main

if __name__ == "__main__":
    main()