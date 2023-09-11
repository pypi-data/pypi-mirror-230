# -*- coding: utf-8 -*-

"""

search_helper.paths

Paths module

Copyright (C) 2020-2023 Rainer Schwarzbach

This file is part of search_helper.

search_helper is free software:
you can redistribute it and/or modify it under the terms of the MIT License.

search_helper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


from pathlib import Path


PACKAGE_MODULES_PATH = Path(__file__).resolve().parent
PACKAGE_DATA_PATH = PACKAGE_MODULES_PATH / "data"
PACKAGE_LOCALE_PATH = PACKAGE_MODULES_PATH / "locale"


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
