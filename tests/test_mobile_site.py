from paperless_bt.mobile_site import MobileSite, read_mobile_site


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
