# -*- coding: utf-8 -*-

"""

tests.test_main

Test the search_helper.__main__ module

Copyright (C) 2023 Rainer Schwarzbach

This file is part of search_helper.

search_helper is free software:
you can redistribute it and/or modify it under the terms of the MIT License.

search_helper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import dataclasses
import io
import sys

from unittest import TestCase
from unittest.mock import patch

from search_helper import __version__
from search_helper import __main__


@dataclasses.dataclass(frozen=True)
class MainCallResult:

    """Result from a __main__.main() call"""

    returncode: int = 0
    stdout: str = ""

    @classmethod
    def from_call(
        cls,
        *arguments,
        stdout=sys.stdout,
        stderr=sys.stderr,
        **kwargs,
    ):
        """Return a GenericCallResult instance
        from the real function call,
        mocking sys.stdin if stdin_data was provided.
        """
        assert stdout is sys.stdout
        assert stderr is sys.stderr
        returncode = __main__.main(*arguments, **kwargs)
        return cls(
            returncode=returncode,
            stdout=stdout.getvalue(),
        )


class ModuleTest(TestCase):

    """__main__ module"""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main(self, mock_stdout):
        """main() function"""
        result = MainCallResult.from_call(
            "search_helper", "--version", stdout=mock_stdout
        )
        self.assertEqual(result.stdout.rstrip(), __version__)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
