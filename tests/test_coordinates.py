import math

import pytest
from paperless_bt.coordinates import (
    EARTH_RADIUS,
    compute_haversine,
    lamber93_to_gps,
    nearest_from,
)

COORDINATES_8_RUE_LA_FAYETTE = (2.334332, 48.873258)
COORDINATES_12_RUE_HALEVY = (2.333123, 48.872321)
COORDINATES_10_PLACE_OPERA = (2.331972, 48.871423)
COORDINATES_28_BOULEVARD_CAPUCINES = (2.328364, 48.870152)


def test_lamber93_to_gps():
    assert lamber93_to_gps(102980, 6847973) == (
        pytest.approx(-5.0888561),
        pytest.approx(48.4565745),
    )


@pytest.mark.parametrize(
    "coordinates1, coordinates2, expected",
    [
        ((0, 0), (0, 0), 0),
        ((0, 0), (90, 0), pytest.approx(math.pi / 2.0 * EARTH_RADIUS)),
        ((0, 0), (-90, 23.12), pytest.approx(math.pi / 2.0 * EARTH_RADIUS)),
        ((0, 0), (-45, 0), pytest.approx(math.pi / 4.0 * EARTH_RADIUS)),
    ],
)
def test_haversine_formulat(coordinates1, coordinates2, expected):
    assert (
        compute_haversine(
            coordinates1[0],
            coordinates2[0],
            coordinates1[1],
            coordinates2[1],
        )
        == expected
    )


def test_nearest_from():
    assert (
        nearest_from(
            COORDINATES_28_BOULEVARD_CAPUCINES,
            iter(
                (
                    COORDINATES_12_RUE_HALEVY,
                    COORDINATES_8_RUE_LA_FAYETTE,
                    COORDINATES_10_PLACE_OPERA,
                )
            ),
            lambda k: (k[0], k[1]),
        )
        == COORDINATES_10_PLACE_OPERA
    )
