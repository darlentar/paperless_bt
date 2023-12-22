import csv
import logging
from collections import defaultdict
from dataclasses import dataclass

from paperless_bt.coordinates import compute_haversine, lamber93_to_gps

logger = logging.getLogger(__name__)


class MNCFormatError(Exception):
    pass


class MobileSiteFormatError(Exception):
    pass


class MobileSiteGPSFormatError(Exception):
    pass


@dataclass
class MobileSite:
    provider: str
    lambert93: tuple[int, int]
    has_2g: bool
    has_3g: bool
    has_4g: bool


@dataclass
class MobileSiteGPS:
    provider: str
    gps: tuple[float, float]
    has_2g: bool
    has_3g: bool
    has_4g: bool


def mobile_site_row_to_mobilesite(row: list[str]) -> MobileSite:
    return MobileSite(
        provider=row[0],
        lambert93=(int(row[1]), int(row[2])),
        has_2g=row[3] == "1",
        has_3g=row[4] == "1",
        has_4g=row[5] == "1",
    )


def mobile_site_gps_row_to_mobilesite(row: list[str]) -> MobileSiteGPS:
    return MobileSiteGPS(
        provider=row[0],
        gps=(float(row[1]), float(row[2])),
        has_2g=row[3] == "True",
        has_3g=row[4] == "True",
        has_4g=row[5] == "True",
    )


def read_mobile_site(filename: str) -> list[MobileSite]:
    res = []
    with open(filename, newline="") as csvfile:
        mobile_site_reader = csv.reader(csvfile, delimiter=";")
        # ignore headers
        try:
            next(mobile_site_reader)
        except StopIteration:
            raise MobileSiteFormatError
        for row in mobile_site_reader:
            try:
                res.append(mobile_site_row_to_mobilesite(row))
            except (IndexError, ValueError):
                logger.error("incorrect row{}".format(row))
                raise MobileSiteFormatError
    return res


def read_mobile_site_gps(filename: str) -> list[MobileSiteGPS]:
    res = []
    with open(filename, newline="") as csvfile:
        mobile_site_gps_reader = csv.reader(csvfile, delimiter=" ")
        for row in mobile_site_gps_reader:
            try:
                res.append(mobile_site_gps_row_to_mobilesite(row))
            except (IndexError, ValueError):
                logger.error("incorrect row: {}".format(row))
                raise MobileSiteGPSFormatError
    # we should have at least one line
    if res == []:
        raise MobileSiteGPSFormatError
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
            except (IndexError, ValueError):
                logger.error("incorrect row{}".format(row))
                raise MNCFormatError
    # we sould have at least one line
    if res == []:
        raise MNCFormatError
    return res


class ProviderResolver:
    def __init__(
        self,
        mobile_sites: list[MobileSiteGPS],
        brand_mobile_codes: list[BrandMobileCodes],
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


def convert_lanbert93_to_gps(mobile_site: MobileSite) -> MobileSiteGPS:
    return MobileSiteGPS(
        provider=mobile_site.provider,
        gps=lamber93_to_gps(*mobile_site.lambert93),
        has_2g=mobile_site.has_2g,
        has_3g=mobile_site.has_3g,
        has_4g=mobile_site.has_4g,
    )


def filter_reachable_mobile_sites(
    position: tuple[float, float],
    mobile_sites: list[MobileSiteGPS],
) -> dict[str, dict[str, list[MobileSiteGPS]]]:
    res: dict[str, dict[str, list[MobileSiteGPS]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for mobile_site in mobile_sites:
        distance = compute_haversine(
            position[0],
            mobile_site.gps[0],
            position[1],
            mobile_site.gps[1],
        )
        if distance < 30e3 and mobile_site.has_2g:
            res[mobile_site.provider]["2g"].append(mobile_site)
        if distance < 5e3 and mobile_site.has_3g:
            res[mobile_site.provider]["3g"].append(mobile_site)
        if distance < 10e3 and mobile_site.has_4g:
            res[mobile_site.provider]["4g"].append(mobile_site)
    return res
