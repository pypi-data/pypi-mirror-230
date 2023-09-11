# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the formatter object examples for Version.
"""
import unittest

from packaging.version import Version

import fmtutil.formatter as fmt


class VersionExampleTestCase(unittest.TestCase):
    def test_parse_examples(self):
        self.assertEqual(
            Version("1.0.5"),
            fmt.Version.parse("version: 1-0-5", "version: %m-%n-%c").value,
        )
        self.assertEqual(
            Version("1.0.0a0"),
            fmt.Version.parse("version: 1.0.0a0", "version: %m.%n.%c%q").value,
        )
        self.assertEqual(
            Version("1.0.0b0"),
            fmt.Version.parse("version: 1.0.0b0", "version: %m.%n.%c%q").value,
        )
        self.assertEqual(
            Version("1.0.0rc0"),
            fmt.Version.parse("version: 1.0.0rc0", "version: %m.%n.%c%q").value,
        )
        self.assertEqual(
            Version("1.0.0.post0"),
            fmt.Version.parse(
                "version: 1.0.0.post0", "version: %m.%n.%c.%p"
            ).value,
        )
        self.assertEqual(
            Version("1.0.0.dev0"),
            fmt.Version.parse(
                "version: 1.0.0.dev0", "version: %m.%n.%c.%d"
            ).value,
        )
