import csv
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MobileSite:
    provider: str
    lambert93: Tuple[int, int]
    has_2g: bool
    has_3g: bool
    has_4g: bool


def read_mobile_site(filename: str) -> list[MobileSite]:
    res = []
    with open(filename, newline="") as csvfile:
        mobile_site_reader = csv.reader(csvfile, delimiter=";")
        # ignore headers
        next(mobile_site_reader, None)
        for row in mobile_site_reader:
            try:
                res.append(
                    MobileSite(
                        provider=row[0],
                        lambert93=(int(row[1]), int(row[2])),
                        has_2g=bool(row[3]),
                        has_3g=bool(row[4]),
                        has_4g=bool(row[5]),
                    )
                )
            except ValueError:
                # we ignore the line if we can't convert the values
                # TODO: should be logged
                pass
    return res
