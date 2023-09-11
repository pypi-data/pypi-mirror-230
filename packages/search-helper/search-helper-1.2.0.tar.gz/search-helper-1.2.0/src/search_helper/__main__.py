#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
search_helper.__main__

Main script

Copyright (C) 2020-2023 Rainer Schwarzbach

This file is part of search_helper.

search_helper is free software:
you can redistribute it and/or modify it under the terms of the MIT License.

search_helper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import locale
import os
import sys

from search_helper import __version__


#
# Functions
#


def main(*arguments: str) -> int:
    """Main script function"""
    try:
        first_argument = arguments[1]
    except IndexError:
        config_file_name = ""
    else:
        if first_argument == "--version":
            print(__version__)
            return 0
        #
        config_file_name = first_argument
    #
    # pylint: disable=import-outside-toplevel
    from search_helper import gui_main

    current_locale = os.getenv("LANG", locale.getlocale()[0] or "C")
    languages = [current_locale]
    if "_" in current_locale:
        languages.append(current_locale.split("_")[0])
    #
    gui_main.UserInterface(config_file_name, *languages)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv))


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
