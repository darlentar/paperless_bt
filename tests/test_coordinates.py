import pytest
from paperless_bt.coordinates import lamber93_to_gps


def test_lamber93_to_gps():
    assert lamber93_to_gps(102980, 6847973) == (
        pytest.approx(-5.0888561),
        pytest.approx(48.4565745),
    )
