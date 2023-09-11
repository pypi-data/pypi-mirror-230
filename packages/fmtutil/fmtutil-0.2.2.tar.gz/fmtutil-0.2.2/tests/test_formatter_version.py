# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the Version formatter object.
"""
import unittest

from packaging.version import Version

import fmtutil.formatter as fmt
from fmtutil.exceptions import FormatterValueError


class VersionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.vs = fmt.Version(
            {
                "major": "8",
                "minor": "1",
                "micro": "0",
                "post": "post2",
                "local": "+local1.0",
            }
        )
        self.vs2 = fmt.Version(
            {
                "epoch": "1",
                "major": "4",
                "minor": "8",
                "micro": "12",
                "dev": "dev1",
                "local": "+local0.0.13",
            }
        )
        self.vs3 = fmt.Version(
            {
                "major": "0",
                "minor": "1",
                "micro": "0",
                "pre": "rc3",
            }
        )
        self.vs_default = fmt.Version()
        self.vs_p = fmt.Version.parse("1.2.3beta4", "%m.%n.%c%q")
        self.vs_p2 = fmt.Version.parse("asdf_asdf.sadf", "%-l")

    def test_version_raise_for_pre_or_post_not_valid(self):
        with self.assertRaises(FormatterValueError) as context:
            fmt.Version(
                {
                    "major": "0",
                    "minor": "1",
                    "micro": "0",
                    "pre": "rx3",
                }
            )
        self.assertTrue(
            "Convert prefix dose not valid for value `rx3`"
            in str(context.exception)
        )

    def test_version_regex(self):
        self.assertDictEqual(
            {
                "%m": "(?P<major>\\d{1,3})",
                "%n": "(?P<minor>\\d{1,3})",
                "%c": "(?P<micro>\\d{1,3})",
                "%e": "(?P<epoch>[0-9]+!)",
                "%-e": "(?P<epoch_num>[0-9]+)",
                "%q": "(?P<pre>(a|b|c|rc|alpha|beta|pre|preview)[-_\\.]?[0-9]+)",
                "%p": "(?P<post>(?:(post|rev|r)[-_\\.]?[0-9]+)|(?:-[0-9]+))",
                "%-p": "(?P<post_num>[0-9]+)",
                "%d": "(?P<dev>dev[-_\\.]?[0-9]+)",
                "%l": "(?P<local>\\+[a-z0-9]+(?:[-_\\.][a-z0-9]+)*)",
                "%-l": "(?P<local_str>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*)",
                "%f": "(?P<major>\\d{1,3})_(?P<minor>\\d{1,3})_(?P<micro>\\d{1,3})",
                "%-f": "(?P<major>\\d{1,3})-(?P<minor>\\d{1,3})-(?P<micro>\\d{1,3})",
            },
            fmt.Version.regex(),
        )

    def test_version_formatter(self):
        formatter = fmt.Version.formatter(version=Version(version="0.5.6"))
        regex = fmt.Version.regex()
        self.assertDictEqual(
            {
                "%f": {
                    "regex": (
                        "(?P<major>\\d{1,3})_(?P<minor>\\d{1,3})_"
                        "(?P<micro>\\d{1,3})"
                    ),
                    "value": "0_5_6",
                },
                "%-f": {
                    "regex": (
                        "(?P<major>\\d{1,3})-(?P<minor>\\d{1,3})-"
                        "(?P<micro>\\d{1,3})"
                    ),
                    "value": "0_5_6",
                },
                "%m": {"regex": "(?P<major>\\d{1,3})", "value": "0"},
                "%n": {"regex": "(?P<minor>\\d{1,3})", "value": "5"},
                "%c": {"regex": "(?P<micro>\\d{1,3})", "value": "6"},
                "%e": {"regex": "(?P<epoch>[0-9]+!)", "value": "0!"},
                "%-e": {"regex": "(?P<epoch_num>[0-9]+)", "value": "0"},
                "%q": {
                    "regex": (
                        "(?P<pre>(a|b|c|rc|alpha|beta|pre|preview)[-_\\.]?"
                        "[0-9]+)"
                    ),
                    "value": "",
                },
                "%p": {
                    "regex": (
                        "(?P<post>(?:(post|rev|r)[-_\\.]?[0-9]+)|(?:-[0-9]+))"
                    ),
                    "value": "",
                },
                "%-p": {"regex": "(?P<post_num>[0-9]+)", "value": ""},
                "%d": {"regex": "(?P<dev>dev[-_\\.]?[0-9]+)", "value": ""},
                "%l": {
                    "regex": "(?P<local>\\+[a-z0-9]+(?:[-_\\.][a-z0-9]+)*)",
                    "value": None,
                },
                "%-l": {
                    "regex": "(?P<local_str>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*)",
                    "value": "+None",
                },
            },
            {
                i: {
                    "regex": regex[i],
                    "value": fmt.caller(formatter[i]["value"]),
                }
                for i in formatter
            },
        )

    def test_version_formatter_raise(self):
        with self.assertRaises(fmt.FormatterValueError) as context:
            fmt.Version.formatter("2.0.0")
        self.assertTrue(
            "Version formatter does not support for value, '2.0.0'."
            in str(context.exception)
        )

    def test_version_properties(self):
        self.assertEqual(
            "<Version.parse('v8.1.0post2+local1.0', 'v%m.%n.%c%p%l')>",
            self.vs.__repr__(),
        )
        self.assertEqual(
            "<Version.parse('1!4.8.12.dev1+local0.0.13', '%e%m.%n.%c%d%l')>",
            self.vs2.__repr__(),
        )
        self.assertEqual(
            "<Version.parse('v0.1.0rc3', 'v%m.%n.%c%q')>", self.vs3.__repr__()
        )

        self.assertEqual("v8.1.0post2+local1.0", self.vs.__str__())
        self.assertEqual("1!4.8.12.dev1+local0.0.13", self.vs2.__str__())
        self.assertEqual("v0.1.0rc3", self.vs3.__str__())

        # Test `cls.string` property
        self.assertEqual("v8.1.0post2+local1.0", self.vs.string)
        self.assertEqual("1!4.8.12.dev1+local0.0.13", self.vs2.string)
        self.assertEqual("v0.1.0rc3", self.vs3.string)
        self.assertEqual("v1.2.3b4", self.vs_p.string)
        self.assertEqual("v0.0.0+asdf_asdf.sadf", self.vs_p2.string)

        # Test `cls.value` property
        self.assertEqual(Version(version="v8.1.0post2+local1.0"), self.vs.value)

    def test_version_format(self):
        self.assertEqual("8_1_0", self.vs.format("%f"))
        self.assertEqual("+local1.0", self.vs.format("%-l"))
        self.assertEqual("1", self.vs2.format("%d"))
        self.assertEqual(
            "1!_4_8_12_1_local0.0.13", self.vs2.format("%e_%f_%d_%l")
        )

    def test_version_order(self):
        self.assertTrue(self.vs <= self.vs2)
