# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the error object.
"""
import unittest

import fmtutil.exceptions as err


class ErrorsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        ...

    def test_err_config_str_arg(self):
        result = err.FormatterArgumentError(
            argument="timestamp",
            message=(
                "order file object does not have `timestamp` in name "
                "formatter"
            ),
        )
        respec: str = (
            "with 'timestamp', order file object does not have `timestamp` "
            "in name formatter"
        )
        self.assertEqual(str(result), respec)

    def test_err_config_tuple_arg(self):
        result = err.FormatterArgumentError(
            argument=("timestamp", "serial"),
            message=(
                "order file object does not have `timestamp` and `serial` "
                "in name formatter"
            ),
        )
        respec: str = (
            "with 'timestamp', and 'serial', order file object does not have "
            "`timestamp` and `serial` in name formatter"
        )
        self.assertEqual(str(result), respec)
