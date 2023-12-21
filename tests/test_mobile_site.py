import os

import pytest
from paperless_bt.mobile_site import (
    BrandMobileCodes,
    MobileSite,
    MobileSiteGPS,
    MobileSiteGPSFormatError,
    ProviderResolver,
    UnknownProvider,
    convert_lanbert93_to_gps,
    mobile_site_gps_row_to_mobilesite,
    mobile_site_row_to_mobilesite,
    read_mnc,
    read_mobile_site,
    read_mobile_site_gps,
)


def test_read_mobile_site():
    # TODO Do not hardcode this
    mobile_sites = read_mobile_site("site_mobiles.csv")
    assert len(mobile_sites) == 77147
    assert mobile_sites[-1] == MobileSite(
        provider="20801",
        lambert93=(1240585, 6154019),
        has_2g=True,
        has_3g=True,
        has_4g=True,
    )


def test_read_mobile_site_gps():
    # TODO Do not hardcode this
    mobile_sites = read_mobile_site_gps("site_mobiles_gps.csv")
    assert len(mobile_sites) == 77147
    assert mobile_sites[-1] == MobileSiteGPS(
        provider="20801",
        gps=(pytest.approx(9.5503891), pytest.approx(42.2843603)),
        has_2g=True,
        has_3g=True,
        has_4g=True,
    )


def test_read_mobile_site_gps_with_empty_file():
    with pytest.raises(MobileSiteGPSFormatError):
        read_mobile_site_gps("/dev/null")


def test_read_mobile_site_gps_with_wrong_format():
    uncorrect_format = os.path.abspath(__file__)
    print(uncorrect_format)
    with pytest.raises(MobileSiteGPSFormatError):
        read_mobile_site_gps(uncorrect_format)


def test_mobile_site_row_to_mobilesite():
    assert mobile_site_row_to_mobilesite(
        ["20801", "12345", "6789", "1", "0", "0"]
    ) == MobileSite(
        provider="20801",
        lambert93=(12345, 6789),
        has_2g=True,
        has_3g=False,
        has_4g=False,
    )


def test_mobile_site_gps_row_to_mobilesite():
    assert mobile_site_gps_row_to_mobilesite(
        ["20801", "123.45", "678.9", "True", "False", "False"]
    ) == MobileSiteGPS(
        provider="20801",
        gps=(123.45, 678.9),
        has_2g=True,
        has_3g=False,
        has_4g=False,
    )


def test_read_french_mnc():
    # TODO: Do not hardcode this
    french_mnc = read_mnc("french_mnc.csv")
    assert len(french_mnc) == 46
    assert french_mnc[-1] == BrandMobileCodes(
        mcc=208,
        mnc=98,
        brand="Air France",
    )


@pytest.fixture()
def mobile_sites() -> list[MobileSite]:
    return read_mobile_site("site_mobiles.csv")


@pytest.fixture()
def french_mnc() -> list[BrandMobileCodes]:
    return read_mnc("french_mnc.csv")


@pytest.fixture()
def provider_resolver(
    mobile_sites: list[MobileSite],
    french_mnc: list[BrandMobileCodes],
) -> ProviderResolver:
    return ProviderResolver(
        mobile_sites=mobile_sites,
        brand_mobile_codes=french_mnc,
    )


@pytest.mark.parametrize(
    "provider_id,brand",
    [("20898", "Air France"), ("20801", "Orange"), ("20809", "SFR")],
)
def test_provider_resolver_with_known_id(
    provider_resolver: ProviderResolver,
    provider_id: str,
    brand: str,
):
    assert provider_resolver.resolve(provider_id) == brand


@pytest.mark.parametrize(
    "provider_id",
    ["20847", "2"],
)
def test_provider_resolver_with_unknown_id(
    provider_resolver: ProviderResolver,
    provider_id: str,
):
    with pytest.raises(UnknownProvider) as ex:
        provider_resolver.resolve(provider_id)
    assert provider_id in str(ex.value)


def test_convert_lambert93_to_gps():
    assert convert_lanbert93_to_gps(
        MobileSite(
            provider="20801",
            lambert93=(1240585, 6154019),
            has_2g=True,
            has_3g=True,
            has_4g=True,
        )
    ) == MobileSiteGPS(
        provider="20801",
        gps=(pytest.approx(9.5503891), pytest.approx(42.2843603)),
        has_2g=True,
        has_3g=True,
        has_4g=True,
    )
