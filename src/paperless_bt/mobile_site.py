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


@dataclass
class BrandMobileCodes:
    mcc: int
    mnc: int
    brand: str


def read_mnc(filename: str) -> list[BrandMobileCodes]:
    res = []
    with open(filename, newline="") as csvfile:
        mnc_reader = csv.reader(csvfile, delimiter=",")
        # ignore headers
        next(mnc_reader, None)
        for row in mnc_reader:
            try:
                res.append(
                    BrandMobileCodes(
                        mcc=int(row[0]),
                        mnc=int(row[1]),
                        brand=row[2],
                    )
                )
            except ValueError:
                # we ignore the line if we can't convert the values
                # TODO: should be logged
                pass
    return res


class ProviderResolver:
    def __init__(
        self, mobile_sites: list[MobileSite], brand_mobile_codes: list[BrandMobileCodes]
    ):
        self.mobile_sites = mobile_sites
        self.brand_mobile_codes = brand_mobile_codes
        self.provider_id_to_brand = {}
        for brand_mobile_code in self.brand_mobile_codes:
            self.provider_id_to_brand[
                f"{brand_mobile_code.mcc:d}{brand_mobile_code.mnc:02d}"
            ] = brand_mobile_code.brand

    def resolve(self, provider_id: str) -> str:
        try:
            return self.provider_id_to_brand[provider_id]
        except KeyError:
            raise UnknownProvider(provider_id)


class UnknownProvider(Exception):
    pass
