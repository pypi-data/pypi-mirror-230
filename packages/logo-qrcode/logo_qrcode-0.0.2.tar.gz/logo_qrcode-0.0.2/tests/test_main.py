#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""test
"""
import sys
import pathlib

root_dir = pathlib.Path(__file__).absolute().parent
sys.path.insert(0, str(root_dir))


# using pytest
def test_main():
    from logo_qrcode import logo_qrcode

    print(logo_qrcode._version__)
