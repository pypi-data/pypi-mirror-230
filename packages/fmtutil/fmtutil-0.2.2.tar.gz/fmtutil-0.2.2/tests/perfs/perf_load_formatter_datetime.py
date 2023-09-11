from datetime import datetime
from pathlib import Path
from typing import Iterator, List

from memory_profiler import profile

from fmtutil import Datetime

perf_path = Path().parent / "assets" / "perf_load_formatter_dt.log"
perf_path.parent.mkdir(parents=True, exist_ok=True)
perf_f = perf_path.open(mode="w+")


def make_datetime_formatter(value: str) -> Datetime:
    dt = Datetime.parse(value, "%Y%m%d")
    assert dt.value
    return dt


class DatetimePerfLoadTestCase:  # no cov
    def __init__(self):
        self.dts: Iterator[str] = (
            datetime.now().strftime("%Y%m%d") for _ in range(1, 1000)
        )
        self.dts2: Iterator[str] = (
            datetime.now().strftime("%Y%m%d") for _ in range(1, 10000)
        )
        self.dts3: Iterator[str] = (
            datetime.now().strftime("%Y%m%d") for _ in range(1, 100000)
        )

    @profile(precision=4, stream=perf_f)
    def perf_datetime_parse_01(self):
        dts: List[Datetime] = [make_datetime_formatter(dt) for dt in self.dts]
        print(len(dts))

    @profile(precision=4, stream=perf_f)
    def perf_datetime_parse_02(self):
        dts: List[Datetime] = [make_datetime_formatter(dt) for dt in self.dts2]
        print(len(dts))

    @profile(precision=4, stream=perf_f)
    def perf_datetime_parse_03(self):
        dts: List[Datetime] = [make_datetime_formatter(dt) for dt in self.dts3]
        print(len(dts))

    def runner(self):
        for name in filter(lambda x: not x.startswith("_"), dir(self)):
            if name.startswith("perf_"):
                method = getattr(self, name)
                method()


if __name__ == "__main__":
    testcase = DatetimePerfLoadTestCase()
    testcase.runner()
