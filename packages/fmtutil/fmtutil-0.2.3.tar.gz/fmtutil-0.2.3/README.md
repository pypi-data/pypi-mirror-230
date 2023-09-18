# Utility Package: *Formatter*

[![test](https://github.com/korawica/fmtutil/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/fmtutil/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/korawica/fmtutil/branch/main/graph/badge.svg?token=J2MN63IFT0)](https://codecov.io/gh/korawica/fmtutil)
[![python support version](https://img.shields.io/pypi/pyversions/fmtutil)](https://pypi.org/project/fmtutil/)
[![size](https://img.shields.io/github/languages/code-size/korawica/fmtutil)](https://github.com/korawica/fmtutil)

**Table of Contents**:

- [Installation](#installation)
- [Formatter Objects](#formatter-objects)
  - [Datetime](#datetime)
  - [Version](#version)
  - [Serial](#serial)
  - [Naming](#naming)
  - [Storage](#storage)
  - [Constant](#constant)
- [FormatterGroup Object](#formattergroup-object)
- [Usecase](#usecase)

This **Formatter** package was created for `parse` and `format` any string values
that match format pattern with Python regular expression. This package be the
co-pylot project for stating to my **Python Software Developer** role.

## Installation

```shell
pip install fmtutil
```

:dart: First objective of this project is include necessary formatter objects for
any data components package which mean we can `parse` any complicate names on
data source and ingest the right names to in-house or data target.

For example, we want to get filename with the format like, `filename_20220101.csv`,
on the file system storage, and we want to incremental ingest the latest file with
date **2022-03-25** date. So we will implement `Datetime` object and parse
that filename to it,

```python
Datetime.parse('filename_20220101.csv', 'filename_%Y%m%d.csv').value == datetime.today()
```

The above example is :yawning_face: **NOT SURPRISE!!!** for us because Python
already provide build-in package `datetime` to parse by `{dt}.strptime` and
format by `{dt}.strftime` with any datetime string value. This package will the
special thing when we group more than one formatter objects together as
`Naming`, `Version`, and `Datetime`.

**For complex filename format like**:

```text
{filename:%s}_{datetime:%Y_%m_%d}.{version:%m.%n.%c}.csv
```

From above filename format string, the `datetime` package does not enough for
this scenario right? but you can handle by your hard-code object or create the
better package than this project.

> **Note**: \
> Any formatter object was implemented the `self.valid` method for help us validate
> format string value like the above example scenario,
> ```python
> this_date = Datetime.parse('20220101', '%Y%m%d')
> this_date.valid('any_files_20220101.csv', 'any_files_%Y%m%d.csv')  # True
> ```

## Formatter Objects

- [Datetime](#datetime)
- [Version](#version)
- [Serial](#serial)
- [Naming](#naming)
- [Storage](#storage)
- [Constant](#constant)

The main purpose is **Formatter Objects** for `parse` and `format` with string
value, such as `Datetime`, `Version`, and `Serial` formatter objects. These objects
were used for parse any filename with put the format string value. The formatter
able to enhancement any format value from sting value, like in `Datetime`, for `%B`
value that was designed for month shortname (`Jan`, `Feb`, etc.) that does not
support in build-in `datetime` package.

> **Note**: \
> The main usage of this formatter object is `parse` and `format` method.

### Datetime

```python
from fmtutil import Datetime

datetime = Datetime.parse(
    value='This_is_time_20220101_000101',
    fmt='This_is_time_%Y%m%d_%H%M%S'
)
datetime.format('This_datetime_format_%Y%b-%-d_%H:%M:%S')
```

```text
>>> 'This_datetime_format_2022Jan-1_00:01:01'
```

[Supported Datetime formats](/docs/en/docs/API.md#datetime)

### Version

```python
from fmtutil import Version

version = Version.parse(
    value='This_is_version_2_0_1',
    fmt='This_is_version_%m_%n_%c',
)
version.format('New_version_%m%n%c')
```

```text
>>> 'New_version_201'
```

[Supported Version formats](/docs/en/docs/API.md#version)

### Serial

```python
from fmtutil import Serial

serial = Serial.parse(
    value='This_is_serial_62130',
    fmt='This_is_serial_%n'
)
serial.format('Convert to binary: %b')
```

```text
>>> 'Convert to binary: 1111001010110010'
```

[Supported Serial formats](/docs/en/docs/API.md#serial)

### Naming

```python
from fmtutil import Naming

naming = Naming.parse(
    value='de is data engineer',
    fmt='%a is %n'
)
naming.format('Camel case is %c')
```

```text
>>> 'Camel case is dataEngineer'
```

[Supported Naming formats](/docs/en/docs/API.md#naming)

### Storage

```python
from fmtutil import Storage

storage = Storage.parse(
  value='This file have 250MB size',
  fmt='This file have %M size'
)
storage.format('The byte size is: %b')
```

```text
>>> 'The byte size is: 2097152000'
```

[Supported Storage formats](/docs/en/docs/API.md#storage)

### Constant

```python
from fmtutil import Constant, make_const
from fmtutil.exceptions import FormatterError

const = make_const({
  '%n': 'normal',
  '%s': 'special',
})
try:
    parse_const: Constant = const.parse(
        value='This_is_constant_normal',
        fmt='This_is_constant_%n'
    )
    parse_const.format('The value of %%s is %s')
except FormatterError as err:
    pass
```

```text
>>> 'The value of %s is special'
```

> **Note**: \
> This package already implement environment constant object, `fmtutil.EnvConstant`.

## FormatterGroup Object

The **FormatterGroup** object, `FormatterGroup`, which is the grouping of needed
mapping formatter objects and its alias formatter object ref name together. You
can define a name of formatter that you want, such as `name` for `Naming`, or
`timestamp` for `Datetime`.

**Parse**:

```python
from fmtutil import make_group, Naming, Datetime, FormatterGroupType

group: FormatterGroupType = make_group({'name': Naming, 'datetime': Datetime})
group.parse(
  'data_engineer_in_20220101_de',
  fmt='{name:%s}_in_{timestamp:%Y%m%d}_{name:%a}'
)
```

```text
>>> {
>>>     'name': Naming.parse('data engineer', '%n'),
>>>     'timestamp': Datetime.parse('2022-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
>>> }
```

**Format**:

```python
from fmtutil import FormatterGroup
from datetime import datetime

group_01: FormatterGroup = group({
  'name': 'data engineer',
  'datetime': datetime(2022, 1, 1)
})
group_01.format('{name:%c}_{timestamp:%Y_%m_%d}')
```

```text
>>> dataEngineer_2022_01_01
```

## Usecase

If you have multi-format filenames on data source directory, and you want to
dynamic getting these filenames to your app, you can make a formatter group for
this.

```python
from typing import List

from fmtutil import (
  make_group, Naming, Datetime, FormatterGroup, FormatterGroupType,
  FormatterArgumentError,
)

name: Naming = Naming.parse('Google Map', fmt='%t')

fmt_group: FormatterGroupType = make_group(
    {
        "naming": name.to_const(),
        "timestamp": Datetime,
    }
)

rs: List[FormatterGroup] = []
for file in (
  'googleMap_20230101.json',
  'googleMap_20230103.json',
  'googleMap_20230103_bk.json',
  'googleMap_with_usage_20230105.json',
  'googleDrive_with_usage_20230105.json',
):
    try:
        rs.append(
            fmt_group.parse(
                file,
                fmt=r'{naming:c}_{timestamp:%Y%m%d}\.json',
            )
        )
    except FormatterArgumentError:
        continue

repr(max(rs).groups['timestamp'])
```

```text
>>> <Datetime.parse('2023-01-03 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')>
```

> **Note**: \
> The above example will convert the name, Naming instance, to Constant
> instance before passing to a formatter group because I do not want to dynamic
> the naming format to find the filenames.

## License

This project was licensed under the terms of the [MIT license](LICENSE).
