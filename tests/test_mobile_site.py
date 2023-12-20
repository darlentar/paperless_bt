import pytest
from paperless_bt.mobile_site import (
    BrandMobileCodes,
    MobileSite,
    ProviderResolver,
    UnknownProvider,
    read_mnc,
    read_mobile_site,
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
