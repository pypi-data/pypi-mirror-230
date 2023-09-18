# -------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Test the formatter group object examples.
"""
import unittest
from typing import List, Tuple

import fmtutil.formatter as fmt


class FormatterGroupExampleTestCase(unittest.TestCase):
    def test_fmt_group_parse_examples(self):
        grouping: fmt.FormatterGroupType = fmt.make_group(
            {
                "naming": fmt.make_const(
                    fmt=fmt.Naming,
                    value="data_engineer",
                ),
                "domain": fmt.make_const(
                    fmt=fmt.Naming,
                    value="demo",
                ),
                "timestamp": fmt.Datetime,
            }
        )
        rs_parse: List[fmt.FormatterGroup] = []
        for filename in (
            "dataEngineer_demo_20230101.json",
            "dataEngineer_demo_20230226.json",
            "dataEngineer_demo_20230418.json",
            "dataEngineer_demo_20230211_temp.json",
            "dataEngineer_demo_20230101_bk.json",
        ):
            try:
                rs_parse.append(
                    grouping.parse(
                        filename,
                        "{naming:%c}_{domain:%s}_{timestamp:%Y%m%d}.json",
                    )
                )
            except fmt.FormatterGroupArgumentError:
                continue
        self.assertEqual("20230418", max(rs_parse).format("{timestamp:%Y%m%d}"))
        self.assertEqual("20230101", min(rs_parse).format("{timestamp:%Y%m%d}"))

    def test_fmt_group_parse_examples02(self):
        CompressConst: fmt.ConstantType = fmt.make_const(
            name="CompressConst",
            formatter={
                "%g": "gzip",
                "%-g": "gz",
                "%b": "bz2",
                "%r": "rar",
                "%x": "xz",
                "%z": "zip",
            },
        )

        FileExtensionConst: fmt.ConstantType = fmt.make_const(
            name="FileExtensionConst",
            formatter={
                "%j": "json",
                "%y": "yaml",
                "%e": "env",
                "%t": "toml",
            },
        )

        def grouping2() -> fmt.FormatterGroupType:
            return fmt.make_group(
                {
                    "naming": fmt.make_const(
                        fmt=fmt.Naming, value="conn_local_data_landing"
                    ),
                    "domain": fmt.make_const(fmt=fmt.Naming, value="demo"),
                    "compress": CompressConst,
                    "extension": FileExtensionConst,
                    "version": fmt.Version,
                    "timestamp": fmt.Datetime,
                }
            )

        rs_parse: List[Tuple[int, fmt.FormatterGroup]] = []
        for idx, filename in enumerate(
            [
                "conn_local_data_landing.20230915_162359.json",
                "conn_local_data_landing.20230917_135234.json",
            ]
        ):
            try:
                rs_parse.append(
                    (
                        idx,
                        # grouping1.parse(
                        grouping2().parse(
                            value=filename,
                            fmt=r"{naming:%s}.{timestamp:%Y%m%d_%H%M%S}\.json",
                        ),
                    )
                )
            except fmt.FormatterGroupArgumentError:
                continue
        # This line will show the diff of unique id of these classes
        a: fmt.FormatterGroup = rs_parse[0][1]
        b: fmt.FormatterGroup = rs_parse[1][1]
        self.assertFalse(id(a.__class__) == id(b.__class__))

        # Able to get the max value from diff unique id
        max_rs = sorted(
            rs_parse,
            key=lambda x: (x[1],),
            reverse=False,
        )
        self.assertEqual("20230917", max_rs[-1][1].format("{timestamp:%Y%m%d}"))
